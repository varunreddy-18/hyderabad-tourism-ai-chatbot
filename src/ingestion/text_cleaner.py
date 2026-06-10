import re


def clean_text(text):
    """
    Clean extracted PDF text with careful handling of:
    - Page numbers and headers/footers
    - Image captions and photo credits
    - OCR artifacts and repeated whitespace
    - Broken sentences and fragments
    """
    
    # 1. Remove photo credits and attribution lines
    text = re.sub(r'(?:Photo|Image|Picture)\s+(?:by|credit|courtesy).*?(?=\n|$)', '', text, flags=re.IGNORECASE)
    
    # 2. Remove common header/footer patterns
    text = re.sub(r'FINAL\s+Hyderabad.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'My\s+City\s+My\s+Heritage.*', '', text, flags=re.IGNORECASE)
    
    # 3. Remove standalone page numbers (at end of line or beginning)
    # Matches: " 15" or "15 " but not "1500" or "Fort 12th"
    text = re.sub(r'(?:^|\s)(?<![\w\-])(?:\d{1,3})(?:\s|$)', ' ', text, flags=re.MULTILINE)
    
    # 4. Remove weird symbols and bullets
    text = re.sub(r'[•▪■◆►×†‡§¶]', '', text)
    
    # 5. Remove multiple whitespace (but preserve intentional newlines)
    text = re.sub(r'[ \t]+', ' ', text)  # Replace multiple spaces/tabs with single space
    text = re.sub(r'\n\s*\n+', '\n', text)  # Replace multiple empty lines with single newline
    
    # 6. Fix broken sentences - remove isolated punctuation at start of line
    text = re.sub(r'\n\s*[.,;:!?-]\s+', '\n', text)
    
    # 7. Remove lines that are just punctuation or numbers
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Skip empty lines, pure numbers, or pure punctuation
        if line and not re.match(r'^[\d\s.,;:\-]*$', line):
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # 8. Final normalization
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

    
	# Remove standalone page numbers
    text = re.sub(r'\s+\d+\s*$', '', text, flags=re.MULTILINE)
	

	# Remove isolated page numbers inside text
    text = re.sub(r'\b\d{1,3}\b', ' ', text)
	

	# Normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()
	

    return text.strip()