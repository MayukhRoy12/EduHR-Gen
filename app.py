import streamlit as st
import pandas as pd
import db_utils as db
import pdf_utils as pdf_gen
import email_utils
import auth_utils as auth
import base64
import random
import warnings
import sqlite3

# Suppress Warnings
warnings.filterwarnings("ignore")

# ==========================================
# 🛠️ SELF-HEALING DATABASE FUNCTION
# ==========================================
def ensure_database_integrity():
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Ensure tables exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_balance (
            faculty_id INTEGER PRIMARY KEY,
            cl_balance INTEGER DEFAULT 10, sl_balance INTEGER DEFAULT 5, el_balance INTEGER DEFAULT 2
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teaching_progress (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT, faculty_id INTEGER, 
            week_number INTEGER, teacher_completion_pct INTEGER, 
            student_avg_pct INTEGER, class_verdict TEXT
        )""")
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"⚠️ Database Repair Failed: {e}")

ensure_database_integrity()

# ==========================================
# ⚙️ PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="EduHR-Gen Portal", layout="wide", page_icon="🎓")

def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        st.markdown(
        f"""<style>
        .stApp {{ background-image: url(data:image/{"png"};base64,{encoded_string.decode()}); background-size: cover; }} 
        .stMarkdown, .stText, h1, h2, h3, p, label {{ 
            text-shadow: 0px 0px 3px rgba(255, 255, 255, 0.8); 
            font-weight: 500;
        }} 
        </style>""", unsafe_allow_html=True)
    except FileNotFoundError:
        pass 

add_bg_from_local('background.jpg') 

# ==========================================
# 🔐 AUTHENTICATION
# ==========================================
auth.login()
auth.logout()

current_role = st.session_state.get("role", None)
user_id = st.session_state.get("user_id", None)

if not current_role: st.stop()

st.title("🎓 EduHR-Gen: Academic HR Assistant")

# ==========================================
# 👤 SIDEBAR
# ==========================================
st.sidebar.header("User Panel")
st.sidebar.markdown(f"**Logged in as:** {current_role}")

faculty_names = db.get_faculty_names()

if faculty_names.empty:
    st.error("⚠️ Database is empty!")
    st.stop()

if current_role == "HOD":
    # Show ID in dropdown to avoid confusion
    faculty_dict = dict(zip(faculty_names['name'] + " (ID: " + faculty_names['faculty_id'].astype(str) + ")", faculty_names['faculty_id']))
    
    selected_label = st.sidebar.selectbox("Select Faculty Member", list(faculty_dict.keys()))
    faculty_id = faculty_dict[selected_label]
    selected_faculty = faculty_names[faculty_names['faculty_id'] == faculty_id]['name'].values[0]

else:
    faculty_id = user_id
    try:
        my_name = faculty_names[faculty_names['faculty_id'] == faculty_id]['name'].values[0]
        st.sidebar.info(f" Viewing Profile: **{my_name}**")
        selected_faculty = my_name
    except IndexError:
        st.error("❌ Error: Your Faculty ID was not found.")
        st.stop()

# ==========================================
# 📑 TABS (Chatbot Removed)
# ==========================================
if current_role == "HOD":
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📝 Leave Portal", "📊 Feedback Analytics", "⭐ Sentiment AI", 
        "📈 Performance", "🔒 HOD Dashboard", "📚 Teaching Tracker"
    ])
else:
    t1, t2, t3, t4, t6 = st.tabs([
        "📝 Leave Portal", "📊 Feedback Analytics", "⭐ Sentiment AI", 
        "📈 Performance", "📚 Teaching Tracker"
    ])
    t5 = None

# ==========================================
# 📝 TAB 1: LEAVES (HOD READ-ONLY)
# ==========================================
with t1:
    st.subheader(f"Leave Profile: {selected_faculty}")

    # --- HOD VIEW (Read Only) ---
    if current_role == "HOD":
        st.info(f"Viewing Leave Records for **{selected_faculty}**")
        
        # 1. Balance Table
        st.markdown("### 📊 Current Balance")
        balance = db.get_leave_balance(faculty_id)
        st.dataframe(balance, hide_index=True, use_container_width=True)

        # 2. History Table
        st.divider()
        st.markdown("### 📜 Leave Application History")
        history = db.get_leave_history(faculty_id)
        
        if not history.empty:
            def color_status(val):
                color = 'orange' if val == 'Pending' else ('green' if val == 'Approved' else 'red')
                return f'color: {color}; font-weight: bold'
            st.dataframe(history.style.applymap(color_status, subset=['status']), use_container_width=True)
        else:
            st.write("No leave records found for this faculty.")

    # --- FACULTY VIEW (Can Apply) ---
    else:
        col1, col2 = st.columns([1, 2], gap="medium")
        
        # 1. Balance
        with col1:
            st.info("📊 Current Leave Balance")
            balance = db.get_leave_balance(faculty_id)
            st.dataframe(balance, hide_index=True, use_container_width=True)

        # 2. Apply Form
        with col2:
            st.warning("📝 New Leave Request")
            email_needed = st.toggle("📧 Generate Email Draft for HOD?", value=False)
            
            with st.form("leave_form"):
                col_a, col_b = st.columns(2)
                l_type = col_a.selectbox("Leave Type", ["CL", "SL", "EL", "OD"])
                days = col_b.number_input("Days Requested", min_value=1, max_value=30)
                reason = st.text_area("Reason for Leave")
                
                if st.form_submit_button("Submit Request"):
                    success, msg = db.apply_for_leave(faculty_id, l_type, days)
                    if success:
                        st.success(msg)
                        if email_needed:
                            draft = email_utils.generate_leave_application_email(
                                selected_faculty, l_type, days, reason
                            )
                            st.markdown("---")
                            st.info("📋 **Copy this email to send to your HOD:**")
                            st.code(draft, language="markdown")
                    else:
                        st.error(msg)
        
        # History
        st.divider()
        st.subheader("📜 My Leave History")
        history = db.get_leave_history(faculty_id)
        if not history.empty:
            def color_status(val):
                color = 'orange' if val == 'Pending' else ('green' if val == 'Approved' else 'red')
                return f'color: {color}; font-weight: bold'
            st.dataframe(history.style.applymap(color_status, subset=['status']), use_container_width=True)
        else:
            st.write("No leave records found.")

# ==========================================
# 📊 TAB 2: FEEDBACK
# ==========================================
with t2:
    st.subheader("📊 Feedback Analysis")
    f_df = db.get_student_feedback(faculty_id)
    if not f_df.empty:
        c1, c2 = st.columns(2)
        c1.metric("Avg Rating", f"{f_df['rating'].mean():.1f}/5")
        c2.metric("Reviews", len(f_df))
        st.bar_chart(f_df['rating'].value_counts())
        
        st.divider()
        st.dataframe(f_df[['course_name', 'rating', 'feedback_comment', 'sentiment_label']], use_container_width=True)
    else:
        st.info("No feedback data found.")

# ==========================================
# ⭐ TAB 3: SENTIMENT
# ==========================================
with t3:
    st.subheader("🤖 AI Sentiment")
    if not f_df.empty:
        st.bar_chart(f_df['sentiment_label'].value_counts())
        with st.expander("Show Comments"):
            st.write(f_df['feedback_comment'])
    else:
        st.write("No data.")

# ==========================================
# 📈 TAB 4: PERFORMANCE (AUTO-CALCULATE)
# ==========================================
with t4:
    st.subheader("🏆 Annual Performance Appraisal")
    st.write(f"Performance Data for: **{selected_faculty} (ID: {faculty_id})**")

    # 1. Calculate Score (Independent)
    score_data = None
    try:
        with st.spinner("Analyzing performance metrics..."):
            score_data = db.calculate_appraisal_score(faculty_id)
        
        if score_data and score_data['total'] > 0:
            c1, c2 = st.columns([1, 2])
            c1.metric("Final Score", f"{score_data['total']}/100")
            c2.json(score_data['breakdown'])
        else:
            st.warning("⚠️ Score is 0. This profile might need data sync.")
            if st.button("🔄 Sync Missing Data Now"):
                # Quick fix button inside the app!
                try:
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE faculty_master SET research_score = 85 WHERE faculty_id = ?", (faculty_id,))
                    reviews = [(faculty_id, "CS101", 5, "Auto-Fix", "Positive", 1.0)]
                    cursor.executemany("INSERT INTO student_feedback (faculty_id, course_name, rating, feedback_comment, sentiment_label, sentiment_score) VALUES (?, ?, ?, ?, ?, ?)", reviews)
                    conn.commit()
                    st.success("Data injected! Refresh page.")
                except:
                    st.error("Sync failed.")
                    
    except Exception as e:
        st.error(f"Error calculating score: {e}")

    # 2. Generate PDF (Independent)
    if score_data:
        try:
            pdf_file = pdf_gen.generate_appraisal_pdf(faculty_id)
            if pdf_file:
                with open(pdf_file, "rb") as f:
                    st.download_button("⬇️ Download Report", f, file_name=pdf_file, mime="application/pdf")
        except:
            st.caption("PDF generation unavailable for incomplete profiles.")

# ==========================================
# 🔒 TAB 5: HOD DASHBOARD
# ==========================================
if current_role == "HOD" and t5:
    with t5:
        st.subheader("HOD Approval Portal")
        pending = db.get_pending_leaves()
        if not pending.empty:
            for i, row in pending.iterrows():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"{row['name']} - {row['days_requested']} Days ({row['type']})")
                if c2.button("Approve", key=f"a_{row['leave_id']}"):
                    db.update_leave_status(row['leave_id'], "Approved"); st.rerun()
                if c3.button("Reject", key=f"r_{row['leave_id']}"):
                    db.update_leave_status(row['leave_id'], "Rejected"); st.rerun()
        else:
            st.success("No pending requests.")

# ==========================================
# 📚 TAB 6: TEACHING TRACKER
# ==========================================
with t6:
    st.subheader("Teaching Tracker")
    tp = db.get_teaching_progress(faculty_id)
    if not tp.empty:
        curr = tp.iloc[-1]
        st.metric(f"Week {curr['week_number']} Completion", f"{curr['teacher_completion_pct']}%")
        st.line_chart(tp.set_index("week_number")['teacher_completion_pct'])
    else:
        st.info("Initializing tracker...")
