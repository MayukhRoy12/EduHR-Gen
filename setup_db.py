import sqlite3

# Connect to the database
conn = sqlite3.connect('academic_hr.db')
c = conn.cursor()

# 1. Create the 'faculty' table
c.execute('''
CREATE TABLE IF NOT EXISTS faculty (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    department TEXT
)
''')

# 2. Create the 'teaching_logs' table
# Note: linking 'faculty_id' to the faculty table
c.execute('''
CREATE TABLE IF NOT EXISTS teaching_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    faculty_id INTEGER,
    course_name TEXT,
    semester TEXT,
    syllabus_covered_percent INTEGER,
    recovery_plan TEXT,
    FOREIGN KEY(faculty_id) REFERENCES faculty(id)
)
''')

# 3. Insert SNEHA SINGH (ID 101)
# We use 'INSERT OR IGNORE' to prevent duplicates if you run this twice
c.execute("INSERT OR IGNORE INTO faculty (id, name, department) VALUES (101, 'Sneha Singh', 'Computer Science')")

# 4. Insert SAMPLE TEACHING LOGS for her
# This is the data that should show up in your screenshot
data_to_insert = [
    (101, 'Data Structures', 'Spring 2024', 45, 'Extra class scheduled for Saturday'),
    (101, 'Operating Systems', 'Spring 2024', 30, 'Online module assigned for recovery')
]

c.executemany('''
INSERT INTO teaching_logs (faculty_id, course_name, semester, syllabus_covered_percent, recovery_plan)
VALUES (?, ?, ?, ?, ?)
''', data_to_insert)

# 5. COMMIT THE CHANGES (Crucial step!)
conn.commit()

print("Success! Database initialized with Faculty ID 101 and 2 teaching logs.")

# Verify immediately
check = c.execute("SELECT * FROM teaching_logs WHERE faculty_id=101").fetchall()
print(f"Verification: Found {len(check)} logs for Sneha Singh.")

conn.close()
