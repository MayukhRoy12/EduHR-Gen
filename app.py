import streamlit as st
import db_utils as db
import datetime
import pandas as pd
import pdf_utils
import email_utils
import ai_summary_utils

# --- PAGE SETUP ---
st.set_page_config(page_title="EduHR-Gen Portal", layout="wide")
st.title("🎓 EduHR-Gen: Academic HR Assistant")

# --- SIDEBAR: LOGIN SIMULATION ---
st.sidebar.header("Faculty Login")

try:
    faculty_data = db.get_faculty_names()
    
    if not faculty_data.empty:
        selected_name = st.sidebar.selectbox("Select Faculty Member", faculty_data['name'])
        
        # Find the ID associated with the selected name
        faculty_id = faculty_data[faculty_data['name'] == selected_name]['faculty_id'].values[0]
        
        # Attempt to get profile details for the email signature
        try:
            profile = db.get_faculty_profile(faculty_id) 
            dept = profile['department'] if 'department' in profile else "Department"
            desig = profile['designation'] if 'designation' in profile else "Faculty Member"
        except:
            dept = "Academic Department"
            desig = "Faculty"

        st.sidebar.success(f"Logged in as: {selected_name} (ID: {faculty_id})")
    else:
        st.error("Database is connected but empty.")
        st.stop()

except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()

# --- HELPER: AI EMAIL GENERATOR ---
def generate_email_draft(name, designation, department, leave_type, days, reason):
    today = datetime.date.today().strftime("%B %d, %Y")
    subject = f"Leave Application: {leave_type} - {name}"
    
    body = f"""
Subject: {subject}

Dear Head of Department,

I am writing to formally request **{leave_type}** for **{days} day(s)** starting from {today}.

**Reason for Leave:**
{reason}

I have ensured that my classes and responsibilities for this period are managed. I would be grateful for your approval.

Sincerely,

**{name}**
{designation}
{department}
    """
    return body

# MAIN TABS
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Apply for Leave", 
    "📜 My Leave History", 
    "📢 Student Feedback", 
    "🏆 Performance Appraisal",
    "🔒 HOD Dashboard",
    "📈 Teaching Tracker" 
])

# TAB 1: Apply for Leave (FIXED: Email Preview remains visible)
with tab1:
    st.subheader("Submit a Leave Request")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("leave_form"):
            st.markdown("### 1. Enter Leave Details")
            
            # Select Leave Type
            leave_type_selection = st.selectbox("Leave Type", ["CL (Casual Leave)", "SL (Sick Leave)", "EL (Earned Leave)", "OD (On Duty)"])
            leave_code = leave_type_selection.split()[0] 
            
            # 1. Get the balance from DB
            balance = db.get_leave_balance(faculty_id, leave_code)
            
            # 2. Display it
            if balance > 5:
                st.success(f"✅ Balance Remaining: {balance} days")
            elif balance > 0:
                st.warning(f"⚠️ Low Balance: Only {balance} days left")
            else:
                st.error(f"❌ No {leave_code} left! Balance: 0")
            
            # 3. Input Days
            days = st.number_input("Number of Days", min_value=1, max_value=30, value=1)
            
            # 4. VALIDATION
            is_valid = True
            if days > balance:
                st.error(f"⛔ ERROR: You cannot apply for {days} days. You only have {balance} {leave_code} remaining.")
                is_valid = False
            
            reason = st.text_area("Reason for Leave", placeholder="e.g., Attending International Conference...")
            
            # Submit Button
            submitted = st.form_submit_button("Generate Email & Submit")

    with col2:
        st.markdown("### 2. AI Email Preview")
        if submitted:
            if is_valid:
                # Generate Email
                email_draft = generate_email_draft(selected_name, desig, dept, leave_type_selection, days, reason)
                st.text_area("Auto-Generated Draft", value=email_draft, height=350)
                
                # Save to DB
                success = db.apply_leave(faculty_id, leave_code, days)
                if success:
                    st.success(f"✅ Success! {leave_code} request submitted.")
                    st.balloons()
                    # I removed st.rerun() here so the email stays on screen!
                    st.info("ℹ️ Your balance will update the next time you interact with the page.")
                else:
                    st.error("❌ Failed to save to database.")
            else:
                st.error("❌ Submission Blocked: Insufficient Leave Balance.")
        else:
            st.info("👋 Select a leave type to see your balance.")

# TAB 2: View History
with tab2:
    st.subheader("Your Application Status")
    history_df = db.get_leave_history(faculty_id)
    if not history_df.empty:
        st.dataframe(history_df[['leave_id', 'type', 'days_requested', 'status']], use_container_width=True)
    else:
        st.info("No leave records found.")

