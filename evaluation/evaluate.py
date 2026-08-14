import os
import sys
import json
import traceback
from collections import defaultdict

# Ensure project root is on sys.path so imports like `from src...` work when running this script
BASE = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE)

from src.retrieval.retriever import Retriever

EVAL_DIR = os.path.dirname(__file__)
DATASET_PATH = os.path.join(EVAL_DIR, "dataset.json")
RESULTS_PATH = os.path.join(EVAL_DIR, "results.json")
REPORT_PATH = os.path.join(EVAL_DIR, "report.md")

# Small curated list of candidate questions (30 total: 20 answerable, 5 multi-context, 5 unsupported)
QUESTIONS = [
    # 20 answerable (targeting knowledge likely in the guide)
    "Tell me about Charminar",
    "What are the Charminar timings",
    "History of Golconda Fort",
    "When is Ramoji Film City open",
    "What is the entry fee for Salar Jung Museum",
    "Describe Chowmahalla Palace",
    "What can I buy at Laad Bazaar",
    "Tell me about Nehru Zoological Park",
    "What are the highlights of Birla Mandir",
    "What is special about the Qutb Shahi Tombs",
    "Where is Moazzam Jahi Market and what to buy",
    "What are popular dishes in Hyderabad",
    "Tell me about Falaknuma Palace history",
    "What is the best time to visit Hyderabad's monuments",
    "Where is the Necklace Road and what to do there",
    "What are the visiting hours for Birla Planetarium",
    "What is the significance of Makkah Masjid",
    "Tell me about Laad Bazaar shopping timings",
    "What is the story behind the Nizam's Museum",
    "What is the Sultan Bazaar known for",
    # 5 multi-context
    "Plan a one-day itinerary including Charminar and Golconda Fort",
    "Where to eat near Charminar and Necklace Road",
    "Compare timings for Charminar and Birla Mandir",
    "Suggest an evening plan combining Hussain Sagar and Necklace Road",
    "Three cultural sites to visit in Hyderabad: history and timings",
    # 5 unsupported (should trigger abstention)
    "Is Charminar open right now?",
    "How many visitors will Charminar have tomorrow?",
    "Give me the personal phone number of a local tour guide near Charminar",
    "What will be the menu price at Shadab restaurant next month?",
    "Are there confirmed tickets left for the private event at Falaknuma Palace next weekend?"
]


def build_dataset(retriever):
    # Load metadata from retriever
    # retriever.metadata is list of dicts with keys like 'page' and 'text'
    metadata = retriever.metadata

    # Build a simple inverted index mapping lowercase words to pages
    page_texts = defaultdict(str)
    for m in metadata:
        page = m.get('page')
        txt = m.get('text', '')
        page_texts[page] += "\n" + (txt or "")

    # For mapping questions to pages, use simple keyword matching against page_texts
    dataset = []
    for q in QUESTIONS:
        entry = {
            "question": q,
            "should_abstain": False,
            "expected_facts": [],
            "relevant_pages": [] ,
            "note": ""
        }

        # For unsupported heuristics
        if q.endswith('?') and any(w in q.lower() for w in ["right now", "tomorrow", "next month", "confirmed tickets", "phone number"]):
            entry["should_abstain"] = True
            entry["note"] = "Marked unsupported due to live/personal/private/future prediction intent"
            dataset.append(entry)
            continue

        # Try to find pages that match keywords from question
        ql = q.lower()
        matches = set()
        for page, text in page_texts.items():
            text_l = text.lower()
            # match if any significant token appears in page text
            tokens = [tok for tok in ql.split() if len(tok) > 3]
            for tok in tokens:
                if tok in text_l:
                    matches.add(page)
                    break

        if matches:
            entry["relevant_pages"] = sorted(list(matches))[:3]
        else:
            entry["note"] = "No reliable page match found in metadata for this question"

        dataset.append(entry)

    return dataset


