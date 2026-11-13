import sqlite3
from contextlib import closing
from pathlib import Path

DB_URI = Path("leave.db").resolve().as_uri() + "?mode=ro"     # read-only open
DEPARTMENTS = {"HR", "IT", "FINANCE", "SALES"}                # whitelist

SQL_BALANCE = ("SELECT e.name, l.annual_total - l.used FROM employees e "
               "JOIN leaves l ON l.emp_id = e.emp_id WHERE e.emp_id = ?")
SQL_COUNT = "SELECT COUNT(*) FROM employees WHERE UPPER(department) = ?"


def ro_connection():
    """Read-only 'database user': cannot INSERT, UPDATE, DELETE or DROP anything."""
    con = sqlite3.connect(DB_URI, uri=True)
    con.execute("PRAGMA query_only = ON")
    return con


def get_leave_balance(emp_id):
    if isinstance(emp_id, bool) or not str(emp_id).isdigit():
        raise ValueError("emp_id must be a whole number")
    with closing(ro_connection()) as con:
        row = con.execute(SQL_BALANCE, (int(emp_id),)).fetchone()   # parameter, not string join
    if not row:
        return f"No employee with id {emp_id}"
    return f"{row[0]} (id {emp_id}) has {row[1]} leave days left"


def count_employees(department):
    dep = str(department).strip().upper()
    if dep not in DEPARTMENTS:
        raise ValueError(f"Unknown department: {department!r}")
    with closing(ro_connection()) as con:
        n = con.execute(SQL_COUNT, (dep,)).fetchone()[0]
    return f"{n} employees in {dep}"