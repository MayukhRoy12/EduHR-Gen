import sqlite3
import os
import random

# 1. SETUP PATHS (Forces the script to find the exact right file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")

print(f"🔌 CONNECTING TO: {DB_FILE}")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 2. ENSURE TABLE EXISTS
cursor.execute("""
    CREATE TABLE IF NOT EXISTS teaching_progress (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER,
        week_number INTEGER,
        teacher_completion_pct INTEGER,
        student_avg_pct INTEGER,
        class_verdict TEXT
    )
""")

# 3. GET ALL FACULTY IDs
try:
    faculty_ids = [row[0] for row in cursor.execute("SELECT faculty_id FROM faculty_master").fetchall()]
    print(f"📊 Found {len(faculty_ids)} faculty members.")
except:
    print("❌ CRITICAL: Could not read faculty_master. Is the DB empty?")
    exit()

# 4. GENERATE & INJECT DATA
print("🚀 Injecting teaching logs for EVERYONE...")
cursor.execute("DELETE FROM teaching_progress") # Clear old data

records = []

for fid in faculty_ids:
    # Give everyone a slightly different speed
    speed = random.uniform(0.9, 1.1) 
    
    current_progress = 0
    
    for week in range(1, 13): # Weeks 1 to 12
        # Progress increases by ~8% per week
        increment = int(8 * speed)
        current_progress += increment
        
        # Clamp to 100%
        if current_progress > 100: current_progress = 100
        
        # Student perception is usually slightly lower (-5%)
        student_view = max(0, current_progress - random.randint(0, 10))
        
        # Verdict
        if current_progress < (week * 7): verdict = "Lagging Behind"
        elif current_progress > (week * 9): verdict = "Too Fast"
        else: verdict = "On Track"
        
        records.append((fid, week, current_progress, student_view, verdict))

cursor.executemany("""
    INSERT INTO teaching_progress 
    (faculty_id, week_number, teacher_completion_pct, student_avg_pct, class_verdict)
    VALUES (?, ?, ?, ?, ?)
""", records)

conn.commit()
conn.close()
print(f"✅ SUCCESS! Injected {len(records)} teaching logs.")
print("👉 Restart Streamlit (Ctrl+C -> streamlit run app.py) and check Tab 6.")
