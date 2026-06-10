"""
Configuration settings for the RAG pipeline.
"""

# PDF Processing
PDF_PATH = "data/raw/MyCityMyHeritage-Hyderabad.pdf"
PAGES_TO_SKIP = 9  # Skip intro pages (0-8)

# Text Chunking
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Character overlap between chunks
MIN_CHUNK_LENGTH = 100  # Minimum characters to keep a chunk
MIN_WORDS_PER_CHUNK = 10  # Minimum words in a chunk

# Embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 output dimension

# Vector Store
VECTORSTORE_DIR = "data/vectorstore"
FAISS_INDEX_PATH = "data/vectorstore/faiss_index"
METADATA_PATH = "data/vectorstore/metadata.pkl"

# Retrieval
DEFAULT_TOP_K = 5  # Default number of results to retrieve
SIMILARITY_THRESHOLD = None  # Optional: filter by similarity

# Paths
DATA_DIR = "data"
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
CHUNKS_PATH = "data/processed/chunks.pkl"
