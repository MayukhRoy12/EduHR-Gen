import sqlite3
import os
import random

# --- SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("🚀 REDISTRIBUTING RESEARCH SCORES...")

# 1. Get all Faculty IDs
cursor.execute("SELECT faculty_id FROM faculty_master")
faculty_ids = [row[0] for row in cursor.fetchall()]
total_faculty = len(faculty_ids)

print(f"📊 Processing {total_faculty} faculty members...")

# 2. Shuffle them to make it random
random.shuffle(faculty_ids)

# 3. Define the Distribution (The Bell Curve)
# 15% High Performers (Score 30/30) -> Need 6+ papers
# 65% Average Performers (Score 10-25) -> Need 2-5 papers
# 20% Low Performers (Score 0-5) -> Need 0-1 papers

count_high = int(total_faculty * 0.15)
count_avg = int(total_faculty * 0.65)
count_low = total_faculty - count_high - count_avg

print(f"🎯 Target Distribution:")
print(f"   - Star Researchers (30/30): {count_high}")
print(f"   - Average Researchers:      {count_avg}")
print(f"   - No/Low Research (0-5):    {count_low}")

# 4. Apply the Updates
# --- GROUP A: STARS (30 pts) ---
for fid in faculty_ids[:count_high]:
    # Give them enough to hit the cap (6 to 12 papers)
    papers = random.randint(6, 12)
    patents = random.randint(0, 2)
    cursor.execute("UPDATE research_records SET publications_count=?, patents_count=? WHERE faculty_id=?", (papers, patents, fid))

# --- GROUP B: AVERAGE (10-25 pts) ---
start = count_high
end = count_high + count_avg
for fid in faculty_ids[start:end]:
    # Give them 2 to 5 papers
    papers = random.randint(2, 5)
    patents = 0
    cursor.execute("UPDATE research_records SET publications_count=?, patents_count=? WHERE faculty_id=?", (papers, patents, fid))

# --- GROUP C: LOW (0 pts) ---
for fid in faculty_ids[end:]:
    # Give them 0 or 1 paper
    papers = random.choice([0, 0, 0, 1]) # Mostly 0
    patents = 0
    cursor.execute("UPDATE research_records SET publications_count=?, patents_count=? WHERE faculty_id=?", (papers, patents, fid))

conn.commit()
conn.close()
print("✅ SUCCESS! Research scores have been realisticized.")
print("👉 Restart Streamlit to see the new variation in Tab 4.")
