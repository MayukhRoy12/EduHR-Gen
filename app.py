import streamlit as st
import pandas as pd
import db_utils as db
import pdf_utils as pdf_gen
import email_utils
import auth_utils as auth
import chat_utils
import base64
import random

# ==========================================
# ⚙️ PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="EduHR-Gen Portal", layout="wide", page_icon="🎓")

# --- CUSTOM BACKGROUND ---
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
# 🔐 AUTHENTICATION LAYER
# ==========================================
auth.login()
auth.logout()

current_role = st.session_state["role"] # "HOD" or "Faculty"
user_id = st.session_state["user_id"]

st.title("🎓 EduHR-Gen: Academic HR Assistant")

# ==========================================
# 👤 SIDEBAR & USER SELECTION
# ==========================================
st.sidebar.header("User Panel")
st.sidebar.markdown(f"**Logged in as:** {current_role}")

faculty_names = db.get_faculty_names()

if current_role == "HOD":
    # HOD can search and select ANY faculty member
    selected_faculty = st.sidebar.selectbox("Select Faculty Member", faculty_names['name'])
    try:
        faculty_id = faculty_names[faculty_names['name'] == selected_faculty]['faculty_id'].values[0]
    except:
        faculty_id = 101 # Fallback
else:
    # Faculty is locked to their OWN ID
    faculty_id = user_id
    try:
        my_name = faculty_names[faculty_names['faculty_id'] == faculty_id]['name'].values[0]
        st.sidebar.info(f" Viewing Profile: **{my_name}**")
        selected_faculty = my_name
    except IndexError:
        st.error("❌ Error: Your Faculty ID was not found in the database.")
        st.stop()

# ==========================================
# 📑 TABS LOGIC (FIXED)
# ==========================================
if current_role == "HOD":
    # HOD sees 7 Tabs
    tab_names = [
        "📝 Leave Portal", 
        "📊 Feedback Analytics", 
        "⭐ Sentiment AI", 
        "📈 Performance", 
        "🔒 HOD Dashboard", 
        "📚 Teaching Tracker", 
        "💬 AI Assistant"
    ]
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(tab_names)

else:
    # Faculty sees 5 Tabs
    tab_names = [
        "📝 Leave Portal", 
        "📊 Feedback Analytics", 
        "⭐ Sentiment AI", 
        "📈 Performance", 
        "📚 Teaching Tracker"
    ]
    t1, t2, t3, t4, t6 = st.tabs(tab_names)
    t5 = None 
    t7 = None 

# ==========================================
# 📝 TAB 1: LEAVE PORTAL
# ==========================================
with t1:
    st.subheader(f"Leave Application for {selected_faculty}")
    col1, col2 = st.columns([1, 2], gap="medium")
    
    # 1. BALANCE CHECK
    with col1:
        st.info("📊 Current Leave Balance")
        balance = db.get_leave_balance(faculty_id)
        st.dataframe(balance, hide_index=True, use_container_width=True)

    # 2. APPLY FORM
    with col2:
        st.warning("📝 New Leave Request")
        email_needed = st.toggle("📧 Generate Email Draft for HOD?", value=False)
        
        with st.form("leave_form"):
            c_form1, c_form2 = st.columns(2)
            l_type = c_form1.selectbox("Leave Type", ["CL", "SL", "EL", "OD"])
            days = c_form2.number_input("Days Requested", min_value=1, max_value=30)
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

    st.divider()
    st.subheader("📜 My Leave History")
    history = db.get_leave_history(faculty_id)
    
    def color_status(val):
        color = 'orange' if val == 'Pending' else ('green' if val == 'Approved' else 'red')
        return f'color: {color}; font-weight: bold'

    if not history.empty:
        st.dataframe(history.style.applymap(color_status, subset=['status']), use_container_width=True)
    else:
        st.write("No leave records found.")

