from src.retrieval.retriever import Retriever
from src.llm.groq_llm import GroqLLM

from src.search.query_router import QueryRouter
from src.search.web_search import WebSearch


class RAGPipeline:

    def __init__(self):

        print("Initializing RAG Pipeline...")

        self.retriever = Retriever()
        self.llm = GroqLLM()

        self.router = QueryRouter()
        self.web_search = WebSearch()

        print("RAG Pipeline Ready ✅")

    def ask(self, query):

        route = self.router.get_route(query)

        print("\n" + "=" * 80)
        print("ROUTE:", route.upper())
        print("=" * 80)

        # ==================================================
        # HYBRID MODE
        # ==================================================
        if route == "hybrid":

            print("\nHYBRID MODE ACTIVATED")

            docs = self.retriever.search(query, top_k=5)

            rag_context = "\n\n".join([
                doc["text"]
                for doc in docs
            ])

            web_results = self.web_search.search(query)

            web_context = "\n\n".join([
                f"""
Title: {result['title']}

Content:
{result['body']}
"""
                for result in web_results[:5]
            ])

            prompt = f"""
You are a Hyderabad Tourism Expert.

Use BOTH sources:

1. Hyderabad Tourism Guide
2. Web Search Results

GUIDE CONTEXT:

{rag_context}

WEB SEARCH RESULTS:

{web_context}

QUESTION:
{query}

Rules:
- Use guide information for history and culture.
- Use web results for current recommendations.
- Combine both naturally.
- Be detailed and helpful.
- Do not make up information.

ANSWER:
"""

            answer = self.llm.generate(prompt)

            pages = sorted(
                list(
                    set(
                        doc["page"]
                        for doc in docs
                    )
                )
            )

            return {
                "answer": answer,
                "sources": (
                    [f"Guide Page {page}" for page in pages]
                    +
                    [
                        result["url"]
                        for result in web_results[:3]
                    ]
                )
            }

        # ==================================================
        # WEB MODE
        # ==================================================
        elif route == "web":

            web_results = self.web_search.search(query)

            print("\nWEB RESULTS")
            print("=" * 80)

            for i, result in enumerate(web_results[:5]):

                print(f"\nResult {i+1}")
                print("Title:", result["title"])
                print("URL:", result["url"])
                print("-" * 50)
                print(result["body"])

            web_context = "\n\n".join([
                f"""
Title: {result['title']}

Content:
{result['body']}
"""
                for result in web_results[:5]
            ])

            prompt = f"""
You are a Hyderabad Tourism Expert.

Use ONLY the web search results below.

Rules:
- Extract factual information only.
- If multiple timings are found, mention both and state that sources differ.
- Answer directly.
- Keep answers concise.
- Include ticket prices if available.
- Include location if available.
- Do not make up information.

WEB SEARCH RESULTS:

{web_context}

QUESTION:
{query}

ANSWER:
"""

            answer = self.llm.generate(prompt)

            return {
                "answer": answer,
                "sources": [
                    result["url"]
                    for result in web_results[:3]
                ]
            }

        # ==================================================
        # RAG MODE
        # ==================================================
        else:

            docs = self.retriever.search(query, top_k=10)

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

                filtered_docs.sort(
                    reverse=True,
                    key=lambda x: x[0]
                )

                docs = [
                    item[1]
                    for item in filtered_docs[:5]
                ]

            else:
                docs = docs[:5]

            print("\n" + "=" * 80)
            print("RETRIEVED DOCUMENTS")
            print("=" * 80)

            for i, doc in enumerate(docs):

                print(f"\nDocument {i+1}")
                print(f"Page: {doc['page']}")
                print("-" * 50)

                print(
                    doc["text"][:400]
                )

            context = "\n\n".join([
                doc["text"]
                for doc in docs
            ])

            prompt = f"""
You are an expert Hyderabad Tourism Guide.

Use ONLY the information provided in the guide context.

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

            pages = sorted(
                list(
                    set(
                        doc["page"]
                        for doc in docs
                    )
                )
            )

            return {
                "answer": answer,
                "sources": [
                    f"Guide Page {page}"
                    for page in pages
                ]
            }