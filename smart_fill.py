import sqlite3
import pandas as pd
import os
import random

# --- FILES ---
DB_FILE = "academic_hr.db"
FACULTY_CSV = "faculty_dataset_(2).csv"
FEEDBACK_CSV = "feedback_dataset.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, DB_FILE)

print("🚀 STARTING SMART FEEDBACK FILL (10 REVIEWS PER FACULTY)...")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. CLEAR OLD TABLE
cursor.execute("DELETE FROM student_feedback")
print("🧹 Cleared student_feedback table.")

# 2. LOAD DATASETS
df_faculty = pd.read_csv(os.path.join(BASE_DIR, FACULTY_CSV))
df_real_feedback = pd.read_csv(os.path.join(BASE_DIR, FEEDBACK_CSV))

# Get list of IDs that actually have real feedback
ids_with_real_data = set(df_real_feedback['faculty_id'].unique())
print(f"📊 Found {len(ids_with_real_data)} faculty with REAL feedback.")

# 3. INSERT REAL DATA (Priority 1)
print("📥 Importing real feedback rows...")
real_count = 0
for _, row in df_real_feedback.iterrows():
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
    real_count += 1

# 4. GENERATE MISSING DATA (Priority 2)
POSITIVE_COMMENTS = ["Excellent teaching style.", "Very clear concepts.", "Loved the class.", "Great examples.", "Very helpful professor.", "Inspiring lectures.", "Best class this sem.", "Explained perfectly."]
NEUTRAL_COMMENTS = ["Good but fast.", "Average experience.", "Okay lectures.", "Strict on attendance.", "Content was decent.", "Could be more engaging.", "Standard delivery.", "Notes were helpful."]
NEGATIVE_COMMENTS = ["Hard to understand.", "Boring lectures.", "Not helpful.", "Confusing explanation.", "Voice not audible.", "Too much homework.", "Disorganized class.", "Hard to follow."]
courses = ["CS101", "AI202", "DS303", "ENG101", "MATH101"]

print("🤖 Generating 10 reviews for missing faculty...")
gen_count = 0
for _, row in df_faculty.iterrows():
    fid = row['faculty_id']
    
    # SKIP if they already have real data
    if fid in ids_with_real_data:
        continue
        
    # LOGIC: Use their 'teaching_feedback_score' from CSV
    raw_score = row.get('teaching_feedback_score', 5.0)
    if pd.isna(raw_score): raw_score = 5.0
    
    base_rating = raw_score / 2 if raw_score > 5 else raw_score
    
    # --- CHANGED FROM 5 TO 10 HERE ---
    for _ in range(10):
        # Add slight variation (-1, 0, +1)
        rating = int(base_rating + random.choice([-1, 0, 0, 1])) # skewed to be closer to base
        rating = max(1, min(5, rating)) # Clamp between 1 and 5
        
        if rating >= 4:
            comm = random.choice(POSITIVE_COMMENTS)
            sent = "Positive"
        elif rating == 3:
            comm = random.choice(NEUTRAL_COMMENTS)
            sent = "Neutral"
        else:
            comm = random.choice(NEGATIVE_COMMENTS)
            sent = "Negative"
            
        cursor.execute("""
            INSERT INTO student_feedback 
            (faculty_id, course_name, rating, feedback_comment, sentiment_label, teaching_clarity_score, engagement_score, pace_score) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fid, 
            random.choice(courses), 
            rating, 
            comm, 
            sent,
            random.randint(60, 95), 
            random.randint(60, 95), 
            random.randint(60, 95)
        ))
        gen_count += 1

conn.commit()
conn.close()

print(f"\n🏁 DONE!")
print(f"✅ Real Records Loaded: {real_count}")
print(f"✅ Generated Records:   {gen_count}")
print("👉 Restart Streamlit. Every faculty member now has 10 reviews!")
