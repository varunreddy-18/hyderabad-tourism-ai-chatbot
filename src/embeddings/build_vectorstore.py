import os
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


CHUNKS_PATH = "data/processed/chunks.pkl"

VECTORSTORE_DIR = "data/vectorstore"
INDEX_PATH = os.path.join(VECTORSTORE_DIR, "faiss_index")
METADATA_PATH = os.path.join(VECTORSTORE_DIR, "metadata.pkl")


def build_vectorstore():
    """
    Build FAISS vector store from processed chunks.
    Generates embeddings and creates searchable index.
    """
    print("Loading chunks...")

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    print(f"Loaded {len(chunks)} chunks")

    # Extract text only for embeddings
    texts = [chunk["text"] for chunk in chunks]

    print("Loading embedding model...")

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    embeddings = embeddings.astype("float32")

    print(f"Embedding dimension: {embeddings.shape[1]}")

    print("Creating FAISS index...")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    os.makedirs(VECTORSTORE_DIR, exist_ok=True)

    print("Saving FAISS index...")

    faiss.write_index(index, INDEX_PATH)

    print("Saving metadata...")

    metadata = []

    for chunk in chunks:
        metadata.append(
            {
                "chunk_id": chunk["chunk_id"],
                "page": chunk["page"],
                "text": chunk["text"]
            }
        )

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print("\n✅ Vector Store Created Successfully")
    print(f"Total vectors: {index.ntotal}")


if __name__ == "__main__":
    build_vectorstore()
