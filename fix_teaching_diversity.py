import sqlite3
import os
import random

# --- SETUP PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("🚀 STARTING DIVERSE TEACHING DATA GENERATION...")

# 1. Get All Faculty IDs
try:
    faculty_ids = [row[0] for row in cursor.execute("SELECT faculty_id FROM faculty_master").fetchall()]
    print(f"📊 Found {len(faculty_ids)} faculty members.")
except:
    print("❌ Error: Could not read faculty_master table.")
    exit()

# 2. CLEAR OLD TABLE
cursor.execute("DELETE FROM teaching_progress")
print("🧹 Cleared old identical data.")

# 3. GENERATE UNIQUE DATA FOR EVERYONE
count = 0
for fid in faculty_ids:
    # Assign a Random Persona
    persona = random.choice(['fast', 'consistent', 'consistent', 'slow', 'struggling'])
    
    if persona == 'fast':
        base_inc = 10; variance = 2  # Finishes early (Week 10)
    elif persona == 'consistent':
        base_inc = 8; variance = 1   # Finishes on time (Week 12)
    elif persona == 'slow':
        base_inc = 6; variance = 2   # Reaches ~72%
    else: # struggling
        base_inc = 4; variance = 3   # Reaches ~50%
    
    current_progress = 0
    
    for week in range(1, 13):
        # Calculate Progress
        inc = base_inc + random.randint(-variance, variance)
        current_progress += max(0, inc)
        if current_progress > 100: current_progress = 100
        
        # Student View (Slightly lower/random)
        gap = random.randint(0, 10)
        student_view = max(0, current_progress - gap)
        
        # Verdict Logic
        target = week * 8
        if current_progress < (target - 15): verdict = "Lagging Behind"
        elif current_progress > (target + 15): verdict = "Too Fast"
        else: verdict = "On Track"
        
        cursor.execute("""
            INSERT INTO teaching_progress 
            (faculty_id, week_number, teacher_completion_pct, student_avg_pct, class_verdict)
            VALUES (?, ?, ?, ?, ?)
        """, (fid, week, current_progress, student_view, verdict))
        
    count += 1

conn.commit()
conn.close()

print(f"✅ SUCCESS! Generated unique teaching profiles for {count} faculty members.")
print("👉 Restart Streamlit. Everyone now has a unique graph!")