# TAB 3: Student Feedback Analytics
with tab3:
    st.subheader("📢 Student Feedback Analytics")
    
    # 1. Fetch Data
    feedback_df = db.get_faculty_feedback(faculty_id)
    
    if not feedback_df.empty:
        # Metrics
        avg_rating = feedback_df['rating'].mean()
        total_reviews = len(feedback_df)
        
        # Safe calculation for positive pct
        if total_reviews > 0:
            positive_count = len(feedback_df[feedback_df['sentiment_label'] == 'Positive'])
            positive_pct = (positive_count / total_reviews) * 100
        else:
            positive_pct = 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("⭐ Average Rating", f"{avg_rating:.2f}/5")
        m2.metric("📝 Total Reviews", total_reviews)
        m3.metric("😊 Positive Sentiment", f"{positive_pct:.1f}%")
        
        st.divider()
        
        # Charts
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Sentiment Distribution")
            st.bar_chart(feedback_df['sentiment_label'].value_counts())
        with c2:
            st.markdown("### Teaching Scores Breakdown")
            score_cols = ['teaching_clarity_score', 'engagement_score', 'pace_score']
            st.line_chart(feedback_df[score_cols].mean())

        # Comments
        st.markdown("### 💬 Recent Student Comments")
        st.dataframe(feedback_df[['course_name', 'rating', 'feedback_comment']], use_container_width=True)
        
        # --- NEW AI SUMMARY SECTION (Week 7-8 Requirement) ---
        st.divider()
        st.subheader("🤖 AI Feedback Intelligence")
        
        if st.button("Generate AI Summary & Recommendations", key="ai_summary_btn"):
            with st.spinner("Analyzing comments patterns..."):
                # Get list of comments and current rating
                comments = feedback_df['feedback_comment'].tolist()
                
                # Call the AI function
                summary_text, action_plan = ai_summary_utils.generate_feedback_insight(comments, avg_rating)
                
                # Display Summary
                st.success("Analysis Complete")
                st.markdown(f"### 📝 Executive Summary")
                st.write(summary_text)
                
                # Display Action Plan
                st.markdown(f"### 🚀 Recommended Action Plan")
                for action in action_plan:
                    st.markdown(f"- {action}")
        
    else:
        st.warning(f"No feedback data found for {selected_name}.")