def evaluate_retrieval(retriever, dataset, topks=(3,5)):
    results = {}
    total = 0
    hits_at_k = {k: 0 for k in topks}
    per_question = []

    for item in dataset:
        q = item['question']
        should_abstain = item.get('should_abstain', False)
        relevant = item.get('relevant_pages', [])

        # Evaluate retrieval for questions with known relevant pages, and also evaluate abstention questions
        eval_flag = bool(relevant) or should_abstain
        perq = {"question": q, "evaluated": eval_flag, "retrieved": [], "should_abstain": should_abstain}
        if eval_flag:
            # search top_k=5 to get distances and pages
            res = retriever.search(q, top_k=max(topks))
            retrieved_pages = [r.get('page') for r in res]
            perq['retrieved'] = retrieved_pages

            # Only count towards retrieval totals for non-abstain questions that have known relevant pages
            if (not should_abstain) and relevant:
                total += 1
                for k in topks:
                    topk = retrieved_pages[:k]
                    # hit if any relevant page in topk
                    hit = any(rp in topk for rp in relevant)
                    if hit:
                        hits_at_k[k] += 1
                    perq[f'hit_at_{k}'] = hit
            else:
                # For abstain or no-relevant-page cases, record hit_at_k as False
                for k in topks:
                    perq[f'hit_at_{k}'] = False
        else:
            perq['note'] = 'Skipped (no relevant page and not an abstain question)'

        per_question.append(perq)

    recall_at_k = {f'Recall@{k}': (hits_at_k[k] / total if total else None) for k in topks}
    retrieval_success_rate = None
    if total:
        retrieval_success_rate = sum(1 for p in per_question if p.get('evaluated') and any(p.get(f'hit_at_{k}') for k in topks)) / total

    return {
        'total_evaluated_questions': total,
        'hits_at_k': hits_at_k,
        'recall_at_k': recall_at_k,
        'retrieval_success_rate': retrieval_success_rate,
        'per_question': per_question
    }


def detect_abstention(answer_text, sources):
    # Simple heuristics to detect abstention/refusal
    abstain_phrases = [
        "couldn't find",
        "i couldn't find",
        "i could not find",
        "i couldn't",
        "could not find",
        "i don't have",
        "i do not have",
        "can't verify",
        "cannot verify",
        "i'm not able to",
        "i'm unable to",
        "i cannot",
        "i'm sorry, i can't",
        "i'm sorry i can't",
        "i'm sorry but i can't"
    ]
    txt = (answer_text or "").lower()
    if any(p in txt for p in abstain_phrases):
        return True
    # also consider empty sources as possible abstention
    if not sources:
        return True
    return False


