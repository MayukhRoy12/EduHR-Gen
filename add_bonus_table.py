import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "academic_hr.db")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

print("🚀 UPDATING DATABASE SCHEMA...")

# Create a table to track extra leave grants
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bonus_leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER,
        leave_type TEXT,
        extra_days INTEGER,
        granted_date TEXT
    )
""")

conn.commit()
conn.close()
print("✅ Success! 'bonus_leaves' table created.")