# TAB 4: Performance Appraisal
with tab4:
    st.subheader("🏆 Annual Performance Appraisal")
    
    # Initialize session state for this tab if it doesn't exist
    if 'appraisal_calculated' not in st.session_state:
        st.session_state['appraisal_calculated'] = False

    # 1. THE CALCULATE BUTTON
    if st.button("Calculate My Performance Score"):
        st.session_state['appraisal_calculated'] = True
        
    # 2. DISPLAY RESULTS (Only if calculated)
    if st.session_state['appraisal_calculated']:
        # Run calculation
        result = db.calculate_appraisal_score(faculty_id)
        score = result["total"]
        breakdown = result["breakdown"]
        
        # Display Score Card
        st.markdown(f"""
        <div style="text-align: center; border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="margin:0;">Final Appraisal Score</h2>
            <h1 style="font-size: 60px; color: #4CAF50; margin:0;">{score}/100</h1>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Students (50%)", f"{breakdown['Feedback (50%)']}")
        c2.metric("Research (30%)", f"{breakdown['Research (30%)']}")
        c3.metric("Attendance (20%)", f"{breakdown['Attendance (20%)']}")
        
        st.divider()
        
        # 3. THE PDF BUTTON (Now it stays visible!)
        st.subheader("📄 Download Official Report")
        
        # Logic to generate PDF
        if st.button("Generate PDF Report"):
            try:
                pdf_file = pdf_utils.generate_appraisal_pdf(faculty_id)
                
                with open(pdf_file, "rb") as f:
                    pdf_data = f.read()
                
                st.download_button(
                    label="⬇️ Click Here to Download PDF",
                    data=pdf_data,
                    file_name=pdf_file,
                    mime="application/pdf"
                )
                st.success("✅ Report Ready! Click the download button above.")
                
            except Exception as e:
                st.error(f"⚠️ Error generating PDF: {e}")

# TAB 5: HOD Dashboard (Updated with Limit Extension)
with tab5:
    st.subheader("🔒 Head of Department (HOD) Approval Portal")
    
    # --- SECTION 1: APPROVAL WORKFLOW ---
    st.markdown("### 1. Pending Approvals")
    pending_leaves = db.get_pending_leaves()
    
    if pending_leaves.empty:
        st.success("✅ No pending leave requests.")
    else:
        for index, row in pending_leaves.iterrows():
            with st.expander(f"{row['name']} - {row['type']} ({row['days_requested']} days)"):
                c1, c2 = st.columns(2)
                
                if c1.button(f"✅ Approve", key=f"app_{row['leave_id']}"):
                    db.update_leave_status(row['leave_id'], "Approved")
                    email_draft = email_utils.generate_leave_email(row['name'], row['type'], row['days_requested'], "Approved")
                    st.success(f"Approved!")
                    st.text_area("Email Draft:", email_draft, height=150)
                    
                if c2.button(f"❌ Reject", key=f"rej_{row['leave_id']}"):
                    db.update_leave_status(row['leave_id'], "Rejected")
                    email_draft = email_utils.generate_leave_email(row['name'], row['type'], row['days_requested'], "Rejected")
                    st.error(f"Rejected.")
                    st.text_area("Email Draft:", email_draft, height=150)

    st.divider()

    # --- SECTION 2: LIMIT EXTENSION (NEW) ---
    st.markdown("### 2. Grant Special Leave Extension")
    st.info("Use this to increase the leave limit for a specific faculty member.")
    
    with st.form("bonus_leave_form"):
        # Get Faculty List
        fac_data = db.get_faculty_names()
        target_fac = st.selectbox("Select Faculty", fac_data['name'])
        
        c1, c2 = st.columns(2)
        target_type = c1.selectbox("Leave Type to Extend", ["CL", "SL", "EL", "OD"])
        extra_days = c2.number_input("Extra Days to Grant", min_value=1, max_value=10)
        
        if st.form_submit_button("Grant Extension"):
            # Get ID
            target_id = fac_data[fac_data['name'] == target_fac]['faculty_id'].values[0]
            
            # Save to DB
            db.grant_bonus_leave(target_id, target_type, extra_days)
            st.success(f"✅ Successfully added {extra_days} extra {target_type} days to {target_fac}'s quota.")

# TAB 6: Teaching Progress Tracker
with tab6:
    st.subheader("📈 Syllabus Coverage & Recovery Plan")
    
    # 1. Try to Fetch Data
    fid_clean = int(faculty_id)
    progress_df = db.get_teaching_progress(fid_clean)
    
    # 2. IF DATA IS MISSING -> SHOW REPAIR BUTTON
    if progress_df.empty:
        st.error(f"⚠️ No teaching logs found for Faculty ID: {fid_clean}")
        st.info("The database table appears empty or disconnected for this user.")
        
        # --- THE SELF-REPAIR BUTTON ---
        if st.button("🛠️ CLICK HERE TO REPAIR TEACHING DATA"):
            import random
            
            # Use the App's own connection to ensure we hit the right file
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # 1. Create Table (Just in case it's missing)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teaching_progress (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    faculty_id INTEGER,
                    week_number INTEGER,
                    teacher_completion_pct INTEGER,
                    student_avg_pct INTEGER,
                    class_verdict TEXT
                )
            """)
            
            # 2. Delete old broken data for this ID
            cursor.execute("DELETE FROM teaching_progress WHERE faculty_id = ?", (fid_clean,))
            
            # 3. Generate 12 Weeks of Fresh Data
            current_progress = 0
            for week in range(1, 13):
                increment = random.randint(5, 9)
                current_progress += increment
                if current_progress > 100: current_progress = 100
                
                # Student view is slightly lower/random
                student_view = max(0, current_progress - random.randint(0, 10))
                
                # Verdict
                if current_progress < (week * 7): verdict = "Lagging Behind"
                elif current_progress > (week * 9): verdict = "Too Fast"
                else: verdict = "On Track"
                
                cursor.execute("""
                    INSERT INTO teaching_progress 
                    (faculty_id, week_number, teacher_completion_pct, student_avg_pct, class_verdict)
                    VALUES (?, ?, ?, ?, ?)
                """, (fid_clean, week, current_progress, student_view, verdict))
                
            conn.commit()
            conn.close()
            
            st.success("✅ Database Repaired! Reloading...")
            st.rerun() # Automatically refreshes the page

    # 3. IF DATA EXISTS -> SHOW DASHBOARD
    else:
        # Status Overview
        latest_week = progress_df.iloc[-1]
        completion = latest_week['teacher_completion_pct']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Week", f"Week {latest_week['week_number']}")
        c2.metric("Syllabus Completed", f"{completion}%")
        
        target = latest_week['week_number'] * 8
        if completion < target:
            status = "Lagging Behind"
            color = "red"
        else:
            status = "On Track"
            color = "green"
        c3.markdown(f"**Status:** :{color}[{status}]")
        
        st.divider()
        
        # Visualization
        st.markdown("### 📊 Reality Check: Teacher vs. Student Perception")
        chart_data = progress_df.set_index("week_number")[['teacher_completion_pct', 'student_avg_pct']]
        st.line_chart(chart_data)
        
        # AI Recovery Plan
        st.subheader("🤖 AI Recovery Plan Suggestions")
        if status == "Lagging Behind":
            deficit = target - completion
            st.error(f"⚠️ You are {deficit}% behind schedule.")
            st.markdown("#### Recommended Actions:")
            st.write("1. **Schedule Extra Class:** Book a slot this Saturday.")
            st.write("2. **Share Notes:** Distribute PDF notes for the current unit.")
        else:
            st.success("✅ You are on track!")
            st.write("- **Recommendation:** Conduct a surprise quiz to test retention.")
