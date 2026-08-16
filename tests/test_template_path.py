import sys, os, types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# stub heavy modules
sys.modules['src.llm.langchain_llm'] = types.ModuleType('src.llm.langchain_llm')
sys.modules['src.retrieval.retriever'] = types.ModuleType('src.retrieval.retriever')
sys.modules['src.search.query_router'] = types.ModuleType('src.search.query_router')
sys.modules['src.search.web_search'] = types.ModuleType('src.search.web_search')
setattr(sys.modules['src.llm.langchain_llm'], 'LangChainLLM', type('LangChainLLM', (), {'generate': lambda self, context, query, system_prompt=None: '[stub]'}))
setattr(sys.modules['src.retrieval.retriever'], 'Retriever', type('Retriever', (), {'search': lambda self, q, top_k=5: []}))
setattr(sys.modules['src.search.query_router'], 'QueryRouter', type('QueryRouter', (), {'get_route': lambda self, q: 'rag'}))
setattr(sys.modules['src.search.web_search'], 'WebSearch', type('WebSearch', (), {'search': lambda self, q: []}))
from app import app
print('template_folder=', app.template_folder)
print('jinja_loader searchpath=', getattr(app.jinja_loader, 'searchpath', None))
