# parser.py
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    with fitz.open(pdf_path) as doc:
        return "\n".join([page.get_text() for page in doc])

def save_text(text: str, save_path: str):
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)
