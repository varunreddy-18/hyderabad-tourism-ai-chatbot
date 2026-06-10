from src.rag.rag_pipeline import RAGPipeline

rag = RAGPipeline()

while True:

    query = input("\nAsk: ")

    if query.lower() == "exit":
        break

    result = rag.ask(query)

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print("-", source)