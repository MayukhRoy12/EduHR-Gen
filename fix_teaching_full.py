import sqlite3
import pandas as pd
import numpy as np
import os
import random

# --- SETUP ---
DB_FILE = "academic_hr.db"
CSV_FILE = "teaching_progress_dataset (1).csv"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, DB_FILE)
csv_path = os.path.join(BASE_DIR, CSV_FILE)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🚀 RE-BUILDING TEACHING TRACKER (UNIQUE DATA)...")

# 1. Re-Create Table with Faculty ID
cursor.execute("DROP TABLE IF EXISTS teaching_progress")
cursor.execute("""
    CREATE TABLE teaching_progress (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_id INTEGER,
        week_number INTEGER,
        teacher_completion_pct INTEGER,
        student_avg_pct INTEGER,
        class_verdict TEXT
    )
""")

# 2. Load the Template CSV
if not os.path.exists(csv_path):
    print("❌ Error: CSV file not found.")
    exit()

template_df = pd.read_csv(csv_path)

# Calculate the template "Student Average" column
student_cols = [c for c in template_df.columns if "Est_%" in c]
template_df['student_avg_base'] = template_df[student_cols].mean(axis=1).astype(int)

# 3. Get All Faculty IDs
faculty_ids = pd.read_sql("SELECT faculty_id FROM faculty_master", conn)['faculty_id'].tolist()
print(f"📊 Generating data for {len(faculty_ids)} faculty members...")

# 4. Generate Unique Data for Each Faculty
count = 0
for fid in faculty_ids:
    # Random "Speed Factor" for this teacher
    # 0.8 = Slow teacher, 1.2 = Fast teacher
    speed_factor = random.uniform(0.85, 1.15) 
    
    # Random "Gap Factor" (How much students disagree)
    gap_noise = random.randint(-5, 5)
    
    for _, row in template_df.iterrows():
        # Apply variation to the base CSV numbers
        base_teach = row['Teacher_Reported_Completion_%']
        base_stud = row['student_avg_base']
        
        # Calculate unique values
        new_teach_pct = int(base_teach * speed_factor)
        new_teach_pct = min(100, max(0, new_teach_pct)) # Clamp 0-100
        
        new_stud_pct = int(base_stud * speed_factor) + gap_noise
        new_stud_pct = min(100, max(0, new_stud_pct))
        
        # Verdict Logic
        verdict = row['Ultimate_Class_Review']
        if new_teach_pct < (row['Week'] * 7):
            verdict = "Class feels the pace is too slow"
        elif new_teach_pct > (row['Week'] * 9):
            verdict = "Class feels the pace is too fast"
            
        cursor.execute("""
            INSERT INTO teaching_progress 
            (faculty_id, week_number, teacher_completion_pct, student_avg_pct, class_verdict)
            VALUES (?, ?, ?, ?, ?)
        """, (fid, row['Week'], new_teach_pct, new_stud_pct, verdict))
        
    count += 1

conn.commit()
conn.close()
print(f"✅ Success! Generated unique teaching logs for {count} faculty.")
