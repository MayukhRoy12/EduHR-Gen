import streamlit as st
import db_utils as db
import datetime

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
        
        # Fetch detailed profile for email signature
        # We handle cases where extra columns might be missing
        try:
            profile = db.get_faculty_profile(faculty_id) 
            # Safe access to department/designation if they exist
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
    """
    Simulates a Generative AI model to create a formal email draft.
    In Week 7-8, we can replace this with a real LLM call (like HuggingFace).
    """
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

# --- MAIN DASHBOARD ---
tab1, tab2 = st.tabs(["📝 Apply for Leave", "📜 My Leave History"])

# TAB 1: Leave Application Form
with tab1:
    st.subheader("Submit a Leave Request")
    st.info("Your request will be sent to the HOD for approval.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("leave_form"):
            st.markdown("### 1. Enter Leave Details")
            leave_type_selection = st.selectbox("Leave Type", ["CL (Casual Leave)", "SL (Sick Leave)", "EL (Earned Leave)", "OD (On Duty)"])
            leave_code = leave_type_selection.split()[0] 
            
            days = st.number_input("Number of Days", min_value=1, max_value=30, value=1)
            reason = st.text_area("Reason for Leave", placeholder="e.g., Attending International Conference on AI...")
            
            # This button triggers the form submission
            submitted = st.form_submit_button("Generate Email & Submit")

    with col2:
        st.markdown("### 2. AI Email Preview")
        
        if submitted:
            # 1. Generate the AI Email Draft
            email_draft = generate_email_draft(selected_name, desig, dept, leave_type_selection, days, reason)
            
            # 2. Display it in a nice box
            st.text_area("Auto-Generated Draft (Ready to Send)", value=email_draft, height=350)
            
            # 3. Save to Database
            success = db.apply_leave(faculty_id, leave_code, days)
            
            if success:
                st.success(f"✅ Application Submitted to DB!")
                st.balloons()
            else:
                st.error("❌ Failed to save to database.")
        else:
            st.info("👋 Fill out the form on the left and click 'Submit' to see the AI-generated email draft here.")

# TAB 2: View History
with tab2:
    st.subheader("Your Application Status")
    history_df = db.get_leave_history(faculty_id)
    
    if not history_df.empty:
        st.dataframe(history_df[['leave_id', 'type', 'days_requested', 'status']], use_container_width=True)
    else:
        st.info("No leave records found for this profile.")
