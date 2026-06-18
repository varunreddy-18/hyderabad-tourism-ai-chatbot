from src.search.query_router import QueryRouter

router = QueryRouter()

print("Test 1:")
print(router.should_use_web(
    "Tell me about Charminar"
))

print("\nTest 2:")
print(router.should_use_web(
    "Charminar timings today"
))

print("\nTest 3:")
print(router.should_use_web(
    "Best restaurants near Charminar"
))