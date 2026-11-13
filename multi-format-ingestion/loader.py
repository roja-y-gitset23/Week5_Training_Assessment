import os, io
import fitz                     # PyMuPDF
import pytesseract
from PIL import Image
from docx import Document
from openpyxl import load_workbook

pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")


def _ocr_page(page):
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img)


def load_pdf(path):
    items, src = [], os.path.basename(path)
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = " ".join(page.get_text().split())
            section = f"page {i}"
            if len(text) < 20:                       # no text layer -> scanned -> OCR fallback
                try:
                    text = " ".join(_ocr_page(page).split())
                    section = f"page {i} (OCR)"
                except Exception as e:
                    print(f"  [warn] OCR failed on {src} page {i}: {e}")
                    text = ""
            if text:
                items.append({"text": text, "source": src, "page_or_section": section})
    return items


def load_docx(path):
    items, src = [], os.path.basename(path)
    d = Document(path)
    title, buf = "Intro", []

    def flush():
        body = " ".join(buf).strip()
        if body:
            items.append({"text": f"{title}. {body}", "source": src, "page_or_section": title})

    for p in d.paragraphs:
        if p.style.name.startswith("Heading"):
            flush()
            title, buf = p.text.strip(), []
        elif p.text.strip():
            buf.append(p.text.strip())
    flush()
    return items


def load_xlsx(path):
    items, src = [], os.path.basename(path)
    wb = load_workbook(path, data_only=True, read_only=True)
    for ws in wb.worksheets:
        rows = ws.iter_rows(values_only=True)
        header = next(rows, None)
        if not header:
            continue
        for n, row in enumerate(rows, start=2):
            if all(v is None for v in row):
                continue
            text = " | ".join(f"{h}={v}" for h, v in zip(header, row))
            items.append({"text": text, "source": src, "page_or_section": f"{ws.title}!row{n}"})
    return items


def load_document(path):
    """Returns a list of {text, source, page_or_section} for pdf / docx / xlsx."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return load_pdf(path)
    if ext == ".docx":
        return load_docx(path)
    if ext == ".xlsx":
        return load_xlsx(path)
    raise ValueError(f"Unsupported file type: {ext}")