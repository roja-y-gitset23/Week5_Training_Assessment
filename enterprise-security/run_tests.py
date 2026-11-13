import sqlite3
from router import ask, route
from rag import retrieve
from docs import CHUNKS, HR_ONLY_SOURCES
from sql_tools import ro_connection, get_leave_balance, count_employees

print("=== 1. Role-based access ===")
Q = "What is the salary revision policy?"
for role in ("employee", "hr"):
    print(f"{role}: salary revision question -> {ask(Q, role)[1]}")

print("\n=== 2. Routing (role = employee) ===")
QUESTIONS = [
    "What is the leave policy for annual leave?",
    "What is the leave balance of employee 101?",
    "How many employees are in IT?",
    "What is the travel reimbursement policy?",
    "What is the leave balance of employee 102 and what does the leave policy say about carry forward?",
    "How many employees are in HR and what is the remote work policy?",
]
print(f"{'#':<3}{'Route':<8}Question")
for n, q in enumerate(QUESTIONS, start=1):
    r, a = ask(q, "employee")
    print(f"{n:<3}{r:<8}{q}")
    print(f"   -> {a}")

print("\n=== 3. HR-only chunks never retrieved for role 'employee' ===")
probes = QUESTIONS + [Q, "salary revision", "HR director approval", "disciplinary cases warnings",
                      "promotion off cycle salary revision", "confidential records HR five years"]
probes += [c["text"] for c in CHUNKS]                  # every chunk text used as a query
leaks = 0
for p in probes:
    leaks += sum(1 for c in retrieve(p, "employee", k=50) if c["source"] in HR_ONLY_SOURCES)
print(f"HR-only sources: {sorted(HR_ONLY_SOURCES)}")
print(f"Queries tried: {len(probes)} | HR-only chunks returned to employee: {leaks}")
print("PASS" if leaks == 0 else "FAIL")
print("Unknown role 'guest' gets:", retrieve("leave policy", "guest"), "(default deny)")

print("\n=== 4. 'drop the leave table' cannot execute anything ===")
r, a = ask("drop the leave table", "employee")
print(f"Router: route={r} -> {a}")

try:                                                     # even if someone bypassed the router
    ro_connection().execute("DROP TABLE leaves")
except sqlite3.OperationalError as e:
    print(f"Direct DROP on read-only connection -> error: {e}")

for label, fn, arg in [("injection in department", count_employees, "IT'; DROP TABLE leaves;--"),
                       ("injection in emp_id", get_leave_balance, "101; DROP TABLE leaves")]:
    try:
        fn(arg)
    except ValueError as e:
        print(f"{label} -> rejected: {e}")

con = ro_connection()
tables = [t[0] for t in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
rows = con.execute("SELECT COUNT(*) FROM leaves").fetchone()[0]
print(f"After all attempts: tables = {tables}, rows in leaves = {rows}  (unchanged)")