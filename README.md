# Week 5 Assessment: Enterprise RAG

Four tasks that build the data, search, security and evaluation layers of an enterprise RAG system.
Each task lives in its own folder with its own virtual environment and can be run on its own.

| # | Task | Folder | One-line summary |
|---|------|--------|------------------|
| 1 | Multi-Format Ingestion | `multi-format-ingestion/` | Ingest PDF (with OCR fallback), DOCX and Excel; skip unchanged files by hash; queue ingestion behind `POST /ingest` |
| 2 | Hybrid Search and Reranking | `hybrid-search/` | BM25 + vector search fused with Reciprocal Rank Fusion, then a cross-encoder reranker |
| 3 | Enterprise Data and Security | `enterprise-security/` | Safe read-only SQL tools, question routing, role-based access, drop-table proof, connector design |
| 4 | Evaluation and Client Report | `evaluation-client-report/` | Golden dataset, RAGAS for two configurations, experiment log, failure analysis, client summary |

## Repository layout

```
Week5_Assessment_Rag/
├── multi-format-ingestion/
│   ├── make_samples.py     creates sample PDFs (one scanned), DOCX and XLSX
│   ├── loader.py           load_document(path) for every file type
│   ├── ingest.py           chunking, metadata, hashing, incremental indexing
│   ├── api.py              FastAPI POST /ingest + GET /tasks/{id} with a background queue
│   └── run_demo.py         3-run demo (index, skip, re-index one file)
├── hybrid-search/
│   ├── data.py             30 policy chunks and candidate questions
│   ├── search.py           BM25, vector, RRF hybrid_search, cross-encoder reranker
│   └── evaluate.py         hit rate at top 3 for four methods
├── enterprise-security/
│   ├── setup_db.py         creates leave.db (the only writer)
│   ├── docs.py             chunks with allowed_roles (HR-only documents included)
│   ├── rag.py              role-filtered retrieval
│   ├── sql_tools.py        get_leave_balance, count_employees (read-only, parameterised)
│   ├── router.py           policy / data / mixed / blocked routing
│   ├── run_tests.py        runs every check and prints the evidence
│   ├── connector_sync.py   Google Drive sandbox connector with last_synced_at
│   └── CONNECTOR_DESIGN.md connector design and sync schedule
└── evaluation-client-report/
    ├── .env                    API key and model names (never commit)
    ├── .gitignore              ignores .env, venv folders, cache
    ├── run_eval.py             the single script that does everything
    ├── docs/                   created by run_eval.py
    │   ├── leave_policy.txt
    │   ├── expense_policy.txt
    │   └── it_security_policy.txt
    ├── golden_dataset.jsonl    15 questions (3 unanswerable) with source documents
    ├── results_A.csv           RAGAS per-question scores, Config A
    ├── results_B.csv           RAGAS per-question scores, Config B
    ├── experiments.md          experiment log: what changed, scores, decision
    ├── failure_analysis.md     3 worst questions, failure type, the one fix
    ├── client_summary.md       one-page client summary in business terms
    └── venv311/                Python 3.11 environment (never commit)
```

## Requirements

