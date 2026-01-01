import sqlite3
import pandas as pd
import os
from datetime import datetime

# --- DATABASE CONNECTION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")

def get_connection():
    return sqlite3.connect(DB_FILE)

# --- FACULTY DATA ---
def get_faculty_names():
    conn = get_connection()
    df = pd.read_sql("SELECT faculty_id, name FROM faculty_master", conn)
    conn.close()
    return df

def get_faculty_profile(faculty_id):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM faculty_master WHERE faculty_id=?", conn, params=(faculty_id,))
    conn.close()
    return df

# --- LEAVE MANAGEMENT (FIXED) ---
def get_leave_balance(faculty_id, leave_type=None):
    """
    If leave_type is None -> Returns a DataFrame (Table) of ALL balances.
    If leave_type is provided (e.g. 'CL') -> Returns an Integer (Available Balance).
    """
    conn = get_connection()
    
    # 1. Define Standard Quotas
    quota = {'CL': 12, 'SL': 10, 'EL': 15, 'OD': 5}
    
    # 2. Add Bonus Leaves (Extensions)
    try:
        bonus_query = "SELECT leave_type, SUM(extra_days) as extra FROM bonus_leaves WHERE faculty_id=? GROUP BY leave_type"
        bonus_df = pd.read_sql(bonus_query, conn, params=(faculty_id,))
        for _, row in bonus_df.iterrows():
            if row['leave_type'] in quota:
                quota[row['leave_type']] += row['extra']
    except:
        pass # Table might not exist yet

    # 3. Calculate Used Leaves (Approved only)
    used_query = "SELECT type, SUM(days_requested) as used FROM leave_records WHERE faculty_id=? AND status='Approved' GROUP BY type"
    used_df = pd.read_sql(used_query, conn, params=(faculty_id,))
    used_dict = dict(zip(used_df['type'], used_df['used']))
    
    conn.close()

    # 4. Build Balance Data
    balance_data = []
    for l_type, total_allowed in quota.items():
        consumed = used_dict.get(l_type, 0)
        remaining = total_allowed - consumed
        balance_data.append({
            "Leave Type": l_type, 
            "Total Allocated": total_allowed, 
            "Used": consumed, 
            "Available Balance": remaining
        })
    
    # 5. Return Logic
    if leave_type:
        # Validation Mode: Return Number
        for item in balance_data:
            if item["Leave Type"] == leave_type:
                return item["Available Balance"]
        return 0 
    else:
        # Dashboard Mode: Return Table
        return pd.DataFrame(balance_data)

def apply_for_leave(faculty_id, leave_type, days):
    # 1. Check Balance using the validated function
    balance = get_leave_balance(faculty_id, leave_type)
    
    if days > balance:
        return False, f"❌ Insufficient Balance! You have {balance} {leave_type} remaining."
    
    # 2. Submit Request
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO leave_records (faculty_id, type, days_requested, status) VALUES (?, ?, ?, 'Pending')", 
                   (faculty_id, leave_type, days))
    conn.commit()
    conn.close()
    return True, "✅ Leave request submitted successfully!"

def get_leave_history(faculty_id):
    conn = get_connection()
    query = "SELECT type, days_requested, status FROM leave_records WHERE faculty_id=? ORDER BY leave_id DESC"
    df = pd.read_sql(query, conn, params=(faculty_id,))
    conn.close()
    return df

# --- HOD FUNCTIONS ---
def get_pending_leaves():
    conn = get_connection()
    query = """
        SELECT l.leave_id, f.name, l.type, l.days_requested, l.status
        FROM leave_records l
        JOIN faculty_master f ON l.faculty_id = f.faculty_id
        WHERE l.status = 'Pending'
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def update_leave_status(leave_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leave_records SET status=? WHERE leave_id=?", (status, leave_id))
    conn.commit()
    conn.close()

def update_all_pending_leaves(new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leave_records SET status = ? WHERE status = 'Pending'", (new_status,))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def get_all_past_leaves():
    conn = get_connection()
    query = """
        SELECT f.name, l.type, l.days_requested, l.status
        FROM leave_records l
        JOIN faculty_master f ON l.faculty_id = f.faculty_id
        WHERE l.status != 'Pending'
        ORDER BY l.leave_id DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def grant_bonus_leave(faculty_id, leave_type, days):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bonus_leaves (faculty_id, leave_type, extra_days, granted_date) VALUES (?, ?, ?, ?)",
                   (faculty_id, leave_type, days, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

# --- STUDENT FEEDBACK ---
def get_student_feedback(faculty_id):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM student_feedback WHERE faculty_id=?", conn, params=(faculty_id,))
    conn.close()
    return df

# --- PERFORMANCE APPRAISAL ---
def calculate_appraisal_score(faculty_id):
    conn = get_connection()
    
    # 1. Feedback Score (Max 50)
    feed_df = pd.read_sql("SELECT rating FROM student_feedback WHERE faculty_id=?", conn, params=(faculty_id,))
    if not feed_df.empty:
        avg_rating = feed_df['rating'].mean()
        feedback_score = (avg_rating / 5) * 50
    else:
        feedback_score = 0
        
    # 2. Research Score (Max 30)
    res_df = pd.read_sql("SELECT publications_count, patents_count FROM research_records WHERE faculty_id=?", conn, params=(faculty_id,))
    if not res_df.empty:
        pubs = res_df.iloc[0]['publications_count']
        pats = res_df.iloc[0]['patents_count']
        research_score = min(30, (pubs * 5) + (pats * 10))
    else:
        research_score = 0
        
    # 3. Attendance (Max 20) -> Mock logic
    attendance_score = 18 
    
    conn.close()
    
    total = int(feedback_score + research_score + attendance_score)
    return {
        "total": total,
        "breakdown": {
            "Feedback (50%)": round(feedback_score, 1),
            "Research (30%)": round(research_score, 1),
            "Attendance (20%)": attendance_score
        }
    }

# --- TEACHING TRACKER ---
def get_teaching_progress(faculty_id):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM teaching_progress WHERE faculty_id=?", conn, params=(faculty_id,))
    conn.close()
    return df
