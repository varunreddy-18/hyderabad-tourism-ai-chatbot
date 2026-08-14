# RAG Evaluation Report

## Dataset
Total: 30
Answerable: 20
Multi-context: 5
Unsupported: 5

## Retrieval Metrics
Recall@3: 0.65
Recall@5: 0.75
Retrieval success rate: 0.75

## Answer Quality
{
  "average_relevance": 0.7333333333333333,
  "average_faithfulness": 0.5333333333333333,
  "abstention_accuracy": 0.6
}

## Abstention
Abstention accuracy (if measured): 0.6


## Limitations
- Answer evaluation requires GROQ_API_KEY for LLM calls; if not set, only retrieval metrics are computed.
- Grounding evaluation is a conservative heuristic: checks for relevant page ids in returned sources or presence in top-retrieved results.
- Relevance scoring uses token overlap heuristics and is a coarse proxy.
