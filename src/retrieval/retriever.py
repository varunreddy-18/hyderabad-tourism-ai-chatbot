import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


INDEX_PATH = "data/vectorstore/faiss_index"
METADATA_PATH = "data/vectorstore/metadata.pkl"


class Retriever:
    """
    FAISS-based retriever for semantic search over document chunks.
    Uses L2 distance metric and pre-computed embeddings.
    """

    def __init__(self):
        print("Loading FAISS index...")
        self.index = faiss.read_index(INDEX_PATH)

        print("Loading metadata...")
        with open(METADATA_PATH, "rb") as f:
            self.metadata = pickle.load(f)

        print("Loading embedding model...")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        print(f"Retriever Ready ✅ ({len(self.metadata)} chunks indexed)")

    def search(self, query, top_k=5):
        """
        Search for relevant chunks using semantic similarity.

        Returns a list of result dicts that include:
          - chunk metadata (page, text, chunk_id)
          - distance: raw faiss L2 distance (lower is better)
          - similarity: converted similarity score in (0,1], computed as 1/(1+distance)
          - rank: 1-based rank

        This keeps the external interface but exposes distances/similarities for debugging.
        """
        # Generate query embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )
        query_embedding = query_embedding.astype("float32")

        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            result = self.metadata[idx].copy()
            dist = float(distances[0][i])
            # conservative similarity transform from L2 distance to 0..1 (higher is better)
            sim = 1.0 / (1.0 + dist) if dist is not None else 0.0
            result["distance"] = dist
            result["similarity"] = float(sim)
            result["rank"] = i + 1
            results.append(result)

        return results


if __name__ == "__main__":
    retriever = Retriever()

    print("\n" + "=" * 80)
    print("RETRIEVER TEST INTERFACE")
    print("=" * 80)

    test_queries = [
        "Golconda Fort history",
        "Charminar",
        "Nehru Zoological Park",
        "Moazzam Jahi Market",
        "Hyderabad food",
        "Museums in Hyderabad"
    ]

    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print("=" * 80)

        results = retriever.search(query, top_k=3)

        for result in results:
            print(f"\n[Rank {result['rank']}] Page {result['page']} | Distance: {result['distance']:.4f}")
            print("-" * 70)
            print(result["text"][:500])
            if len(result["text"]) > 500:
                print("...")
