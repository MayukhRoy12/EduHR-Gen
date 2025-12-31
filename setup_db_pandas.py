import pandas as pd
import sqlite3
import os

# 1. Setup Database Connection
db_filename = "academic_hr.db"
conn = sqlite3.connect(db_filename)
print(f"Connected to database: {db_filename}")

# 2. Define File Mappings (CSV File -> Table Name)
files_to_tables = {
    "faculty_dataset_(2).csv": "faculty_master",
    "Performance_dataset.csv": "performance_metrics",
    "leave_dataset_.csv": "leave_records",
    "feedback_dataset.csv": "student_feedback",
    "teaching_progress_dataset (1).csv": "teaching_progress"
}

# 3. Load and Insert Data
for csv_file, table_name in files_to_tables.items():
    try:
        # Read CSV using Pandas (It handles commas and headers automatically)
        df = pd.read_csv(csv_file)

        # --- Data Cleaning ---
        # Remove empty columns (like 'Unnamed: 11')
        df = df.dropna(axis=1, how='all')

        # Standardize Column Names:
        # Strip whitespace, replace spaces with underscores, remove special chars
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('%', 'pct').str.replace(r'[^\w]', '', regex=True)

        # Write to SQLite
        # if_exists='replace' ensures a fresh start each time you run this
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        print(f"✓ Created table '{table_name}' with {len(df)} records.")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{csv_file}'. Check the file name.")
    except Exception as e:
        print(f"❌ Error processing {csv_file}: {e}")

# 4. Verify Success
print("\n--- Verification: Previewing 'faculty_master' ---")
try:
    preview = pd.read_sql("SELECT * FROM faculty_master LIMIT 3", conn)
    print(preview[['faculty_id', 'name', 'department', 'designation']])
except Exception as e:
    print("Could not verify table creation.")

conn.close()
print(f"\nDatabase setup complete. File saved as '{db_filename}'")
