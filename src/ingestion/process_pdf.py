from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_cleaner import clean_text
from src.ingestion.chunker import create_chunks

import pickle


PDF_PATH = "data/raw/MyCityMyHeritage-Hyderabad.pdf"


def process_pdf():

    print("Loading PDF...")

    pages = load_pdf(PDF_PATH)

    print("Cleaning Pages...")

    cleaned_pages = []

    for page in pages:

        cleaned_pages.append(
            {
                "page": page["page"],
                "text": clean_text(page["text"])
            }
        )

    print("Creating Chunks...")

    chunks = create_chunks(cleaned_pages)

    print(f"Total Chunks: {len(chunks)}")

    with open(
        "data/processed/chunks.pkl",
        "wb"
    ) as f:

        pickle.dump(chunks, f)

    print("Saved Successfully")


if __name__ == "__main__":
    process_pdf()