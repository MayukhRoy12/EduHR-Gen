import sqlite3
import os

# --- SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "academic_hr.db")
AUTH_FILE = os.path.join(BASE_DIR, "auth_utils.py")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("🚀 GENERATING CREDENTIALS (User=First_Last, Pass=1234)...")

# 1. Fetch all Faculty (Sorted by ID)
cursor.execute("SELECT faculty_id, name FROM faculty_master ORDER BY faculty_id ASC")
faculty_list = cursor.fetchall()

# 2. Start building file content
file_content = """import streamlit as st
import time

# --- AUTO-GENERATED CREDENTIALS ---
USERS = {
    "admin": {
        "password": "admin123", 
        "role": "HOD", 
        "faculty_id": 999
    },
"""

# 3. COLLISION LOGIC
seen_usernames = {} 

for fid, name in faculty_list:
    # Clean Name
    clean_name = name.replace("Dr.", "").replace("Prof.", "").strip()
    parts = clean_name.split(" ")
    
    # Base Username (First_Last)
    if len(parts) > 1:
        base_username = f"{parts[0].lower()}_{parts[-1].lower()}" # e.g., amit_sharma
    else:
        base_username = parts[0].lower() # e.g., suman
    
    # Handle Duplicate Usernames
    if base_username in seen_usernames:
        count = seen_usernames[base_username]
        final_username = f"{base_username}{count}" # e.g., amit_sharma1
        seen_usernames[base_username] += 1
    else:
        final_username = base_username
        seen_usernames[base_username] = 1
    
    # Add to file content
    file_content += f'    "{final_username}": {{\n'
    file_content += f'        "password": "1234",\n'
    file_content += f'        "role": "Faculty",\n'
    file_content += f'        "faculty_id": {fid}\n'
    file_content += f'    }},\n'

# 4. Finish the file
file_content += """}

def login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["role"] = None
        st.session_state["user_id"] = None

    if not st.session_state["authenticated"]:
        st.markdown("## 🔐 EduHR-Gen Portal Login")
        st.write("Please sign in to access the Academic HR System.")
        st.info("**Credential Format:** \\n- **Username:** firstname_lastname (e.g. `amit_sharma`) \\n- **Password:** `1234`")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            username = st.text_input("Username").lower().strip()
            password = st.text_input("Password", type="password")
            
            if st.button("Login", type="primary"):
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["role"] = USERS[username]["role"]
                    st.session_state["user_id"] = USERS[username]["faculty_id"]
                    st.success(f"Welcome back, {username.capitalize()}!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password")
        st.stop()

def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        st.session_state["role"] = None
        st.session_state["user_id"] = None
        st.rerun()

def get_current_role():
    return st.session_state.get("role", "Guest")
"""

with open(AUTH_FILE, "w", encoding="utf-8") as f:
    f.write(file_content)

conn.close()
print("✅ Updated 'auth_utils.py'. Format is First_Last / 1234.")
