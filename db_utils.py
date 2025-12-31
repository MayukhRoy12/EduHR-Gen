import sqlite3
import pandas as pd
import os

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "academic_hr.db")

print(f"🔌 CONNECTING TO DATABASE AT: {DB_NAME}")

def get_connection():
    return sqlite3.connect(DB_NAME)

# --- READ OPERATIONS ---
def get_faculty_names():
    conn = get_connection()
    df = pd.read_sql("SELECT faculty_id, name FROM faculty_master", conn)
    conn.close()
    return df

def get_faculty_profile(faculty_id):
    conn = get_connection()
    # FIX: Force ID to be a standard integer
    fid = int(faculty_id)
    df = pd.read_sql("SELECT * FROM faculty_master WHERE faculty_id = ?", conn, params=(fid,))
    conn.close()
    return df

def get_leave_history(faculty_id):
    conn = get_connection()
    fid = int(faculty_id)
    df = pd.read_sql("SELECT * FROM leave_records WHERE faculty_id = ?", conn, params=(fid,))
    conn.close()
    return df

# --- CREATE OPERATIONS ---
def apply_leave(faculty_id, leave_type, days):
    conn = get_connection()
    cursor = conn.cursor()
    fid = int(faculty_id)
    
    cursor.execute("SELECT MAX(leave_id) FROM leave_records")
    next_id = (cursor.fetchone()[0] or 0) + 1
    
    cursor.execute("""
        INSERT INTO leave_records (leave_id, faculty_id, type, days_requested, status) 
        VALUES (?, ?, ?, ?, 'Pending')
    """, (next_id, fid, leave_type, days))
    
    conn.commit()
    conn.close()
    return True

# --- FEEDBACK ANALYTICS ---
def get_faculty_feedback(faculty_id):
    conn = get_connection()
    fid = int(faculty_id)
    
    query = """
        SELECT course_name, rating, feedback_comment, 
               sentiment_label, teaching_clarity_score, 
               engagement_score, pace_score 
        FROM student_feedback 
        WHERE faculty_id = ?
    """
    df = pd.read_sql(query, conn, params=(fid,))
    conn.close()
    return df

# --- WEEK 9: APPRAISAL ENGINE ---
def calculate_appraisal_score(faculty_id):
    """
    Calculates a weighted score (0-100) based on:
    1. Feedback (50%): Avg Rating * 20
    2. Research (30%): (Papers * 5) + (Patents * 10) (Capped at 30)
    3. Attendance (20%): Starts at 20, minus 2 per leave day
    """
    conn = get_connection()
    fid = int(faculty_id)
    
    # 1. GET FEEDBACK SCORE (50%)
    feedback_score = 0
    f_df = pd.read_sql("SELECT rating FROM student_feedback WHERE faculty_id = ?", conn, params=(fid,))
    if not f_df.empty:
        avg_rating = f_df['rating'].mean() # e.g., 4.5
        feedback_score = avg_rating * 10 # Convert 5-scale to 50-scale
    
    # 2. GET RESEARCH SCORE (30%)
    research_score = 0
    r_df = pd.read_sql("SELECT * FROM research_records WHERE faculty_id = ?", conn, params=(fid,))
    if not r_df.empty:
        papers = r_df.iloc[0]['publications_count']
        patents = r_df.iloc[0]['patents_count']
        
        # Scoring Logic: 5 points per paper, 10 per patent
        raw_r_score = (papers * 5) + (patents * 10)
        research_score = min(raw_r_score, 30) # Cap at max 30 points
        
    # 3. GET ATTENDANCE SCORE (20%)
    attendance_score = 20 # Everyone starts with full points
    l_df = pd.read_sql("SELECT days_requested FROM leave_records WHERE faculty_id = ? AND status='Approved'", conn, params=(fid,))
    if not l_df.empty:
        total_leaves = l_df['days_requested'].sum()
        penalty = total_leaves * 2 # Deduct 2 points per leave day
        attendance_score = max(0, 20 - penalty) # Cannot go below 0

    conn.close()
    
    total_score = feedback_score + research_score + attendance_score
    
    return {
        "total": round(total_score, 1),
        "breakdown": {
            "Feedback (50%)": round(feedback_score, 1),
            "Research (30%)": round(research_score, 1),
            "Attendance (20%)": round(attendance_score, 1)
        }
    }

