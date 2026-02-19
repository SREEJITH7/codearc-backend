from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_otp_email(email, otp):
    subject = " CodeArc - Your One-Time Verification Code"

    text_content = f"""
Hello,

Your CodeArc verification code is: {otp}

This code will expire in 5 minutes.

If you did not request this code, please ignore this email or contact our support team.

Thank you,
CodeArc Team
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background: white; padding: 30px; border-radius: 8px;">
            
            <h2 style="color: #1f2937; text-align: center;">CodeArc</h2>
            
            <p style="font-size: 16px; color: #374151;">
                Hello,
            </p>

            <p style="font-size: 16px; color: #374151;">
                Use the following One-Time Password (OTP) to complete your verification:
            </p>

            <div style="text-align: center; margin: 20px 0;">
                <span style="font-size: 28px; font-weight: bold; letter-spacing: 5px; color: #2563eb;">
                    {otp}
                </span>
            </div>

            <p style="font-size: 14px; color: #6b7280;">
                This code will expire in <strong>5 minutes</strong>.
            </p>

            <p style="font-size: 14px; color: #6b7280;">
                If you did not request this verification, you can safely ignore this email.
            </p>

            <hr style="margin: 25px 0;">

            <p style="font-size: 12px; color: #9ca3af; text-align: center;">
                © {2026} CodeArc. All rights reserved.
            </p>

        </div>
    </div>
    """

    email_message = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

    email_message.attach_alternative(html_content, "text/html")
    email_message.send()


