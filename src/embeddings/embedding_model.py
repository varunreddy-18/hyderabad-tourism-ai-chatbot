from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load model once at module level for efficiency
model = SentenceTransformer(MODEL_NAME)


def get_embedding(text):
    """Generate embedding for a single text."""
    return model.encode(text)


def get_embeddings(texts, show_progress_bar=True):
    """Generate embeddings for multiple texts."""
    return model.encode(texts, show_progress_bar=show_progress_bar, convert_to_numpy=True)
