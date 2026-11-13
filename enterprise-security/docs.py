ALL = ["employee", "hr", "admin"]
HR = ["hr", "admin"]

CHUNKS = [
 {"id": "d1", "source": "leave_policy.pdf", "section": "page 1", "allowed_roles": ALL,
  "text": "Leave Policy: Full-time employees receive 24 days of annual leave per year. Unused leave can carry forward up to 5 days into the next year."},
 {"id": "d2", "source": "travel_policy.pdf", "section": "page 1", "allowed_roles": ALL,
  "text": "Travel Reimbursement Policy: Employees must submit travel claims with receipts within 30 days. Claims above 500 dollars need manager approval."},
 {"id": "d3", "source": "remote_work_policy.docx", "section": "Section 2", "allowed_roles": ALL,
  "text": "Remote Work Policy: Employees may work remotely up to three days per week with manager approval."},
 {"id": "d4", "source": "it_security.pdf", "section": "page 3", "allowed_roles": ALL,
  "text": "Password Rules: Passwords must have 12 characters and be changed every 90 days."},
 {"id": "d5", "source": "payroll_faq.xlsx", "section": "Sheet1!row2", "allowed_roles": ALL,
  "text": "Payday: pay is credited on the last working day of each month."},

 # ---- HR-only document: must NEVER be returned for role "employee" ----
 {"id": "h1", "source": "hr_salary_policy.pdf", "section": "page 1", "allowed_roles": HR,
  "text": "Salary Revision Policy: Salaries are revised every April. The revision is between 5 and 12 percent based on the performance rating and is approved by the HR director."},
 {"id": "h2", "source": "hr_salary_policy.pdf", "section": "page 2", "allowed_roles": HR,
  "text": "Salary Revision exceptions: Promotions can trigger an off cycle salary revision with written approval from the HR director."},
 {"id": "h3", "source": "hr_disciplinary_cases.docx", "section": "Section 1", "allowed_roles": HR,
  "text": "Disciplinary Cases: Confidential records of employee warnings are kept by HR for five years."},
]

HR_ONLY_SOURCES = {c["source"] for c in CHUNKS if "employee" not in c["allowed_roles"]}