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

        # Minimum top similarity (converted from L2 distance) to consider RAG results reliable.
        # This is intentionally conservative; similarity = 1/(1+distance). Typical good matches will be
        # noticeably higher than this. Tune if you have empirical distributions.
        self.MIN_RAG_SIMILARITY = 0.04

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

            # diagnostic logging for RAG results
            print("RAG doc count:", len(docs))
            for i, d in enumerate(docs, start=1):
                print(f"RAG {i}: page={d.get('page')} rank={d.get('rank')} dist={d.get('distance'):.4f} sim={d.get('similarity'):.4f}")

            # Determine if RAG retrieval is strong enough to include
            include_rag = False
            if docs and docs[0].get('similarity', 0) >= self.MIN_RAG_SIMILARITY:
                include_rag = True

            rag_context = "\n\n".join([d["text"] for d in docs]) if include_rag else ""

            web_out = self.web_search.search(query)
            web_results = web_out.get('results', []) if isinstance(web_out, dict) else web_out
            ddgs_query = web_out.get('search_query', '') if isinstance(web_out, dict) else ''

            # Diagnostic logging required by the fix
            print("SEARCH QUERY:", ddgs_query or query)
            print("WEB RESULT COUNT:", len(web_results))
            print("RESULT TITLES:", [r.get('title') for r in web_results[:5]])
            print("RESULT URLS:", [r.get('url') for r in web_results[:5]])

            # Build web context with explicit evidence type labels (snippet vs page) so LLM doesn't treat snippets as verified facts
            web_context_pieces = []
            for result in web_results[:5]:
                web_context_pieces.append(f"""
Title: {result.get('title')}
URL: {result.get('url')}
Evidence Type: {result.get('source_type', 'snippet')}

Content:
{result.get('body')}
""")

            web_context = "\n\n".join(web_context_pieces)

            # If RAG is weak but web results exist, rely primarily on web context
            if not include_rag and web_results:
                combined_context = f"""
WEB-FIRST ANSWER (Guide had no strong match):

WEB SEARCH RESULTS:

{web_context}
"""
            else:
                combined_context = f"""
GUIDE INFORMATION:

{rag_context}

WEB SEARCH RESULTS:

{web_context}
"""

            # Construct a conservative system prompt that instructs abstention when unsupported
            system_prompt = """
You are a Hyderabad Tourism Expert.

Use the guide context for history, culture, and general Hyderabad tourism facts.
Use web results only when they provide current or specific recommendations.

Rules:
- Combine both sources naturally.
- If the guide has no reliable information for the question, rely on the web results and state that guide context was not available.
- Do not fabricate live facts such as current opening status, prices, or availability unless they are explicitly present in the provided results.
- If neither source provides reliable information, clearly say you couldn't find grounded information and suggest trying a different query.
"""

            answer = self.llm.generate(
                context=combined_context,
                query=query,
                system_prompt=system_prompt
            )

            pages = sorted(
                list(
                    set(
                        doc["page"]
                        for doc in docs
                    )
                )
            ) if include_rag else []

            sources = []
            if include_rag:
                sources += [f"Guide Page {page}" for page in pages]
            sources += [result["url"] for result in web_results[:3] if result.get('url')]

            # If both sources empty, abstain
            if not sources:
                return {
                    "answer": "I couldn't find grounded information for that query from the guide or web results.",
                    "sources": []
                }

            return {
                "answer": answer,
                "sources": sources
            }

        # ==================================================
        # WEB MODE
        # ==================================================
        elif route == "web":

            web_out = self.web_search.search(query)
            web_results = web_out.get('results', []) if isinstance(web_out, dict) else web_out
            ddgs_query = web_out.get('search_query', '') if isinstance(web_out, dict) else ''

            print("\nWEB RESULTS")
            print("=" * 80)

            # Diagnostic logging
            print("ROUTE:", route.upper())
            print("SEARCH QUERY:", ddgs_query or query)
            print("WEB RESULT COUNT:", len(web_results))
            print("RESULT TITLES:", [r.get('title') for r in web_results[:5]])
            print("RESULT URLS:", [r.get('url') for r in web_results[:5]])

            for i, result in enumerate(web_results[:5]):

                print(f"\nResult {i+1}")
                print("Title:", result.get("title"))
                print("URL:", result.get("url"))
                print("Evidence Type:", result.get("source_type"))
                print("-" * 50)
                print((result.get("body") or "")[:400])

            if not web_results:
                return {
                    "answer": "I couldn't find current web information for that query. I can still help with Hyderabad tourism suggestions from the guide if you ask about attractions, history, or general travel advice.",
                    "sources": []
                }

            web_context_pieces = []
            for result in web_results[:5]:
                web_context_pieces.append(f"""
Title: {result.get('title')}
URL: {result.get('url')}
Evidence Type: {result.get('source_type', 'snippet')}

Content:
{result.get('body')}
""")

            web_context = "\n\n".join(web_context_pieces)

            # If the query is a recommendation-type question, instruct the LLM explicitly to extract names
            reco_hint = ""
            if any(k in query.lower() for k in ["restaurant", "restaurants", "best", "top", "recommend"]):
                reco_hint = "\n- For recommendation queries (restaurants/hotels), extract explicit establishment names from the results. If no specific names are present, say that reliable specific recommendations were not found."

            prompt = f"""
You are a Hyderabad Tourism Expert.

Use ONLY the provided web search results.

Rules:
- Extract factual information only.
- For general recommendations, offer suggestions conservatively and clearly label them as general advice when the results do not provide verified live details.{reco_hint}
- Do not fabricate live facts such as current opening status, prices, or availability unless they are explicitly present in the provided results.
- If the results are limited or do not include enough detail, say so clearly.
- Keep answers concise.
"""

            answer = self.llm.generate(
                context=web_context,
                query=query,
                system_prompt=prompt
            )

            return {
                "answer": answer,
                "sources": [
                    result.get("url")
                    for result in web_results[:3]
                    if result.get('url')
                ]
            }

        # ==================================================
        # RAG MODE
        # ==================================================
        else:

            docs = self.retriever.search(query, top_k=10)

            print("RAG doc count:", len(docs))
            for i, d in enumerate(docs, start=1):
                print(f"RAG {i}: page={d.get('page')} rank={d.get('rank')} dist={d.get('distance'):.4f} sim={d.get('similarity'):.4f}")

            # Simple keyword re-ranking filter retained but with safety: do not remove all
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

            # Decide if retrieved docs are reliable enough
            top_sim = docs[0].get('similarity', 0) if docs else 0
            print(f"Top RAG similarity={top_sim:.4f} (threshold={self.MIN_RAG_SIMILARITY})")

            if top_sim < self.MIN_RAG_SIMILARITY:
                # Abstain instead of passing weak/unrelated context
                return {
                    "answer": "I couldn't find grounded information in the guide for that question. You can try asking about general attractions, or try web mode for current info.",
                    "sources": []
                }

            print("\n" + "=" * 80)
            print("RETRIEVED DOCUMENTS")
            print("=" * 80)

            for i, doc in enumerate(docs):
                print(f"\nDocument {i+1}")
                print(f"Page: {doc['page']}")
                print("-" * 50)
                print(doc["text"][:400])

            context = "\n\n".join([doc["text"] for doc in docs])

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

            pages = sorted(list(set(doc["page"] for doc in docs)))

            return {
                "answer": answer,
                "sources": [f"Guide Page {page}" for page in pages]
            }