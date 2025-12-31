import pandas as pd
import random

def generate_feedback_insight(comments_list, avg_rating):
    """
    Simulates an AI analyzing student comments to generate a summary and action plan.
    """
    if not comments_list or len(comments_list) == 0:
        return "No comments available to analyze.", []

    # 1. Combine all text for analysis
    full_text = " ".join(comments_list).lower()
    
    # 2. KEYWORD DETECTION (The "Brain")
    # We look for specific patterns in the text
    issues = []
    strengths = []
    
    # Speed/Pace Analysis
    if any(w in full_text for w in ["fast", "rushed", "hurry", "speed"]):
        issues.append("Pace is too fast")
    elif any(w in full_text for w in ["slow", "boring", "sleep"]):
        issues.append("Lectures are not engaging enough")
        
    # Clarity Analysis
    if any(w in full_text for w in ["confused", "hard to understand", "unclear"]):
        issues.append("Concepts need better explanation")
    if any(w in full_text for w in ["clear", "explained well", "easy to understand"]):
        strengths.append("Excellent conceptual clarity")
        
    # Resources
    if any(w in full_text for w in ["notes", "slides", "material", "book"]):
        issues.append("Students are asking for better study materials")

    # 3. GENERATE NARRATIVE SUMMARY
    summary = f"Based on an analysis of {len(comments_list)} student reviews, the overall sentiment is "
    
    if avg_rating >= 4.0:
        summary += "**Overwhelmingly Positive**. "
        summary += "Students consistently praised the course structure. "
        if strengths: summary += f"Key strength identified: **{strengths[0]}**. "
        summary += "The faculty is seen as a subject matter expert."
    elif avg_rating >= 3.0:
        summary += "**Generally Positive with specific concerns**. "
        summary += "While many students are satisfied, there are consistent recurring themes regarding delivery. "
        if issues: summary += f"Main pain point: **{issues[0]}**. "
    else:
        summary += "**Critical**. "
        summary += "Immediate intervention is required. Students are expressing frustration with the fundamental delivery method."

    # 4. GENERATE ACTION PLAN (Recommendations)
    actions = []
    if "Pace is too fast" in issues:
        actions.append("📉 **Action:** Reduce coverage speed by 15% in next lectures.")
        actions.append("📹 **Tip:** Record sessions so students can re-watch complex parts.")
    elif "Lectures are not engaging enough" in issues:
        actions.append("🎮 **Action:** Introduce a quiz or interactive poll every 20 mins.")
    
    if "Concepts need better explanation" in issues:
        actions.append("🧠 **Action:** Use more real-world analogies.")
        actions.append("❓ **Tip:** Start the next class with a 10-min Q&A session.")
        
    if not actions: # Default advice for good teachers
        actions.append("🌟 **Maintain:** Keep up the current teaching style.")
        actions.append("🤝 **Growth:** Consider mentoring junior faculty members.")

    return summary, actions