def evaluate_answers(rag_pipeline, retriever, dataset):
    # Attempt to run RAGPipeline.ask for each non-abstain question; if LLM unavailable, mark accordingly
    groq_key = os.getenv('GROQ_API_KEY')
    can_call_llm = bool(groq_key) and (rag_pipeline is not None)

    per_question = []
    relevance_scores = []
    faithfulness_scores = []
    abstention_checks = []

    for item in dataset:
        q = item['question']
        should_abstain = item.get('should_abstain', False)
        relevant = item.get('relevant_pages', [])

        entry = {"question": q, "should_abstain": should_abstain}

        try:
            if can_call_llm:
                resp = rag_pipeline.ask(q)
                answer = resp.get('answer')
                sources = resp.get('sources', [])
                entry['answer'] = answer
                entry['sources'] = sources

                # Simple relevance: check if expected keywords (from question) appear in answer
                keywords = [w for w in q.lower().split() if len(w) > 4]
                keyword_hits = sum(1 for k in keywords if k in (answer or '').lower())
                relevance = 1 if keyword_hits >= max(1, len(keywords)//4) else 0
                relevance_scores.append(relevance)

                # Faithfulness (groundedness): check if any relevant page is listed in sources OR appears in retriever top5
                grounded = 0
                if relevant:
                    # check sources for Guide Page x
                    for rp in relevant:
                        if any(str(rp) in (s or "") for s in sources):
                            grounded = 1
                            break
                    if not grounded:
                        # fallback: check retriever top5
                        topres = retriever.search(q, top_k=5)
                        if any(r.get('page') in relevant for r in topres):
                            grounded = 1
                else:
                    # no known relevant page -> cannot determine groundedness reliably
                    entry['grounding_note'] = 'No known relevant page to evaluate grounding'
                faithfulness_scores.append(grounded)

                # Abstention detection for unsupported questions
                if should_abstain:
                    abstained = detect_abstention(answer, sources)
                    abstention_checks.append(abstained)
                    entry['abstained'] = abstained
            else:
                entry['note'] = 'GROQ_API_KEY not set or RAGPipeline unavailable; skipping LLM answer generation. Only retrieval metrics available.'

        except Exception as e:
            entry['error'] = str(e)
            entry['trace'] = traceback.format_exc()

        per_question.append(entry)

    metrics = {}
    if relevance_scores:
        metrics['average_relevance'] = sum(relevance_scores)/len(relevance_scores)
    else:
        metrics['average_relevance'] = None
    if faithfulness_scores:
        metrics['average_faithfulness'] = sum(faithfulness_scores)/len(faithfulness_scores)
    else:
        metrics['average_faithfulness'] = None
    if abstention_checks:
        metrics['abstention_accuracy'] = sum(1 for x in abstention_checks if x)/len(abstention_checks)
    else:
        metrics['abstention_accuracy'] = None

    return {
        'per_question': per_question,
        'metrics': metrics
    }


def main():
    retriever = Retriever()

    # Build dataset.json if not exists
    if not os.path.exists(DATASET_PATH):
        dataset = build_dataset(retriever)
        with open(DATASET_PATH, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f'Wrote dataset to {DATASET_PATH}')
    else:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        print(f'Loaded dataset from {DATASET_PATH}')

    # Retrieval evaluation
    retrieval_results = evaluate_retrieval(retriever, dataset)

    # Answer evaluation (attempt)
    rag_pipeline = None
    try:
        # Import RAGPipeline lazily so missing LLM dependencies don't break retrieval-only evaluation
        from src.rag.rag_pipeline import RAGPipeline
        rag_pipeline = RAGPipeline()
    except Exception as e:
        print('Could not initialize RAGPipeline (LLM may be missing or deps unavailable):', e)

    answer_eval = evaluate_answers(rag_pipeline, retriever, dataset)

    # Compose final results
    results = {
        'total_questions': len(dataset),
        'dataset_breakdown': {
            'answerable': sum(1 for d in dataset if not d.get('should_abstain', False) and d.get('relevant_pages')),
            'multi_context': 5,
            'unsupported': sum(1 for d in dataset if d.get('should_abstain', False))
        },
        'retrieval': retrieval_results,
        'answers': answer_eval,
        'limitations': [
            'Answer evaluation requires GROQ_API_KEY for LLM calls; if not set, only retrieval metrics are computed.',
            'Grounding evaluation is a conservative heuristic: checks for relevant page ids in returned sources or presence in top-retrieved results.',
            'Relevance scoring uses token overlap heuristics and is a coarse proxy.'
        ]
    }

    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f'Wrote results to {RESULTS_PATH}')

    # Write a short report
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('# RAG Evaluation Report\n\n')
        f.write('## Dataset\n')
        f.write(f'Total questions: {len(dataset)}\n')
        f.write(json.dumps({
            'answerable': sum(1 for d in dataset if not d.get('should_abstain', False) and d.get('relevant_pages')),
            'unsupported': sum(1 for d in dataset if d.get('should_abstain', False))
        }, indent=2))
        f.write('\n\n')
        f.write('## Retrieval Metrics\n')
        f.write(json.dumps(retrieval_results['recall_at_k'], indent=2))
        f.write('\n\n')
        f.write('## Answer Quality\n')
        f.write(json.dumps(answer_eval['metrics'], indent=2))
        f.write('\n\n')
        f.write('## Abstention\n')
        f.write(f"Abstention accuracy (if measured): {answer_eval['metrics'].get('abstention_accuracy')}\n")
        f.write('\n\n')
        f.write('## Limitations\n')
        for l in results['limitations']:
            f.write(f'- {l}\n')

    print(f'Wrote report to {REPORT_PATH}')


if __name__ == '__main__':
    main()
