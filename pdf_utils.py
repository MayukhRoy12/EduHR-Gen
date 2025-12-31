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
    profile = db.get_faculty_profile(faculty_id).iloc[0]
    appraisal = db.calculate_appraisal_score(faculty_id)
    
    # 2. SETUP PDF FILE
    filename = f"Appraisal_Report_{faculty_id}_{profile['name'].replace(' ', '_')}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # --- HEADER ---
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Annual Performance Appraisal Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")
    c.line(50, height - 80, width - 50, height - 80)
    
    # --- SECTION 1: FACULTY DETAILS ---
    y_pos = height - 120
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "1. Faculty Details")
    
    c.setFont("Helvetica", 12)
    y_pos -= 25
    c.drawString(50, y_pos, f"Name: {profile['name']}")
    c.drawString(300, y_pos, f"ID: {profile['faculty_id']}")
    
    y_pos -= 20
    c.drawString(50, y_pos, f"Department: {profile['department']}")
    c.drawString(300, y_pos, f"Designation: {profile['designation']}")
    
    # --- SECTION 2: PERFORMANCE SCORECARD ---
    y_pos -= 60
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "2. Performance Scorecard")
    
    # Draw Score Box
    score = appraisal['total']
    breakdown = appraisal['breakdown']
    
    # Color Logic for Score
    if score >= 80: color = colors.green
    elif score >= 60: color = colors.orange
    else: color = colors.red
    
    c.setFillColor(color)
    c.rect(50, y_pos - 80, 500, 60, fill=1) # Background bar
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, y_pos - 65, f"FINAL SCORE: {score}/100")
    
    # Reset Color
    c.setFillColor(colors.black)
    
    # Breakdown Table
    data = [
        ["Metric", "Weightage", "Points Earned"],
        ["Student Feedback", "50%", f"{breakdown['Feedback (50%)']}"],
        ["Research & Pubs", "30%", f"{breakdown['Research (30%)']}"],
        ["Attendance", "20%", f"{breakdown['Attendance (20%)']}"]
    ]
    
    table = Table(data, colWidths=[200, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 100, y_pos - 180)
    
    # --- SECTION 3: HR RECOMMENDATION ---
    y_pos -= 230
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_pos, "3. Official Recommendation")
    
    c.setFont("Helvetica", 12)
    y_pos -= 30
    if score >= 80:
        verdict = "Outstanding Performance. Eligible for Promotion and Bonus."
    elif score >= 60:
        verdict = "Meets Expectations. Continue with current responsibilities."
    else:
        verdict = "Below Expectations. Performance Improvement Plan (PIP) required."
        
    c.drawString(50, y_pos, f"Verdict: {verdict}")
    
    # --- SIGNATURES ---
    y_pos -= 100
    c.line(50, y_pos, 250, y_pos)
    c.drawString(50, y_pos - 15, "Faculty Signature")
    
    c.line(350, y_pos, 550, y_pos)
    c.drawString(350, y_pos - 15, "HOD / HR Signature")
    
    c.save()
    return filename
