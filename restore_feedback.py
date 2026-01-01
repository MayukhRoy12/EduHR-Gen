import sqlite3
import pandas as pd
import os
import random

# --- SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")
FEEDBACK_CSV = os.path.join(BASE_DIR, "feedback_dataset.csv")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("🚀 GENERATING 50 REVIEWS PER FACULTY...")

# 1. Clear Old Data
cursor.execute("DELETE FROM student_feedback")
print("🧹 Cleared old feedback data.")

# 2. Expanded Comment Banks (For Variety)
POSITIVE = [
    "Excellent teaching style.", "Concepts are very clear.", "Great real-world examples.", 
    "Helpful professor.", "Best class of the semester.", "Very inspiring lectures.",
    "Always available for doubts.", "Strict but fair.", "Notes are very detailed.",
    "Makes complex topics easy.", "Highly recommended.", "Great energy in class."
]
NEUTRAL = [
    "Good but fast.", "Average experience.", "Okay lectures.", "Strict attendance.", 
    "Standard content.", "Notes are good.", "Could be more interactive.",
    "Follows the book too closely.", "Decent but boring at times.", "Okay for credits."
]
NEGATIVE = [
    "Hard to understand.", "Boring lectures.", "Not helpful with doubts.", "Confusing explanations.", 
    "Voice too low.", "Disorganized notes.", "Too fast to follow.", "Unfair grading.",
    "Doesn't reply to emails.", "Classes are often cancelled."
]
COURSES = ["CS101", "AI202", "DS303", "ENG101", "MATH101", "PHY202", "CHEM101"]

# 3. Load Real Data (If available)
real_count = 0
ids_with_data = set()
if os.path.exists(FEEDBACK_CSV):
    df_real = pd.read_csv(FEEDBACK_CSV)
    for _, row in df_real.iterrows():
        try:
            cursor.execute("""
                INSERT INTO student_feedback 
                (faculty_id, course_name, rating, feedback_comment, sentiment_label, 
                 teaching_clarity_score, engagement_score, pace_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['faculty_id'], row['course_name'], row['rating'], 
                row['feedback_comment'], row['sentiment_label'], 
                row['teaching_clarity_score'], row['engagement_score'], row['pace_score']
            ))
            real_count += 1
            ids_with_data.add(row['faculty_id'])
        except: pass

# 4. Generate 50 Reviews for Everyone Else
db_ids = [row[0] for row in cursor.execute("SELECT faculty_id FROM faculty_master").fetchall()]

gen_count = 0
for fid in db_ids:
    if fid in ids_with_data: continue # Skip if they have real data
        
    # Assign a Persona
    quality = random.choice(['high', 'high', 'med', 'med', 'low'])
    
    # Generate 50 reviews (Changed from 10)
    for _ in range(50):
        if quality == 'high':
            rating = random.randint(4, 5)
            comm = random.choice(POSITIVE)
            sent = "Positive"
        elif quality == 'med':
            rating = random.randint(3, 4)
            comm = random.choice(NEUTRAL if rating == 3 else POSITIVE)
            sent = "Neutral" if rating == 3 else "Positive"
        else:
            rating = random.randint(1, 3)
            comm = random.choice(NEGATIVE if rating < 3 else NEUTRAL)
            sent = "Negative" if rating < 3 else "Neutral"
            
        cursor.execute("""
            INSERT INTO student_feedback 
            (faculty_id, course_name, rating, feedback_comment, sentiment_label, teaching_clarity_score, engagement_score, pace_score) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fid, random.choice(COURSES), rating, comm, sent,
            random.randint(60, 100), random.randint(60, 100), random.randint(60, 100)
        ))
    gen_count += 1

conn.commit()
conn.close()
print(f"✅ Generated 50 reviews each for {gen_count} faculty members.")
