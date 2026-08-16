import sys, os, types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Stub out the LangChainLLM to capture system_prompt and avoid external deps
stub_mod = types.ModuleType('src.llm.langchain_llm')
_generate_calls = []
class LangChainLLM:
    def __init__(self):
        pass
    def generate(self, context, query, system_prompt=None):
        _generate_calls.append({
            'context': context,
            'query': query,
            'system_prompt': system_prompt
        })
        return "[stub answer]"
stub_mod.LangChainLLM = LangChainLLM
sys.modules['src.llm.langchain_llm'] = stub_mod

# Stub Retriever to avoid heavy ML libs
retr_mod = types.ModuleType('src.retrieval.retriever')
class Retriever:
    def __init__(self):
        pass
    def search(self, query, top_k=10):
        # Return at least one doc with high similarity to avoid abstain
        docs = []
        for i in range(min(5, top_k)):
            docs.append({
                'page': i+1,
                'rank': i+1,
                'distance': 0.1,
                'similarity': 0.5,
                'text': 'Dummy guide text about Hyderabad: attractions, timings, and suggestions.'
            })
        return docs
retr_mod.Retriever = Retriever
sys.modules['src.retrieval.retriever'] = retr_mod

# Stub QueryRouter always returning 'rag' to exercise RAG prompt
qr_mod = types.ModuleType('src.search.query_router')
class QueryRouter:
    def get_route(self, query):
        return 'rag'
qr_mod.QueryRouter = QueryRouter
sys.modules['src.search.query_router'] = qr_mod

# Stub WebSearch (not used in RAG)
ws_mod = types.ModuleType('src.search.web_search')
class WebSearch:
    def search(self, query):
        return []
ws_mod.WebSearch = WebSearch
sys.modules['src.search.web_search'] = ws_mod

from app import app

with app.test_client() as client:
    # Ensure no prior calls
    _generate_calls.clear()

    queries = [
        "I have 2 day and want to explore places in Hyderabad, can you help me in this",
        "I don't know anything about Hyderabad. I am new to this place. Suggest one",
        "plan one day in Hyderabad",
        "2-day plan of Hyderabad",
        "hello"
    ]

    results = []
    for q in queries:
        r = client.post('/', data={'query': q}, follow_redirects=True)
        results.append((q, r.status_code, len(_generate_calls)))

    print('Generate calls per query (cumulative):')
    for q, status, calls in results:
        print(q, '->', status, 'generate_calls=', calls)

    # Determine which queries triggered generate calls (non-greeting)
    # The last query 'hello' should NOT have added a generate call
    # Check that some system_prompts include formatting instruction
    formatting_present = any(
        call and ('Use bullet points' in (call['system_prompt'] or '') or 'Formatting:' in (call['system_prompt'] or ''))
        for call in _generate_calls
    )

    print('Formatting instruction present in system prompts?:', formatting_present)

    # Print last system prompt for inspection
    if _generate_calls:
        print('Last system prompt:\n', _generate_calls[-1]['system_prompt'][:800])