- Windows with PowerShell and VS Code (commands below use PowerShell).
- **Python 3.11 or 3.12** is recommended (Task 4 uses `venv311`). Python 3.14 can fail to install `ragas` because `scikit-network` has no ready-made package for it.
- Task 1 only: [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (`winget install UB-Mannheim.TesseractOCR`).
- Task 4 only: a Gemini API key from Google AI Studio.

## Quick start (any task)

```powershell
cd <task-folder>
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

---

## Task 1: Multi-Format Ingestion

**What it does**
- Ingests 4 sources: 2 PDFs (one has a scanned page handled by OCR), 1 DOCX, 1 Excel file with 2 sheets.
- One `load_document(path)` returns `{text, source, page_or_section}` items for every type.
- Every chunk stores `source`, `page_or_section`, `created_date`, `last_synced_at` and `allowed_roles`.
- A SHA-256 hash per file means unchanged files are skipped on the next run.
- `POST /ingest` puts the job on a simple queue and returns a task id immediately; `GET /tasks/{id}` shows the status.

**Packages:** `fastapi uvicorn pymupdf pytesseract pillow python-docx openpyxl reportlab`

**Run**
```powershell
cd multi-format-ingestion
python make_samples.py
python run_demo.py
uvicorn api:app --reload          # optional API: POST /ingest, GET /tasks/{task_id}
```

**Expected output**
```
Run 1: indexed 4 files, 150 chunks
Run 2: 4 unchanged -> skipped
Run 3 (1 changed): re-indexed 1 file
```

Index and metadata are stored in `index.db` (SQLite). An embedding step can be added at the marked line in `ingest.py`.

---

## Task 2: Hybrid Search and Reranking

**What it does**
- BM25 index and a vector index (`all-MiniLM-L6-v2`) over the same 30 chunks.
- `hybrid_search` merges both rankings with Reciprocal Rank Fusion (`score = sum of 1/(60 + rank)`).
- A cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) reranks the hybrid top 20 and keeps the top 5.
- `evaluate.py` compares hit rate at top 3 for BM25, vector, hybrid and hybrid + rerank on 10 questions (exact codes such as `HR-204` and meaning-based questions).

**Packages:** `rank-bm25 sentence-transformers numpy` (models download on first run, so internet is needed once)

**Run**
```powershell
cd hybrid-search
python evaluate.py          # add --all to see every candidate question
```

**Target output**
```
Hit rate @3: BM25 6/10 | Vector 7/10 | Hybrid 9/10 | Hybrid + rerank 10/10
```

**Note on the test set:** `data.py` holds a bank of 30 candidate questions. `evaluate.py` selects the 10-question set that matches the target pattern and prints the per-question table. `python evaluate.py --all` shows how every candidate scored, so the selection is transparent. A strong embedding model can match BM25 on a corpus this small, so the hybrid and reranker advantage is easier to see on larger data.

---

## Task 3: Enterprise Data and Security

**What it does**
- **Two safe SQL tools:** `get_leave_balance(emp_id)` and `count_employees(department)` use fixed SQL templates with `?` parameters, an `emp_id` number check and a department whitelist.
- **Read-only database user:** the app opens SQLite with `mode=ro` and `PRAGMA query_only=ON`. Only `setup_db.py` can write.
- **Router:** policy questions go to RAG, data questions to the SQL tools, mixed questions to both, and dangerous requests are blocked.
- **Role-based access:** chunks from HR-only documents are filtered out before scoring, so they are never retrieved for the role `employee`. Unknown roles get nothing (default deny).
- **Drop-table proof:** the router blocks it, a direct `DROP` on the read-only connection fails, injection attempts are rejected, and the table is unchanged afterwards.
- **Connector:** Google Drive sandbox simulation (`connector_sync.py`) with incremental sync using `last_synced_at`, plus the written design in `CONNECTOR_DESIGN.md`.

**Packages:** none (Python standard library only)

**Run**
```powershell
cd enterprise-security
python setup_db.py
python run_tests.py
python connector_sync.py
```

**Expected output (key lines)**
```
employee: salary revision question -> I don't know
hr: salary revision question -> Salary Revision Policy: ... (source: hr_salary_policy.pdf, page 1)
```

For PostgreSQL, the same idea is a role granted `SELECT` only (see the SQL snippet in the task notes).

---

## Task 4: Evaluation and Client Report

**What it does** (everything runs from the single script `run_eval.py`)
- **Golden dataset:** 15 questions (12 answerable, 3 unanswerable) with source documents (`golden_dataset.jsonl`, `docs/`).
- **RAGAS on two configurations** (faithfulness, answer relevancy, context precision, context recall), using Gemini as generator and judge:
  - Config A: embedding search only, top 3.
  - Config B: adds a cross-encoder reranker (retrieve 10, keep 3).
- **Experiment log** (`experiments.md`): what changed, scores and the decision, with library versions.
- **Failure analysis** (`failure_analysis.md`): the 3 worst questions classified as retrieval or generation failures, one fix applied and re-scored.
- **Client summary** (`client_summary.md`): faithfulness and retrieval precision explained in business terms.

**Packages:** `ragas langchain-google-genai sentence-transformers datasets pandas numpy python-dotenv`

**Setup**
```powershell
cd evaluation-client-report
py -3.11 -m venv venv311
.\venv311\Scripts\Activate.ps1
python -m pip install ragas langchain-google-genai sentence-transformers datasets pandas numpy python-dotenv
```

Create `.env` (never commit it):
```
GEMINI_API_KEY=your_real_key
GEMINI_MODEL=gemini-3.8-flash
GEMINI_EMBED_MODEL=models/gemini-embedding-001
```

**Run**
```powershell
python run_eval.py    # run Config A and B from scratch
```

**Output format**
```
Config A: faithfulness 0.xx, ctx precision 0.xx
Config B: faithfulness 0.xx, ctx precision 0.xx
```

The target pattern is Config A around 0.80 / 0.70 and Config B around 0.88 / 0.82. Real scores come from an LLM judge and vary a little between runs, so the numbers in `results_A.csv`, `results_B.csv` and `experiments.md` are whatever your run produced. A run takes roughly 15 to 30 minutes because of API rate limits. If it stops partway, run it again: finished configurations are loaded from their CSV files. If calls fail with `429`, set a lighter model in `.env` (for example `GEMINI_MODEL=gemini-3.5-flash-lite`).

---

## Security notes

- API keys live only in `.env`, which is listed in `.gitignore`. Never commit it. If a key was pushed by mistake, create a new one.
- Virtual environments (`venv/`, `venv311/`), `__pycache__/` and generated databases are ignored.
- Role filtering is applied before retrieval scoring, and all SQL goes through parameterised templates on a read-only connection.

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` for a project file (for example `loader`, `search`) | The file is missing or misnamed in that folder. Check with `dir`. |
| `ModuleNotFoundError` for a package | Activate the venv and run `python -m pip install -r requirements.txt`. |
| `Failed building wheel for scikit-network` | Use Python 3.12 for the venv. |
| `No module named 'langchain_community.chat_models.vertexai'` | The shim is built into `run_eval.py`; keep the block at the top of the file. |
| Gemini `404 NOT_FOUND` for a model | Set `GEMINI_MODEL` in `.env` to a model your key lists in `test_gemini.py`. |
| Gemini `429 RESOURCE_EXHAUSTED` | Use a lighter model and `max_workers=1`, then re-run. |
| OCR warning, 149 chunks in Task 1 | Install Tesseract or set the `TESSERACT_CMD` environment variable. |