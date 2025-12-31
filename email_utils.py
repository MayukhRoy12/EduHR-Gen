import datetime

def generate_leave_email(faculty_name, leave_type, days, status, manager_name="HOD"):
    """
    Simulates a Generative AI email writer.
    Generates a professional email draft based on the approval status.
    """
    today = datetime.date.today().strftime("%B %d, %Y")
    
    if status == "Approved":
        subject = f"Approval of Leave Request - {leave_type}"
        body = f"""
        Subject: {subject}
        
        Dear Prof. {faculty_name},

        I am writing to formally confirm that your request for {days} day(s) of {leave_type} has been APPROVED.
        
        The leave has been recorded in the faculty attendance registry. Please ensure that your teaching responsibilities are covered during your absence.
        
        Dates: [As per system record]
        Approval Date: {today}

        Best regards,
        
        {manager_name}
        Head of Department
        Academic Administration
        """
        
    else:  # Rejected
        subject = f"Update on Leave Request - {leave_type}"
        body = f"""
        Subject: {subject}
        
        Dear Prof. {faculty_name},

        I have reviewed your request for {days} day(s) of {leave_type}.

        Regrettably, I am unable to approve this request at the current time due to ongoing departmental priorities and scheduling constraints. We can discuss this further if you have an urgent exigency.

        Please treat this as a formal notification of REJECTION.

        Sincerely,
        
        {manager_name}
        Head of Department
        Academic Administration
        """
        
    return body