# --- WEEK 5-6 ADDITIONS: APPROVAL WORKFLOW ---
def get_pending_leaves():
    conn = get_connection()
    # Join with faculty table to get names
    query = """
        SELECT l.leave_id, f.name, l.type, l.days_requested, l.status 
        FROM leave_records l
        JOIN faculty_master f ON l.faculty_id = f.faculty_id
        WHERE l.status = 'Pending'
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def update_leave_status(leave_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leave_records SET status = ? WHERE leave_id = ?", (new_status, leave_id))
    conn.commit()
    conn.close()
    return True

# --- WEEK 9-10: TEACHING TRACKER ---
def get_teaching_progress(faculty_id):
    conn = get_connection()
    # Now filters by faculty_id
    query = "SELECT * FROM teaching_progress WHERE faculty_id = ? ORDER BY week_number ASC"
    df = pd.read_sql(query, conn, params=(faculty_id,))
    conn.close()
    return df

# --- WEEK 5-6: SMART LEAVE BALANCE (NEW FEATURE) ---
def get_leave_balance(faculty_id, leave_type):
    """
    Calculates remaining leaves by subtracting (Approved + Pending) from the Total Limit.
    """
    # 1. Define Academic Limits (Standard per year)
    LIMITS = {
        "CL": 12,  # Casual Leave
        "SL": 10,  # Sick Leave
        "EL": 15,  # Earned Leave
        "OD": 10   # On Duty
    }
    
    # Get the max limit for the selected type (Default to 0 if unknown)
    max_limit = LIMITS.get(leave_type, 0)
    
    conn = get_connection()
    fid = int(faculty_id)
    
    # 2. Calculate Used Leaves
    # We count 'Pending' leaves too, so they can't double-apply!
    query = """
        SELECT SUM(days_requested) 
        FROM leave_records 
        WHERE faculty_id = ? AND type = ? AND status IN ('Approved', 'Pending')
    """
    cursor = conn.cursor()
    result = cursor.execute(query, (fid, leave_type)).fetchone()[0]
    conn.close()
    
    # If result is None (no leaves taken yet), used is 0
    used = result if result else 0
    
    # 3. Calculate Balance
    remaining = max_limit - used
    return max(0, remaining)
# --- NEW: GRANT BONUS LEAVES ---
def grant_bonus_leave(faculty_id, leave_type, days):
    """HOD adds extra days to a faculty's limit."""
    conn = get_connection()
    cursor = conn.cursor()
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    cursor.execute("""
        INSERT INTO bonus_leaves (faculty_id, leave_type, extra_days, granted_date)
        VALUES (?, ?, ?, ?)
    """, (int(faculty_id), leave_type, days, today))
    
    conn.commit()
    conn.close()
    return True

# --- UPDATED: SMART LEAVE BALANCE ---
def get_leave_balance(faculty_id, leave_type):
    """
    Calculates remaining leaves: (Standard Limit + Bonus) - Used
    """
    # 1. Define Standard Limits
    LIMITS = { "CL": 12, "SL": 10, "EL": 15, "OD": 10 }
    standard_limit = LIMITS.get(leave_type, 0)
    
    conn = get_connection()
    fid = int(faculty_id)
    
    # 2. Fetch BONUS Limit (New Step)
    cursor = conn.cursor()
    bonus_result = cursor.execute("""
        SELECT SUM(extra_days) FROM bonus_leaves 
        WHERE faculty_id = ? AND leave_type = ?
    """, (fid, leave_type)).fetchone()[0]
    
    bonus_limit = bonus_result if bonus_result else 0
    
    # 3. Calculate Used Leaves
    query = """
        SELECT SUM(days_requested) 
        FROM leave_records 
        WHERE faculty_id = ? AND type = ? AND status IN ('Approved', 'Pending')
    """
    used_result = cursor.execute(query, (fid, leave_type)).fetchone()[0]
    used = used_result if used_result else 0
    
    conn.close()
    
    # 4. Final Math
    total_limit = standard_limit + bonus_limit
    remaining = total_limit - used
    
    return max(0, remaining)
