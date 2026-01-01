from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import db_utils as db
import os
import pandas as pd
from datetime import datetime

def generate_appraisal_pdf(faculty_id):
    # 1. FETCH ALL DATA
    # We use .iloc[0] to get the single row as a Series
    profile = db.get_faculty_profile(faculty_id).iloc[0]
    appraisal = db.calculate_appraisal_score(faculty_id)
    
    # 2. SETUP PDF FILE
    # Clean filename (remove spaces)
    clean_name = profile['name'].replace(' ', '_')
    filename = f"Appraisal_Report_{faculty_id}_{clean_name}.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # --- HEADER ---
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Annual Performance Appraisal Report")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 65, "Confidential HR Document")
    c.line(50, height - 75, width - 50, height - 75)
    
    # --- SECTION 1: FACULTY DETAILS ---
    y_pos = height - 120
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.darkblue)
    c.drawString(50, y_pos, "1. Faculty Profile")
    c.setFillColor(colors.black)
    
    c.setFont("Helvetica", 12)
    y_pos -= 25
    c.drawString(50, y_pos, f"Name: {profile['name']}")
    c.drawString(350, y_pos, f"Employee ID: {profile['faculty_id']}")
    
    y_pos -= 20
    c.drawString(50, y_pos, f"Department: {profile['department']}")
    c.drawString(350, y_pos, f"Designation: {profile['designation']}")
    
    # --- SECTION 2: PERFORMANCE SCORECARD ---
    y_pos -= 60
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.darkblue)
    c.drawString(50, y_pos, "2. Performance Scorecard")
    c.setFillColor(colors.black)
    
    # Draw Score Box
    score = appraisal['total']
    breakdown = appraisal['breakdown']
    
    # Color Logic for Score
    if score >= 80: 
        bg_color = colors.green
        verdict_text = "OUTSTANDING"
    elif score >= 60: 
        bg_color = colors.orange
        verdict_text = "MEETS EXPECTATIONS"
    else: 
        bg_color = colors.red
        verdict_text = "NEEDS IMPROVEMENT"
    
    # Draw the colored banner
    c.setFillColor(bg_color)
    c.rect(50, y_pos - 80, 510, 60, fill=1, stroke=0) 
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    # Center the text
    c.drawCentredString(width/2, y_pos - 65, f"FINAL SCORE: {score}/100")
    
    # Reset Color
    c.setFillColor(colors.black)
    
    # Breakdown Table
    data = [
        ["Performance Metric", "Weightage", "Points Earned"],
        ["Student Feedback", "50%", f"{breakdown['Feedback (50%)']}"],
        ["Research & Publications", "30%", f"{breakdown['Research (30%)']}"],
        ["Attendance & Discipline", "20%", f"{breakdown['Attendance (20%)']}"]
    ]
    
    table = Table(data, colWidths=[250, 100, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'), # Left align first column
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 55, y_pos - 180)
    
    # --- SECTION 3: HR RECOMMENDATION ---
    y_pos -= 230
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.darkblue)
    c.drawString(50, y_pos, "3. Official Recommendation")
    c.setFillColor(colors.black)
    
    c.setFont("Helvetica", 12)
    y_pos -= 30
    
    if score >= 80:
        rec_detail = "Eligible for Promotion and Performance Bonus."
    elif score >= 60:
        rec_detail = "Continue with current responsibilities. Annual increment approved."
    else:
        rec_detail = "Performance Improvement Plan (PIP) required. Promotion holds."
        
    c.drawString(50, y_pos, f"Official Verdict: {verdict_text}")
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(50, y_pos - 20, f"Action: {rec_detail}")
    
    # --- AUTOMATIC DIGITAL SIGNATURE (NEW!) ---
    y_pos -= 100
    
    # Draw a "Digital Stamp" box
    c.setStrokeColor(colors.darkblue)
    c.setFillColor(colors.aliceblue) # Very light blue background
    c.roundRect(350, y_pos - 50, 200, 70, 10, fill=1, stroke=1)
    
    # Stamp Text
    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(450, y_pos, "DIGITALLY VERIFIED")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    c.drawCentredString(450, y_pos - 15, "Academic HR Administration")
    
    # Dynamic Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.setFont("Courier", 8)
    c.drawCentredString(450, y_pos - 35, f"Signed: {timestamp}")
    c.drawCentredString(450, y_pos - 45, "ID: SYS-AUTO-GEN")

    c.save()
    return filename
