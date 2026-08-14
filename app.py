from flask import Flask, render_template, request
from src.rag.rag_pipeline import RAGPipeline

app = Flask(__name__, static_folder='app/static', static_url_path='/static')

print("Loading RAG Pipeline...")
rag = RAGPipeline()
print("RAG Ready!")

chat_history = []


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        query = request.form.get("query", "").strip()

        if query:

            try:
                result = rag.ask(query)

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

                chat_history.append({
                    "user": query,
                    "assistant": answer,
                    "sources": sources
                })

            except Exception as e:

                print("ERROR:", str(e))

                chat_history.append({
                    "user": query,
                    "assistant": f"Error: {str(e)}",
                    "sources": []
                })

    return render_template(
        "index.html",
        chat_history=chat_history
    )


if __name__ == "__main__":
    app.run(
    host="0.0.0.0",
    port=5000,
    debug=False
)