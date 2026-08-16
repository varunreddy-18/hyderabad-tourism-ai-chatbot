import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Stub heavy modules before importing app
import types
sys.modules['src.llm.langchain_llm'] = types.ModuleType('src.llm.langchain_llm')
sys.modules['src.retrieval.retriever'] = types.ModuleType('src.retrieval.retriever')
sys.modules['src.search.query_router'] = types.ModuleType('src.search.query_router')
sys.modules['src.search.web_search'] = types.ModuleType('src.search.web_search')
# Provide minimal classes used by RAGPipeline
setattr(sys.modules['src.llm.langchain_llm'], 'LangChainLLM', type('LangChainLLM', (), {'generate': lambda self, context, query, system_prompt=None: '[stub]'}))
setattr(sys.modules['src.retrieval.retriever'], 'Retriever', type('Retriever', (), {'search': lambda self, q, top_k=5: [{'page':1,'rank':1,'distance':0.1,'similarity':0.5,'text':'dummy'}]}))
setattr(sys.modules['src.search.query_router'], 'QueryRouter', type('QueryRouter', (), {'get_route': lambda self, q: 'rag'}))
setattr(sys.modules['src.search.web_search'], 'WebSearch', type('WebSearch', (), {'search': lambda self, q: []}))

from app import app

sample_md = '''## Introduction to Hyderabad

Hyderabad is a city known for its history, culture, food, and architecture.

### Places to Visit

- **Charminar**
- **Golconda Fort**
- **Hussain Sagar Lake**
- **Necklace Road**

### General Advice

1. Explore the Old City.
2. Try Hyderabad Biryani.
3. Visit major heritage attractions.
'''

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['chat_history'] = [{'user':'Test','assistant': sample_md, 'sources': []}]
    resp = client.get('/')
    text = resp.get_data(as_text=True)
    # Save to file for inspection
    with open('tests/output.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('WROTE tests/output.html')
    # Check that the script tag contains the markdown (unescaped) and that assistant-html div exists
    has_script = '<script type="text/markdown" class="assistant-md">' in text
    print('has_script=', has_script)
    print('assistant-html exists:', '<div class="assistant-html"></div>' in text)
