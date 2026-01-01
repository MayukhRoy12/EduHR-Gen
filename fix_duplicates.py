import pandas as pd
import sqlite3
import os
import random
import shutil

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")
FACULTY_CSV = os.path.join(BASE_DIR, "faculty_dataset_(2).csv")
PERFORMANCE_CSV = os.path.join(BASE_DIR, "Performance_dataset.csv")
FEEDBACK_CSV = os.path.join(BASE_DIR, "feedback_dataset.csv")
LEAVE_CSV = os.path.join(BASE_DIR, "leave_dataset_.csv")

print("🚀 STARTING DUPLICATE REMOVAL & SYSTEM RESET...")

# 1. CLEAN THE FACULTY CSV
if os.path.exists(FACULTY_CSV):
    df = pd.read_csv(FACULTY_CSV)
    original_count = len(df)
    
    # Identify the Name column
    name_col = next((c for c in df.columns if "name" in c.lower()), None)
    
    if name_col:
        # DROP DUPLICATES based on Name (Keep the first occurrence)
        df_clean = df.drop_duplicates(subset=[name_col], keep='first')
        new_count = len(df_clean)
        
        # Save the cleaned version back to the file
        df_clean.to_csv(FACULTY_CSV, index=False)
        print(f"🧹 Cleaned CSV: Reduced from {original_count} to {new_count} unique faculty.")
    else:
        print("❌ Error: Could not find Name column in CSV.")
        exit()
else:
    print("❌ Error: Faculty CSV not found.")
    exit()

# 2. DELETE OLD DATABASE
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("🗑️  Deleted old database (with duplicates).")

# 3. REBUILD DATABASE
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create Tables
cursor.execute("""
    CREATE TABLE faculty_master (
        faculty_id INTEGER PRIMARY KEY, 
        name TEXT, designation TEXT, department TEXT, joining_date TEXT
    )
""")
cursor.execute("""
    CREATE TABLE research_records (
        research_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER, publications_count INTEGER, patents_count INTEGER, projects_count INTEGER,
        FOREIGN KEY(faculty_id) REFERENCES faculty_master(faculty_id)
    )
""")
cursor.execute("""
    CREATE TABLE student_feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER, course_name TEXT, rating INTEGER, feedback_comment TEXT, sentiment_label TEXT,
        teaching_clarity_score INTEGER, engagement_score INTEGER, pace_score INTEGER,
        FOREIGN KEY(faculty_id) REFERENCES faculty_master(faculty_id)
    )
""")
cursor.execute("""
    CREATE TABLE leave_records (
        leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER, type TEXT, days_requested INTEGER, status TEXT
    )
""")
cursor.execute("""
    CREATE TABLE teaching_progress (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER, week_number INTEGER, teacher_completion_pct INTEGER, student_avg_pct INTEGER, class_verdict TEXT
    )
""")
cursor.execute("""
    CREATE TABLE bonus_leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER, leave_type TEXT, extra_days INTEGER, granted_date TEXT
    )
""")

print("✅ Created fresh table structure.")

# 4. RELOAD DATA (Now Unique)
# Load Faculty
for _, row in df_clean.iterrows():
    cursor.execute("INSERT INTO faculty_master (faculty_id, name, designation, department, joining_date) VALUES (?, ?, ?, ?, ?)", 
                   (row['faculty_id'], row[name_col], row['designation'], row['department'], row['date_of_joining']))

# Load Research (Matched by ID)
if os.path.exists(PERFORMANCE_CSV):
    df_perf = pd.read_csv(PERFORMANCE_CSV)
    # Filter to only include IDs that exist in our clean list
    clean_ids = set(df_clean['faculty_id'])
    df_perf = df_perf[df_perf['faculty_id'].isin(clean_ids)]
    
    for _, row in df_perf.iterrows():
        total_papers = row.get('journal_publications', 0) + row.get('research_papers', 0) + row.get('conference_papers', 0)
        cursor.execute("INSERT INTO research_records (faculty_id, publications_count, patents_count, projects_count) VALUES (?, ?, ?, ?)",
                       (row['faculty_id'], int(total_papers), int(row.get('patents', 0)), 0))

# Load Feedback & Leaves (Simpler reload)
if os.path.exists(FEEDBACK_CSV):
    df_feed = pd.read_csv(FEEDBACK_CSV)
    df_feed = df_feed[df_feed['faculty_id'].isin(clean_ids)]
    for _, row in df_feed.iterrows():
        cursor.execute("INSERT INTO student_feedback (faculty_id, course_name, rating, feedback_comment, sentiment_label, teaching_clarity_score, engagement_score, pace_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (row['faculty_id'], row['course_name'], row['rating'], row['feedback_comment'], row['sentiment_label'], row['teaching_clarity_score'], row['engagement_score'], row['pace_score']))

if os.path.exists(LEAVE_CSV):
    df_leave = pd.read_csv(LEAVE_CSV)
    df_leave = df_leave[df_leave['faculty_id'].isin(clean_ids)]
    days_col = [c for c in df_leave.columns if "days" in c.lower()][0]
    for _, row in df_leave.iterrows():
        cursor.execute("INSERT INTO leave_records (faculty_id, type, days_requested, status) VALUES (?, ?, ?, ?)",
                       (row['faculty_id'], row['type'], row[days_col], row['status']))

# 5. GENERATE TEACHING DATA (Diverse Personas)
print("📈 Regenerating diverse teaching logs...")
faculty_ids = df_clean['faculty_id'].tolist()
for fid in faculty_ids:
    persona = random.choice(['fast', 'consistent', 'consistent', 'slow', 'struggling'])
    if persona == 'fast': base_inc = 10; variance = 2
    elif persona == 'consistent': base_inc = 8; variance = 1
    elif persona == 'slow': base_inc = 6; variance = 2
    else: base_inc = 4; variance = 3
    
    current_progress = 0
    for week in range(1, 13):
        inc = base_inc + random.randint(-variance, variance)
        current_progress += max(0, inc)
        if current_progress > 100: current_progress = 100
        gap = random.randint(0, 10)
        student_view = max(0, current_progress - gap)
        target = week * 8
        if current_progress < (target - 15): verdict = "Lagging Behind"
        elif current_progress > (target + 15): verdict = "Too Fast"
        else: verdict = "On Track"
        
        cursor.execute("INSERT INTO teaching_progress (faculty_id, week_number, teacher_completion_pct, student_avg_pct, class_verdict) VALUES (?, ?, ?, ?, ?)", 
                       (fid, week, current_progress, student_view, verdict))

conn.commit()
conn.close()
print("✅ SUCCESS! System reset with UNIQUE faculty list.")
print("👉 Restart Streamlit (Ctrl+C -> streamlit run app.py).")
