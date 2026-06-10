from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

from src.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


def sanitize_chunk(chunk):
    """
    Post-process chunks to ensure they're clean:
    - Remove leading/trailing punctuation
    - Ensure proper sentence boundaries
    - Remove fragment artifacts
    """
    chunk = chunk.strip()
    
    # Remove leading punctuation (but keep quotes)
    chunk = re.sub(r'^[.,;:!?\-\s]+', '', chunk).strip()
    
    # Remove trailing isolated punctuation that's not part of sentence
    # Keep proper endings like "." but remove stray ","
    chunk = re.sub(r'[,;:!?\-]\s*$', '.', chunk) if chunk else chunk
    if chunk.endswith('..'):
        chunk = chunk[:-1]
    
    return chunk


def create_chunks(pages):
    """
    Create chunks from cleaned pages with post-processing.
    Ensures chunks:
    - Have meaningful size (>100 chars)
    - Start and end at sentence boundaries
    - Don't contain fragments or artifacts
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []
    chunk_id = 0

    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]

        # Skip intro pages (usually 0-8)
        if page_num < 9:
            continue

        page_chunks = splitter.split_text(text)

        for chunk in page_chunks:
            chunk = sanitize_chunk(chunk)
            
            # Quality filter:
            # - Minimum length for meaningful content
            # - Not just whitespace or punctuation
            # - Must have actual words
            if len(chunk) < 100:
                continue
            
            # Skip chunks that are mostly numbers/punctuation
            word_count = len(re.findall(r'\b\w+\b', chunk))
            if word_count < 10:
                continue

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "page": page_num,
                    "text": chunk
                }
            )

            chunk_id += 1

    return chunks
