import os
from docx import Document
from ingest import run_ingest, DB

if os.path.exists(DB):
    os.remove(DB)

r = run_ingest()
print(f"Run 1: indexed {r['indexed']} files, {r['chunks']} chunks")

r = run_ingest()
print(f"Run 2: {r['skipped']} unchanged -> skipped")

# change exactly one file
d = Document("data/hr_guidelines.docx")
d.paragraphs[1].text += " (Updated for Run 3.)"
d.save("data/hr_guidelines.docx")

r = run_ingest()
print(f"Run 3 (1 changed): re-indexed {r['indexed']} file")
print(f"                   {r['skipped']} unchanged -> skipped")