import sqlite3
import pandas as pd
import os

# --- SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")
OUTPUT_CSV = os.path.join(BASE_DIR, "Faculty_Login_Credentials.csv")

conn = sqlite3.connect(DB_FILE)
query = "SELECT faculty_id, name, designation, department FROM faculty_master ORDER BY faculty_id ASC"
df = pd.read_sql(query, conn)
conn.close()

print(f"🚀 Processing {len(df)} faculty records...")

# --- GENERATE DATA ---
usernames = []
seen_usernames = {}

for name in df['name']:
    clean_name = name.replace("Dr.", "").replace("Prof.", "").strip()
    parts = clean_name.split(" ")
    
    # Username Logic (First_Last)
    if len(parts) > 1:
        base_username = f"{parts[0].lower()}_{parts[-1].lower()}"
    else:
        base_username = parts[0].lower()
    
    # Collision Handling
    if base_username in seen_usernames:
        count = seen_usernames[base_username]
        final_username = f"{base_username}{count}"
        seen_usernames[base_username] += 1
    else:
        final_username = base_username
        seen_usernames[base_username] = 1
        
    usernames.append(final_username)

# Add to DataFrame
df['Username'] = usernames
df['Password'] = "1234" # Fixed Password
df['Role'] = "Faculty"

# Reorder
export_df = df[['faculty_id', 'name', 'Username', 'Password', 'Role', 'department']]
export_df.to_csv(OUTPUT_CSV, index=False)

print(f"✅ SUCCESS! Updated CSV file: {OUTPUT_CSV}")