# ==========================================
# 📊 TAB 2: FEEDBACK ANALYTICS
# ==========================================
with t2:
    st.subheader("📊 Student Feedback Analysis")
    feed_df = db.get_student_feedback(faculty_id)
    
    if feed_df.empty:
        st.info("No feedback data available for this faculty.")
    else:
        avg_rating = feed_df['rating'].mean()
        total_reviews = len(feed_df)
        
        m1, m2 = st.columns(2)
        m1.metric("Average Rating", f"{avg_rating:.1f} / 5.0")
        m2.metric("Total Reviews", total_reviews)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Rating Distribution")
            st.bar_chart(feed_df['rating'].value_counts())
        with c2:
            st.markdown("#### Parameter Scores")
            scores = feed_df[['teaching_clarity_score', 'engagement_score', 'pace_score']].mean()
            st.line_chart(scores)

        st.divider()
        st.markdown("### 📝 All Student Comments")
        
        display_df = feed_df[['course_name', 'rating', 'feedback_comment', 'sentiment_label']]
        
        def color_sentiment(val):
            if val == 'Positive': return 'color: green'
            elif val == 'Negative': return 'color: red'
            else: return 'color: orange'

        st.dataframe(
            display_df.style.applymap(color_sentiment, subset=['sentiment_label']),
            use_container_width=True,
            height=400,
            column_config={
                "course_name": "Course",
                "rating": st.column_config.NumberColumn("Stars", format="%d ⭐"),
                "feedback_comment": "Student Comment",
                "sentiment_label": "AI Sentiment"
            }
        )

# ==========================================
# ⭐ TAB 3: SENTIMENT AI
# ==========================================
with t3:
    st.subheader("🤖 AI Sentiment Analysis")
    feed_df = db.get_student_feedback(faculty_id)
    if not feed_df.empty:
        sentiment_counts = feed_df['sentiment_label'].value_counts()
        st.bar_chart(sentiment_counts)
        
        st.divider()
        st.markdown("### 🗣️ AI Summarized Insights")
        with st.expander("View Top Positive Comments"):
            pos_comments = feed_df[feed_df['sentiment_label'] == 'Positive']['feedback_comment'].head(5)
            for c in pos_comments: st.success(f"- {c}")
        with st.expander("View Critical Feedback"):
            neg_comments = feed_df[feed_df['sentiment_label'] == 'Negative']['feedback_comment'].head(5)
            for c in neg_comments: st.error(f"- {c}")
    else:
        st.write("No data for analysis.")

# ==========================================
# 📈 TAB 4: PERFORMANCE APPRAISAL
# ==========================================
with t4:
    st.subheader("🏆 Annual Performance Appraisal")
    if st.button("🚀 Calculate Performance Score"):
        score_data = db.calculate_appraisal_score(faculty_id)
        st.balloons()
        c1, c2 = st.columns([1, 2])
        c1.metric("Final Score", f"{score_data['total']}/100")
        c2.json(score_data['breakdown'])
        
        pdf_file = pdf_gen.generate_appraisal_pdf(faculty_id)
        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ Download Official Report (PDF)", f, file_name=pdf_file, mime="application/pdf")

# ==========================================
# 🔒 TAB 5: HOD DASHBOARD (HOD ONLY)
# ==========================================
if current_role == "HOD" and t5:
    with t5:
        st.subheader("🔒 Head of Department (HOD) Approval Portal")
        col_actions, col_history = st.columns([1.5, 1], gap="large")
        
        with col_actions:
            st.markdown("### ⏳ Pending Actions")
            pending_leaves = db.get_pending_leaves()
            
            if pending_leaves.empty:
                st.success("✅ No pending requests.")
            else:
                st.markdown("#### ⚡ Bulk Actions")
                b1, b2 = st.columns(2)
                if b1.button("✅ Approve ALL", use_container_width=True):
                    count = db.update_all_pending_leaves("Approved")
                    st.success(f"Approved {count} requests!")
                    st.rerun()
                if b2.button("❌ Reject ALL", use_container_width=True):
                    count = db.update_all_pending_leaves("Rejected")
                    st.error(f"Rejected {count} requests.")
                    st.rerun()
                
                st.divider()
                st.markdown("#### 👤 Individual Review")
                email_enabled = st.toggle("📧 Generate Email Notification?", value=True)
                
                for index, row in pending_leaves.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{row['name']}** requests **{row['days_requested']} days** ({row['type']})")
                        c1, c2 = st.columns(2)
                        if c1.button("Approve", key=f"app_{row['leave_id']}"):
                            db.update_leave_status(row['leave_id'], "Approved")
                            if email_enabled:
                                draft = email_utils.generate_leave_email(row['name'], row['type'], row['days_requested'], "Approved")
                                st.code(draft)
                                if st.button("Done", key=f"d_{row['leave_id']}"): st.rerun()
                            else: st.rerun()
                        if c2.button("Reject", key=f"rej_{row['leave_id']}"):
                            db.update_leave_status(row['leave_id'], "Rejected")
                            st.rerun()

        with col_history:
            st.markdown("### 📜 Decision History")
            history_df = db.get_all_past_leaves()
            if not history_df.empty:
                def highlight_status(val):
                    return f'background-color: {"#d4edda" if val=="Approved" else "#f8d7da"}'
                st.dataframe(history_df.style.applymap(highlight_status, subset=['status']), hide_index=True)

