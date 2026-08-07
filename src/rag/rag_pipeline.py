import logging

from src.llm.langchain_llm import LangChainLLM
from src.retrieval.retriever import Retriever

from src.search.query_router import QueryRouter
from src.search.web_search import WebSearch


logger = logging.getLogger(__name__)


class RAGPipeline:

    def __init__(self):

        print("Initializing RAG Pipeline...")

        self.retriever = Retriever()
        self.llm = LangChainLLM()

        self.router = QueryRouter()
        self.web_search = WebSearch()

        print("RAG Pipeline Ready ✅")

    def _is_greeting(self, query):

        if not query:
            return False

        normalized = query.strip().lower()

        return any(
            phrase in normalized
            for phrase in [
                "hi",
                "hello",
                "hey",
                "good morning",
                "good afternoon",
                "good evening",
                "thanks",
                "thank you",
                "greetings"
            ]
        )

    def ask(self, query):

        if self._is_greeting(query):
            logger.debug("Greeting detected; skipping retrieval")
            return {
                "answer": "Hello! I can help you explore Hyderabad's attractions, food, and travel tips. Ask me about places, timings, food, or itineraries.",
                "sources": []
            }

        route = self.router.get_route(query)

        logger.debug("Route selected: %s", route)

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
            logger.debug(
                "Hybrid route: rag_docs=%s web_results=%s",
                len(docs),
                len(web_results)
            )

            web_context = "\n\n".join([
                f"""
Title: {result['title']}

Content:
{result['body']}
"""
                for result in web_results[:5]
            ])

            if not web_context:
                web_context = "No current web results were found."

            combined_context = f"""
GUIDE INFORMATION:

{rag_context}

WEB SEARCH RESULTS:

{web_context}
"""

            answer = self.llm.generate(
                context=combined_context,
                query=query,
                system_prompt="""
You are a Hyderabad Tourism Expert.

Use the guide context for history, culture, and general Hyderabad tourism facts.
Use web results only when they provide current or specific recommendations.

Rules:
- Combine both sources naturally.
- If web results are unavailable, say so clearly instead of guessing.
- Do not fabricate live facts such as current opening status, prices, or availability unless they are explicitly present in the provided results.
- Be detailed and helpful.
"""
            )

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
            logger.debug("Web route: web_results=%s", len(web_results))

            print("\nWEB RESULTS")
            print("=" * 80)

            for i, result in enumerate(web_results[:5]):

                print(f"\nResult {i+1}")
                print("Title:", result["title"])
                print("URL:", result["url"])
                print("-" * 50)
                print(result["body"])

            if not web_results:
                return {
                    "answer": "I couldn't find current web information for that query. I can still help with Hyderabad tourism suggestions from the guide context if you ask about attractions, history, or general travel advice.",
                    "sources": []
                }

            web_context = "\n\n".join([
                f"""
Title: {result['title']}

Content:
{result['body']}
"""
                for result in web_results[:5]
            ])

            answer = self.llm.generate(
                context=web_context,
                query=query,
                system_prompt="""
You are a Hyderabad Tourism Expert.

Use ONLY the provided web search results.

Rules:
- Extract factual information only.
- For general recommendations, offer suggestions conservatively and clearly label them as general advice when the results do not provide verified live details.
- Do not fabricate live facts such as current opening status, prices, or availability unless they are explicitly present in the provided results.
- If the results are limited or do not include enough detail, say so clearly.
- Keep answers concise.
"""
            )

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
            logger.debug("RAG route: docs=%s", len(docs))

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

            answer = self.llm.generate(
                context=context,
                query=query,
                system_prompt="""
You are an expert Hyderabad Tourism Guide.

Use ONLY the information provided in the guide context.

Rules:
- Answer naturally.
- Be concise but informative.
- Mention timings if available.
- Mention location if available.
- Mention special attractions if available.
- Do NOT make up information.
- If information is unavailable, clearly say so.
"""
            )

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