from src.search.web_search import WebSearch
from src.search.query_router import QueryRouter
import json

queries = [
    "Tell me about Charminar",
    "best restaurants in Hyderabad",
    "restaurants near Charminar",
    "Charminar timings today",
    "what is open today in Hyderabad"
]

searcher = WebSearch()
router = QueryRouter()

for q in queries:
    print('\n' + '='*100)
    print('QUERY:', q)
    route = router.get_route(q)
    print('ROUTE:', route.upper())
    try:
        out = searcher.search(q, max_results=6)
        ddgs_query = out.get('search_query') if isinstance(out, dict) else ''
        results = out.get('results') if isinstance(out, dict) else out

        print('SEARCH QUERY:', ddgs_query or q)
        print('WEB RESULT COUNT:', len(results))
        print('RESULT TITLES:', [r.get('title') for r in results[:5]])
        print('RESULT URLS:', [r.get('url') for r in results[:5]])

        # print a concise view of each top result
        for i, r in enumerate(results[:5], start=1):
            print('\n' + '-'*60)
            print(f'Result {i}')
            print('Title:', r.get('title'))
            print('URL:', r.get('url'))
            print('Evidence Type:', r.get('source_type'))
            body = (r.get('body') or '')
            print('BODY (first 400 chars):', body[:400])

    except Exception as e:
        print('ERROR while processing query:', e)
