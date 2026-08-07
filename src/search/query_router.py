import re


WEB_KEYWORDS = [
    "today",
    "latest",
    "current",
    "weather",
    "restaurant",
    "restaurants",
    "cafe",
    "cafes",
    "food",
    "foods",
    "eat",
    "eating",
    "dish",
    "dishes",
    "street food",
    "hotel",
    "hotels",
    "nearby",
    "near me",
    "open now",
    "timings",
    "ticket",
    "entry fee",
    "event",
    "festival",
    "metro",
    "bus",
    "route",
    "recommend",
    "recommendation",
    "recommendations"
]

HYBRID_KEYWORDS = [
    "plan",
    "itinerary",
    "visit",
    "trip",
    "near",
    "around",
    "best places",
    "best",
    "suggest",
    "suggestion"
]

GREETINGS = re.compile(
    r"\b(hi|hello|hey|good morning|good afternoon|good evening|thanks|thank you|greetings)\b"
)


class QueryRouter:

    def get_route(self, query):

        query = (query or "").strip().lower()

        if not query:
            return "rag"

        if self._is_greeting(query):
            return "rag"

        web = any(
            keyword in query
            for keyword in WEB_KEYWORDS
        )

        hybrid = any(
            keyword in query
            for keyword in HYBRID_KEYWORDS
        )

        if web and hybrid:
            return "hybrid"

        elif web:
            return "web"

        else:
            return "rag"

    def _is_greeting(self, query):
        return bool(GREETINGS.search(query))