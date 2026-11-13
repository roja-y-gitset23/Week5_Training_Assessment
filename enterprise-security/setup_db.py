import sqlite3, os

if os.path.exists("leave.db"):
    os.remove("leave.db")

con = sqlite3.connect("leave.db")          # this is the ONLY writer; the app never uses it
con.executescript("""
CREATE TABLE employees(
    emp_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL
);
CREATE TABLE leaves(
    emp_id INTEGER PRIMARY KEY REFERENCES employees(emp_id),
    annual_total INTEGER NOT NULL,
    used INTEGER NOT NULL
);
""")
con.executemany("INSERT INTO employees VALUES (?,?,?)", [
    (101, "Asha", "IT"), (102, "Ravi", "HR"), (103, "Meena", "Finance"),
    (104, "Kiran", "IT"), (105, "Sara", "Sales"), (106, "John", "IT"),
    (107, "Priya", "HR"), (108, "Arun", "Finance"),
])
con.executemany("INSERT INTO leaves VALUES (?,?,?)", [
    (101, 24, 10), (102, 24, 4), (103, 24, 12), (104, 24, 0),
    (105, 24, 20), (106, 24, 7), (107, 24, 3), (108, 24, 15),
])
con.commit()
con.close()
print("leave.db created: 8 employees, 8 leave rows")