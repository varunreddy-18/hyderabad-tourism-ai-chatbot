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

# Keywords that indicate a blended answer is useful (guide + web)
HYBRID_KEYWORDS = [
    "plan",
    "itinerary",
    "visit",
    "trip",
    "near",
    "around",
    "best places",
    "nearby",
    "close to"
]

# Recommendation-intent keywords — often we want web evidence for these
RECOMMENDATION_KEYWORDS = [
    "best",
    "top",
    "recommend",
    "recommendation",
    "recommended",
    "popular",
    "must try",
    "must-try",
    "where to eat",
    "suggest",
    "suggestion"
]

GREETINGS = re.compile(
    r"\b(hi|hello|hey|good morning|good afternoon|good evening|thanks|thank you|greetings)\b"
)


class QueryRouter:

    def get_route(self, query):

        # normalize and guard
        q = (query or "").strip().lower()

        if not q:
            return "rag"

        if self._is_greeting(q):
            return "rag"

        has_web = any(keyword in q for keyword in WEB_KEYWORDS)
        has_hybrid = any(keyword in q for keyword in HYBRID_KEYWORDS)
        has_reco = any(keyword in q for keyword in RECOMMENDATION_KEYWORDS)

        # If user asks for recommendations (best/top/recommend) about restaurants/food,
        # prefer WEB so that we gather current web evidence and explicit recommendations.
        if has_reco and ("restaurant" in q or "food" in q or "eat" in q):
            return "web"

        # If user asks for location-scoped queries like "near", "nearby", or mentions landmarks,
        # hybrid mode (guide + web) is useful.
        if has_hybrid and ("restaurant" in q or "hotel" in q or "near" in q or "nearby" in q):
            return "hybrid"

        # If query contains clearly temporal or real-time indicators, route to web.
        if any(t in q for t in ["today", "current", "open now", "timings", "latest", "open", "now"]):
            return "web"

        # If there are other web keywords present, treat as web-specific
        if has_web:
            return "web"

        # fallback to rag (guide-only)
        return "rag"

    def _is_greeting(self, query):
        return bool(GREETINGS.search(query))
