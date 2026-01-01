import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")

conn = sqlite3.connect(DB_FILE)
df = pd.read_sql("SELECT faculty_id, name FROM faculty_master", conn)
conn.close()

print(df)
