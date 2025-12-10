# common/email_service.py
import os
import smtplib
from email.message import EmailMessage

def send_email_simple(to_email: str, subject: str, body: str):
    """
    Simple email sender. For dev it prints to console.
    Replace with SMTP or external provider for production.
    """
    # Development: always print to console
    print(f"[Email] To: {to_email}\nSubject: {subject}\n\n{body}\n")

    # Try SMTP if configured
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASS = os.getenv('SMTP_PASS')
    
    if SMTP_HOST and SMTP_USER:
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = SMTP_USER
            msg['To'] = to_email
            msg.set_content(body)
            
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(msg)
            print("[Email] Successfully sent via SMTP")
        except Exception as e:
            print(f"[Email] SMTP failed: {e}. Email printed to console instead.")


