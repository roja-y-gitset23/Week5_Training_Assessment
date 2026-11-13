import re
from sql_tools import get_leave_balance, count_employees
from rag import answer_rag

BLOCK = re.compile(r"\b(drop|delete|update|insert|alter|truncate|create|grant)\b|;|--", re.I)
POLICY_WORDS = ("policy", "policies", "rule", "rules", "guideline", "procedure", "carry forward")


def find_emp_id(q):
    m = re.search(r"\b(\d{3})\b", q)
    return int(m.group(1)) if m else None


def find_dept(q):
    for tok in re.findall(r"[A-Za-z]+", q):
        if tok.lower() == "hr" or tok == "IT" or tok.lower() in ("finance", "sales"):
            return tok
    return None


def route(q):
    if BLOCK.search(q):
        return "blocked"
    ql = q.lower()
    wants_balance = "balance" in ql and find_emp_id(q) is not None
    wants_count = any(p in ql for p in ("how many employees", "number of employees", "headcount")) \
        and find_dept(q) is not None
    data = wants_balance or wants_count
    policy = any(w in ql for w in POLICY_WORDS)
    if data and policy:
        return "mixed"
    return "data" if data else "policy"


def run_sql(q):
    ql, parts = q.lower(), []
    try:
        if "balance" in ql and find_emp_id(q) is not None:
            parts.append(get_leave_balance(find_emp_id(q)))
        if any(p in ql for p in ("how many employees", "number of employees", "headcount")) and find_dept(q):
            parts.append(count_employees(find_dept(q)))
    except ValueError as e:
        parts.append(f"Rejected: {e}")
    return " ; ".join(parts) if parts else "I don't know"


def ask(question, role):
    r = route(question)
    if r == "blocked":
        return r, "Refused: only read-only questions are supported. Nothing was executed."
    if r == "policy":
        return r, answer_rag(question, role)
    if r == "data":
        return r, run_sql(question)
    return r, run_sql(question) + " | " + answer_rag(question, role)     # mixed: both