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
    "route"
]

HYBRID_KEYWORDS = [
    "plan",
    "itinerary",
    "visit",
    "trip",
    "near",
    "around",
    "best places"
]


class QueryRouter:

    def get_route(self, query):

        query = query.lower()

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