# ==========================================
# 📚 TAB 6: TEACHING TRACKER
# ==========================================
with t6:
    st.subheader("📈 Syllabus Coverage & Recovery Plan")
    fid_clean = int(faculty_id)
    progress_df = db.get_teaching_progress(fid_clean)
    
    if progress_df.empty:
        with st.spinner("⚙️ Generating unique teaching profile..."):
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teaching_progress (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT, faculty_id INTEGER, week_number INTEGER,
                    teacher_completion_pct INTEGER, student_avg_pct INTEGER, class_verdict TEXT
                )
            """)
            
            persona = random.choice(['fast', 'consistent', 'consistent', 'slow', 'struggling'])
            if persona == 'fast': base, var = 10, 2
            elif persona == 'consistent': base, var = 8, 1
            else: base, var = 4, 3
            
            curr = 0
            for w in range(1, 13):
                curr += max(0, base + random.randint(-var, var))
                if curr > 100: curr = 100
                verdict = "On Track"
                if curr < (w*8 - 15): verdict = "Lagging Behind"
                elif curr > (w*8 + 15): verdict = "Too Fast"
                cursor.execute("INSERT INTO teaching_progress (faculty_id, week_number, teacher_completion_pct, student_avg_pct, class_verdict) VALUES (?,?,?,?,?)",
                               (fid_clean, w, curr, max(0, curr-random.randint(0,10)), verdict))
            conn.commit()
            conn.close()
            st.rerun()
    else:
        c_filt1, c_filt2 = st.columns([1, 2])
        view_mode = c_filt1.radio("View Mode:", ["Cumulative Trend", "Single Week Snapshot"])
        sel_week = c_filt2.slider("Select Week", 1, 12, 12)
        
        if view_mode == "Cumulative Trend":
            display_df = progress_df[progress_df['week_number'] <= sel_week]
            current_data = display_df.iloc[-1]
        else:
            display_df = progress_df[progress_df['week_number'] == sel_week]
            current_data = display_df.iloc[0] if not display_df.empty else None
            
        if current_data is not None:
            comp = current_data['teacher_completion_pct']
            m1, m2, m3 = st.columns(3)
            m1.metric("Week", f"Week {current_data['week_number']}")
            m2.metric("Completed", f"{comp}%")
            
            target = current_data['week_number'] * 8
            status = "On Track"
            color = "green"
            if comp < (target - 10): status, color = "Lagging Behind", "red"
            elif comp > (target + 10): status, color = "Ahead of Schedule", "blue"
            
            m3.markdown(f"**Status:** :{color}[{status}]")
            
            st.divider()
            if view_mode == "Cumulative Trend":
                st.line_chart(display_df.set_index("week_number")[['teacher_completion_pct', 'student_avg_pct']])
            else:
                chart_data = pd.DataFrame({
                    "Source": ["Teacher Claim", "Student View"],
                    "Completion": [comp, current_data['student_avg_pct']]
                }).set_index("Source")
                st.bar_chart(chart_data)

# ==========================================
# ==========================================
# 💬 TAB 7: AI DATA ASSISTANT (HOD ONLY)
# ==========================================
if current_role == "HOD" and t7:
    with t7:
        st.subheader("🧠 Chat with your HR Data (Powered by Gemini)")
        st.markdown("Ask complex questions about faculty, leaves, or feedback.")
        
        # 1. API Key Input (Updated with your NEW Key)
        if "gemini_key" not in st.session_state:
            # ✅ Your NEW Key is now the default here:
            st.session_state["gemini_key"] = "AIzaSyBwHUWjDrbGBpvIAMWQnncW7UOcGnB_Ddk"
            
        api_key = st.text_input("🔑 Enter Google Gemini API Key", 
                                value=st.session_state["gemini_key"], 
                                type="password")
        
        if api_key:
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Ask a question about your database..."):
                st.chat_message("user").markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.spinner("🤖 Analyzing Database..."):
                    # This calls the smart function that tries multiple models
                    response = chat_utils.ask_gemini(api_key, prompt)
                    
                    st.chat_message("assistant").markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.warning("⚠️ Please enter a valid Gemini API Key to start.")
