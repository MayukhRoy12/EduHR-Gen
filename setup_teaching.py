import sqlite3
import pandas as pd
import os

# --- SETUP ---
DB_FILE = "academic_hr.db"
CSV_FILE = "teaching_progress_dataset (1).csv"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, DB_FILE)
csv_path = os.path.join(BASE_DIR, CSV_FILE)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🚀 SETTING UP TEACHING TRACKER...")

# 1. Create Table
cursor.execute("DROP TABLE IF EXISTS teaching_progress")
cursor.execute("""
    CREATE TABLE teaching_progress (
        week_number INTEGER,
        teacher_completion_pct INTEGER,
        student_avg_pct INTEGER,
        class_verdict TEXT
    )
""")

# 2. Process CSV
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    
    # We need to calculate the "Average Student Estimate" from columns like "Student_1_Est_%"
    student_cols = [c for c in df.columns if "Est_%" in c]
    
    # Calculate row-wise average
    df['student_avg'] = df[student_cols].mean(axis=1).astype(int)
    
    print(f"📥 Importing {len(df)} weeks of teaching logs...")
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO teaching_progress (week_number, teacher_completion_pct, student_avg_pct, class_verdict)
            VALUES (?, ?, ?, ?)
        """, (
            row['Week'],
            row['Teacher_Reported_Completion_%'],
            row['student_avg'],
            row['Ultimate_Class_Review']
        ))
    
    conn.commit()
    print("✅ Teaching data loaded successfully!")
else:
    print(f"❌ Error: Could not find {CSV_FILE}")

conn.close()
