import os, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from openpyxl import Workbook

random.seed(42)
os.makedirs("data", exist_ok=True)
WORDS = ("policy employee leave salary approval manager office travel expense laptop "
         "security review quarter report team access holiday benefit claim").split()

def para(n=70):
    return " ".join(random.choice(WORDS) for _ in range(n)).capitalize() + "."

def make_pdf(path, title, text_pages, scanned=False):
    c = canvas.Canvas(path, pagesize=A4)
    for i in range(1, text_pages + 1):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 800, f"{title} - Page {i}")
        c.setFont("Helvetica", 11)
        y = 770
        for line in simpleSplit(para(), "Helvetica", 11, 490):
            c.drawString(50, y, line)
            y -= 15
        c.showPage()
    if scanned:  # image-only page: no text layer, so OCR is needed
        img = Image.new("RGB", (1400, 500), "white")
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default(size=36)
        lines = ["SCANNED PAGE", "Invoice approval limit is 5000 dollars.",
                 "Manager sign off is required."]
        for k, t in enumerate(lines):
            d.text((40, 40 + k * 90), t, fill="black", font=font)
        img.save("data/_scan.png")
        c.drawImage("data/_scan.png", 40, 400, width=515, height=184)
        c.showPage()
    c.save()

make_pdf("data/policy_handbook.pdf", "Policy Handbook", 40)               # 40 chunks
make_pdf("data/finance_manual.pdf", "Finance Manual", 30, scanned=True)   # 31 chunks
os.remove("data/_scan.png")

# DOCX: 29 sections (heading + paragraph)                                 # 29 chunks
doc = Document()
for i in range(1, 30):
    doc.add_heading(f"Section {i}", level=1)
    doc.add_paragraph(para(60))
doc.save("data/hr_guidelines.docx")

# XLSX: 2 sheets x 25 rows                                                # 50 chunks
wb = Workbook()
ws1 = wb.active; ws1.title = "Employees"
ws1.append(["id", "name", "department", "salary_band"])
for i in range(1, 26):
    ws1.append([i, f"Employee {i}", random.choice(["HR", "IT", "Finance"]), f"B{random.randint(1,5)}"])
ws2 = wb.create_sheet("Policies")
ws2.append(["code", "title", "owner"])
for i in range(1, 26):
    ws2.append([f"POL-{i:03d}", f"Policy {i}", random.choice(["HR", "IT", "Finance"])])
wb.save("data/company_data.xlsx")

print("Sample files created in ./data  (40 + 31 + 29 + 50 = 150 expected chunks)")