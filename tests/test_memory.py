import sys, os, types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Insert a lightweight stub for src.rag.rag_pipeline to avoid heavy LLM imports during tests
stub_mod = types.ModuleType('src.rag.rag_pipeline')
class StubRAG:
    def __init__(self):
        pass
    def ask(self, query, conversation_history=None):
        return {"answer": f"[initial stub for: {query}]", "sources": ["stub://source"]}
stub_mod.RAGPipeline = StubRAG
sys.modules['src.rag.rag_pipeline'] = stub_mod

from app import app, rag

# Monkeypatch rag.ask to capture conversation_history and return predictable output
captured = {"last_called_with": None}

def fake_ask(query, conversation_history=None):
    captured['last_called_with'] = {'query': query, 'conversation_history': conversation_history}
    return {"answer": f"[stub answer for: {query}]", "sources": ["stub://source"]}

rag.ask = fake_ask

with app.test_client() as client:
    # Test 1: Tell me about Golconda Fort, then follow-up
    r1 = client.post('/', data={'query': 'Tell me about Golconda Fort'}, follow_redirects=True)
    print('Test1 - first POST status:', r1.status_code)

    # After first post, session should have 1 exchange
    with client.session_transaction() as sess:
        h = sess.get('chat_history', [])
        print('Test1 - session chat_history after 1st:', h)

    r2 = client.post('/', data={'query': 'What can I see there?'}, follow_redirects=True)
    print('Test1 - second POST status:', r2.status_code)
    print('Test1 - rag.ask last call:', captured['last_called_with'])
    with client.session_transaction() as sess:
        h = sess.get('chat_history', [])
        print('Test1 - session chat_history after 2nd:', h)

    # Test 3: Suggest a place then "Suggest another one"
    r3 = client.post('/', data={'query': 'Suggest a place to visit in Hyderabad'}, follow_redirects=True)
    r4 = client.post('/', data={'query': 'Suggest another one'}, follow_redirects=True)
    print('Test3 - rag.ask last call after "Suggest another one":', captured['last_called_with'])
    with client.session_transaction() as sess:
        print('Test3 - session chat_history:', sess.get('chat_history'))

    # Test 4: Start fresh session (simulate by clearing session) and ask follow-up
    with client.session_transaction() as sess:
        sess.clear()
    r5 = client.post('/', data={'query': 'What can I see there?'}, follow_redirects=True)
    print('Test4 - fresh session POST status:', r5.status_code)
    print('Test4 - rag.ask last call:', captured['last_called_with'])
    with client.session_transaction() as sess:
        print('Test4 - session chat_history:', sess.get('chat_history'))
