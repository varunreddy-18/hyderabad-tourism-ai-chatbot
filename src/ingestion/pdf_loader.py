import fitz  # PyMuPDF
import re


def load_pdf(pdf_path):
    """
    Extract text from PDF with better handling of layout and structure.
    Uses 'text' mode for better line preservation.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Use get_text("text") for better line handling
        # This preserves line breaks better than plain get_text()
        text = page.get_text("text")
        
        pages.append(
            {
                "page": page_num,
                "text": text
            }
        )

    return pages