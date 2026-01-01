import streamlit as st
import time

# --- AUTO-GENERATED CREDENTIALS ---
USERS = {
    "admin": {
        "password": "admin123", 
        "role": "HOD", 
        "faculty_id": 999
    },
    "sneha_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 101
    },
    "suman_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 102
    },
    "arjun_patel": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 103
    },
    "neha_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 104
    },
    "arjun_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 105
    },
    "suman_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 106
    },
    "vikas_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 107
    },
    "kiran_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 109
    },
    "vikas_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 110
    },
    "pooja_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 111
    },
    "kiran_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 112
    },
    "arjun_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 113
    },
    "amit_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 114
    },
    "suman_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 115
    },
    "vikas_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 116
    },
    "suman_patel": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 117
    },
    "sneha_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 119
    },
    "pooja_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 121
    },
    "neha_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 122
    },
    "rohan_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 124
    },
    "pooja_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 125
    },
    "pooja_patel": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 127
    },
    "kiran_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 129
    },
    "kiran_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 130
    },
    "amit_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 131
    },
    "rohan_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 132
    },
    "rohan_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 133
    },
    "suman_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 134
    },
    "rohan_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 136
    },
    "vikas_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 138
    },
    "priya_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 139
    },
    "arjun_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 142
    },
    "neha_patel": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 144
    },
    "priya_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 145
    },
    "suman_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 146
    },
    "neha_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 147
    },
    "arjun_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 150
    },
    "sneha_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 153
    },
    "arjun_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 154
    },
    "vikas_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 157
    },
    "arjun_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 158
    },
    "amit_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 159
    },
    "pooja_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 162
    },
    "neha_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 163
    },
    "amit_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 165
    },
    "priya_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 166
    },
    "amit_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 167
    },
    "sneha_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 168
    },
    "suman_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 169
    },
    "vikas_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 173
    },
    "vikas_patel": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 174
    },
    "priya_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 175
    },
    "sneha_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 177
    },
    "priya_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 178
    },
    "kiran_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 181
    },
    "kiran_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 182
    },
    "rohan_patel": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 183
    },
    "neha_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 189
    },
    "arjun_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 190
    },
    "vikas_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 192
    },
    "arjun_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 198
    },
    "rohan_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 200
    },
    "sneha_patel": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 202
    },
    "sneha_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 203
    },
    "priya_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 204
    },
    "priya_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 208
    },
    "neha_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 209
    },
    "amit_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 216
    },
    "vikas_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 218
    },
    "amit_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 221
    },
    "neha_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 225
    },
    "kiran_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 226
    },
    "sneha_chatterjee": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 231
    },
    "priya_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 232
    },
    "arjun_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 233
    },
    "pooja_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 250
    },
    "neha_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 255
    },
    "pooja_ghosh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 258
    },
    "pooja_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 268
    },
    "rohan_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 275
    },
    "vikas_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 288
    },
    "amit_patel": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 291
    },
    "rohan_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 300
    },
    "suman_iyer": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 311
    },
    "pooja_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 314
    },
    "priya_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 318
    },
    "rohan_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 325
    },
    "neha_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 337
    },
    "sneha_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 339
    },
    "pooja_das": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 340
    },
    "rohan_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 343
    },
    "kiran_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 344
    },
    "sneha_verma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 350
    },
    "suman_singh": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 412
    },
    "suman_sharma": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 429
    },
    "amit_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 432
    },
    "amit_reddy": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 458
    },
    "kiran_nair": {
        "password": "1234",
        "role": "Faculty",
        "faculty_id": 486
    },
}

def login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["role"] = None
        st.session_state["user_id"] = None

    if not st.session_state["authenticated"]:
        st.markdown("## 🔐 EduHR-Gen Portal Login")
        st.write("Please sign in to access the Academic HR System.")
        st.info("**Credential Format:** \n- **Username:** firstname_lastname (e.g. `amit_sharma`) \n- **Password:** `1234`")
        
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
