import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# -------- CONFIG --------
os.environ["TESSDATA_PREFIX"] = r"C:\Users\ADMIN\scoop\apps\tesseract\current\tessdata"
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ADMIN\scoop\apps\tesseract\current\tesseract.exe"
POPPLER_PATH = r"C:\Users\ADMIN\scoop\apps\poppler\current\bin"

PDF_PATH = "../data/#3 SDN Technical.pdf"
OUTPUT_PATH = "../data/textbook.txt"

def extract_text_ocr(pdf_path):
    print("🔍 Converting PDF pages to images...")
    pages = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    full_text = ""
    total = len(pages)

    for i, page_img in enumerate(pages):
        print(f"  📄 OCR processing page {i+1}/{total}...")
        text = pytesseract.image_to_string(page_img, lang="eng")
        full_text += f"\n\n--- Page {i+1} ---\n{text}"

    return full_text.strip()

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF not found at {PDF_PATH}")
        exit()

    print(f"📚 Starting extraction from: {PDF_PATH}")
    text = extract_text_ocr(PDF_PATH)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"\n✅ Done! Saved to: {OUTPUT_PATH}")
    print(f"📊 Total words: {len(text.split())}")
    print(f"📄 Total pages processed: {text.count('--- Page')}")