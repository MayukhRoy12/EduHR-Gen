import sqlite3
import pandas as pd

DB_NAME = "academic_hr.db"

# --- CORE UTILITY ( The "Bridge" ) ---
def get_connection():
    return sqlite3.connect(DB_NAME)

# --- READ OPERATIONS ( The "R" in CRUD ) ---
def get_faculty_names():
    """API to fetch list of faculty for login"""
    conn = get_connection()
    df = pd.read_sql("SELECT faculty_id, name FROM faculty_master", conn)
    conn.close()
    return df

def get_faculty_profile(faculty_id):
    """API to fetch full profile of a single faculty"""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM faculty_master WHERE faculty_id = ?", conn, params=(faculty_id,))
    conn.close()
    return df

def get_leave_history(faculty_id):
    """API to fetch leave records"""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM leave_records WHERE faculty_id = ?", conn, params=(faculty_id,))
    conn.close()
    return df

# --- CREATE/UPDATE OPERATIONS ( The "C" & "U" in CRUD ) ---
def apply_leave(faculty_id, leave_type, days):
    """API to Create a new leave request"""
    conn = get_connection()
    cursor = conn.cursor()
    # Simple logic to get next ID
    cursor.execute("SELECT MAX(leave_id) FROM leave_records")
    next_id = (cursor.fetchone()[0] or 0) + 1
    
    cursor.execute("""
        INSERT INTO leave_records (leave_id, faculty_id, type, days_requested, status) 
        VALUES (?, ?, ?, ?, 'Pending')
    """, (next_id, faculty_id, leave_type, days))
    
    conn.commit()
    conn.close()
    return True
