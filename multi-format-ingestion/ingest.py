import os, glob, json, hashlib, sqlite3, datetime as dt
from loader import load_document

DB = "index.db"
DATA_DIR = "data"
CHUNK_SIZE = 800      # characters; items shorter than this stay as 1 chunk
OVERLAP = 100
SUPPORTED = (".pdf", ".docx", ".xlsx")

# who may see each file (used later by secured retrieval)
ROLES = {
    "policy_handbook.pdf": ["employee", "hr", "admin"],
    "finance_manual.pdf":  ["finance", "admin"],
    "hr_guidelines.docx":  ["hr", "admin"],
    "company_data.xlsx":   ["hr", "finance", "admin"],
}


def get_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS files(
        source TEXT PRIMARY KEY, hash TEXT, last_synced_at TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS chunks(
        id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, page_or_section TEXT,
        chunk_no INTEGER, text TEXT, created_date TEXT,
        last_synced_at TEXT, allowed_roles TEXT)""")
    return con


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def chunk_text(text):
    if len(text) <= CHUNK_SIZE:
        return [text]
    out, start = [], 0
    while start < len(text):
        out.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - OVERLAP
    return out


def index_file(con, path, src, h):
    created = dt.datetime.fromtimestamp(os.path.getctime(path)).date().isoformat()
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    roles = json.dumps(ROLES.get(src, ["admin"]))

    con.execute("DELETE FROM chunks WHERE source=?", (src,))   # remove old version
    count = 0
    for item in load_document(path):
        for n, piece in enumerate(chunk_text(item["text"])):
            # >>> embedding + vector-store upsert would go here <<<
            con.execute(
                "INSERT INTO chunks(source,page_or_section,chunk_no,text,created_date,"
                "last_synced_at,allowed_roles) VALUES (?,?,?,?,?,?,?)",
                (src, item["page_or_section"], n, piece, created, now, roles))
            count += 1
    con.execute("INSERT OR REPLACE INTO files(source,hash,last_synced_at) VALUES (?,?,?)",
                (src, h, now))
    return count


def run_ingest(data_dir=DATA_DIR):
    con = get_db()
    indexed = skipped = chunks = 0
    for path in sorted(glob.glob(os.path.join(data_dir, "*"))):
        if not path.lower().endswith(SUPPORTED):
            continue
        src, h = os.path.basename(path), file_hash(path)
        row = con.execute("SELECT hash FROM files WHERE source=?", (src,)).fetchone()
        if row and row[0] == h:
            skipped += 1
            continue
        chunks += index_file(con, path, src, h)
        indexed += 1
        con.commit()
    con.close()
    return {"indexed": indexed, "skipped": skipped, "chunks": chunks}