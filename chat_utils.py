import warnings
# 🛑 SILENCE WARNINGS BEFORE IMPORTING GOOGLE
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")

import google.generativeai as genai
import pandas as pd
import db_utils as db

def prepare_data_summary():
    """Creates a text summary of the database schema."""
    conn = db.get_connection()
    faculty = pd.read_sql("SELECT * FROM faculty_master", conn)
    leaves = pd.read_sql("SELECT * FROM leave_records", conn)
    feedback = pd.read_sql("SELECT * FROM student_feedback", conn)
    conn.close()
    
    return f"""
    Database Summary:
    1. FACULTY_MASTER: {faculty.head(5).to_string(index=False)}
    2. LEAVE_RECORDS: {leaves.head(5).to_string(index=False)}
    3. STUDENT_FEEDBACK: {feedback.head(5).to_string(index=False)}
    """

def ask_gemini(api_key, question):
    """Tries multiple model versions until one works."""
    try:
        genai.configure(api_key=api_key)
        
        # 📝 LIST OF MODELS TO TRY (In order of preference)
        candidates = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro",       
            "gemini-1.0-pro"
        ]
        
        data_context = prepare_data_summary()
        
        prompt = f"""
        You are an HR Data Analyst Assistant. 
        Here is the data in my database:
        {data_context}
        
        USER QUESTION: {question}
        
        INSTRUCTIONS:
        1. Answer based ONLY on the data provided above.
        2. Keep the answer professional and concise.
        """
        
        last_error = ""
        
        # 🔄 LOOP: Try each model until one succeeds
        for model_name in candidates:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text  # ✅ SUCCESS!
            except Exception as e:
                last_error = str(e)
                continue 
        
        return f"❌ All AI models failed. Last error: {last_error}"
        
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"
