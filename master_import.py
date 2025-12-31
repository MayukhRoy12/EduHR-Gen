import sqlite3
import pandas as pd
import os

# --- FILES ---
DB_FILE = "academic_hr.db"
FACULTY_CSV = "faculty_dataset_(2).csv"
PERFORMANCE_CSV = "Performance_dataset.csv"
FEEDBACK_CSV = "feedback_dataset.csv"
LEAVE_CSV = "leave_dataset_.csv"

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, DB_FILE)

print("🚀 STARTING MASTER DATA IMPORT...")

# 1. CLEAN SLATE (Delete old DB)
if os.path.exists(db_path):
    os.remove(db_path)
    print("🗑️  Deleted old database to start fresh.")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. CREATE TABLES
# Faculty Table
cursor.execute("""
    CREATE TABLE faculty_master (
        faculty_id INTEGER PRIMARY KEY, 
        name TEXT,
        designation TEXT,
        department TEXT,
        joining_date TEXT
    )
""")

# Research Table
cursor.execute("""
    CREATE TABLE research_records (
        research_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER,
        publications_count INTEGER,
        patents_count INTEGER,
        projects_count INTEGER,
        FOREIGN KEY(faculty_id) REFERENCES faculty_master(faculty_id)
    )
""")

# Feedback Table (For your REAL student comments)
cursor.execute("""
    CREATE TABLE student_feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER,
        course_name TEXT,
        rating INTEGER,
        feedback_comment TEXT,
        sentiment_label TEXT,
        teaching_clarity_score INTEGER,
        engagement_score INTEGER,
        pace_score INTEGER,
        FOREIGN KEY(faculty_id) REFERENCES faculty_master(faculty_id)
    )
""")

# Leave Table
cursor.execute("""
    CREATE TABLE leave_records (
        leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER,
        type TEXT,
        days_requested INTEGER,
        status TEXT
    )
""")
print("✅ Created all table structures.")

# 3. IMPORT FACULTY (Master List)
# We use the ID from the CSV as the REAL Key
df_fac = pd.read_csv(os.path.join(BASE_DIR, FACULTY_CSV))
print(f"📥 Importing {len(df_fac)} Faculty...")

for _, row in df_fac.iterrows():
    cursor.execute("""
        INSERT INTO faculty_master (faculty_id, name, designation, department, joining_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        row['faculty_id'], 
        row['name'], 
        row['designation'], 
        row['department'], 
        row['date_of_joining']
    ))

# 4. IMPORT RESEARCH (Performance)
# We link strictly by ID, so it never fails.
df_perf = pd.read_csv(os.path.join(BASE_DIR, PERFORMANCE_CSV))
print(f"📥 Importing Research Metrics for {len(df_perf)} faculty...")

for _, row in df_perf.iterrows():
    # Summing all paper types as per your request
    total_papers = (
        row.get('journal_publications', 0) + 
        row.get('research_papers', 0) + 
        row.get('conference_papers', 0) +
        row.get('scopus_indexed_papers', 0)
    )
    
    cursor.execute("""
        INSERT INTO research_records (faculty_id, publications_count, patents_count, projects_count)
        VALUES (?, ?, ?, ?)
    """, (
        row['faculty_id'],
        int(total_papers),
        int(row.get('patents', 0)),
        0 # Projects column missing in CSV, defaulting to 0
    ))

# 5. IMPORT FEEDBACK (Real Comments)
df_feed = pd.read_csv(os.path.join(BASE_DIR, FEEDBACK_CSV))
print(f"📥 Importing {len(df_feed)} Real Student Feedback rows...")

for _, row in df_feed.iterrows():
    cursor.execute("""
        INSERT INTO student_feedback 
        (faculty_id, course_name, rating, feedback_comment, sentiment_label, 
         teaching_clarity_score, engagement_score, pace_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row['faculty_id'],
        row['course_name'],
        row['rating'],
        row['feedback_comment'],
        row['sentiment_label'],
        row['teaching_clarity_score'],
        row['engagement_score'],
        row['pace_score']
    ))

# 6. IMPORT LEAVES
df_leave = pd.read_csv(os.path.join(BASE_DIR, LEAVE_CSV))
print(f"📥 Importing {len(df_leave)} Leave Records...")

# Handle the column name with extra space: "days requested "
days_col = [c for c in df_leave.columns if "days" in c.lower()][0]

for _, row in df_leave.iterrows():
    cursor.execute("""
        INSERT INTO leave_records (faculty_id, type, days_requested, status)
        VALUES (?, ?, ?, ?)
    """, (
        row['faculty_id'],
        row['type'],
        row[days_col],
        row['status']
    ))

conn.commit()
conn.close()
print("\n🎉 SUCCESS! Your database is now 100% powered by your REAL files.")
print("👉 Restart Streamlit (Ctrl+C -> streamlit run app.py) to see the magic.")
