from flask import Flask, render_template, request, session
from src.rag.rag_pipeline import RAGPipeline
import os

app = Flask(__name__, static_folder='app/static', static_url_path='/static')
# Use an environment-provided secret when available; fall back to a runtime key (not committed)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24)

print("Loading RAG Pipeline...")
rag = RAGPipeline()
print("RAG Ready!")


@app.route("/", methods=["GET", "POST"])
def home():

    # Load per-session chat history (kept as a list of exchanges: {user, assistant, sources})
    chat_history = session.get('chat_history', []) or []

    if request.method == "POST":

        query = request.form.get("query", "").strip()

        if query:

            # Build lightweight conversation history for RAG: last 5 exchanges (user+assistant pairs)
            conversation_history = []
            # chat_history contains exchange dicts; convert to role/content pairs
            for exch in chat_history[-5:]:
                conversation_history.append({"role": "user", "content": exch.get("user", "")})
                conversation_history.append({"role": "assistant", "content": exch.get("assistant", "")})

            try:
                # Pass conversation history as optional parameter; RAG will use it only for context
                result = rag.ask(query, conversation_history=conversation_history)

                print("Result Type:", type(result))
                print("Result:", result)

                # Handle string response
                if isinstance(result, str):
                    answer = result
                    sources = []

                # Handle dict response
                elif isinstance(result, dict):
                    answer = result.get("answer", "No answer found")
                    sources = result.get("sources", [])

                else:
                    answer = str(result)
                    sources = []

                # Append and trim to most recent 5 exchanges to avoid unbounded growth
                chat_history.append({
                    "user": query,
                    "assistant": answer,
                    "sources": sources
                })
                chat_history = chat_history[-5:]
                session['chat_history'] = chat_history

            except Exception as e:

                print("ERROR:", str(e))

                chat_history.append({
                    "user": query,
                    "assistant": f"Error: {str(e)}",
                    "sources": []
                })
                chat_history = chat_history[-5:]
                session['chat_history'] = chat_history

    return render_template(
        "index.html",
        chat_history=chat_history
    )


if __name__ == "__main__":
    app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=False
)