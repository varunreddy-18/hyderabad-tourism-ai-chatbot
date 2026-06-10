from src.retrieval.retriever import Retriever
from src.llm.groq_llm import GroqLLM


class RAGPipeline:

    def __init__(self):
        print("Initializing RAG Pipeline...")

        self.retriever = Retriever()
        self.llm = GroqLLM()

        print("RAG Pipeline Ready ✅")

    def ask(self, query):

        # Retrieve more chunks
        docs = self.retriever.search(query, top_k=10)

        # Simple keyword filtering
        query_words = query.lower().split()

        filtered_docs = []

        for doc in docs:
            text = doc["text"].lower()

            score = 0

            for word in query_words:
                if word in text:
                    score += 1

            if score > 0:
                filtered_docs.append((score, doc))

        if filtered_docs:
            filtered_docs.sort(reverse=True, key=lambda x: x[0])
            docs = [item[1] for item in filtered_docs[:5]]
        else:
            docs = docs[:5]

        print("\n" + "=" * 80)
        print("RETRIEVED DOCUMENTS")
        print("=" * 80)

        for i, doc in enumerate(docs):
            print(f"\nDocument {i+1}")
            print(f"Page: {doc['page']}")
            print("-" * 50)
            print(doc["text"][:400])

        # Build context
        context = "\n\n".join(
            [doc["text"] for doc in docs]
        )

        prompt = f"""
You are an expert Hyderabad Tourism Guide.

Use ONLY the information provided in the context.

Rules:
- Answer naturally.
- Be concise but informative.
- Mention timings if available.
- Mention location if available.
- Mention special attractions if available.
- Do NOT make up information.
- If information is unavailable, say:
  "I could not find that information in the guide."

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

        answer = self.llm.generate(prompt)

        # Sources
        pages = sorted(
            list(
                set(
                    doc["page"]
                    for doc in docs
                )
            )
        )

        # Return dict with separated answer and sources (sources hidden in UI)
        return {
            "answer": answer,
            "sources": [f"Page {page}" for page in pages]
        }