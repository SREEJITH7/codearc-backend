
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from apps.recruiter_app.models import Application
from datetime import date


def build_offer_email_html(candidate_name, job_title, company_name, recruiter_name, recruiter_email, custom_message):
  
    current_year = date.today().year
    formatted_date = date.today().strftime("%B %d, %Y")

    
    safe_message = (
        custom_message
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Job Offer – {job_title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
      background-color: #f0f2f5;
      color: #1a1a2e;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: #4f46e5; text-decoration: none; }}
  </style>
</head>
<body style="background:#f0f2f5; padding: 40px 16px;">

  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:620px; margin:0 auto;">

    <!-- ── TOP LOGO BAR ── -->
    <tr>
      <td style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
                 border-radius: 16px 16px 0 0; padding: 32px 40px; text-align:center;">
        <p style="font-size:26px; font-weight:800; color:#ffffff; letter-spacing:-0.5px; margin:0;">
          {company_name}
        </p>
        <p style="font-size:11px; color:#a5b4fc; letter-spacing:3px; text-transform:uppercase; margin-top:4px;">
          Talent Acquisition
        </p>
      </td>
    </tr>

    <!-- ── HERO BANNER ── -->
    <tr>
      <td style="background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%); padding: 40px 40px 48px;">
        <p style="font-size:13px; color:#c7d2fe; font-weight:600; letter-spacing:2px;
                  text-transform:uppercase; margin-bottom:12px;">
          Official Offer of Employment
        </p>
        <h1 style="font-size:32px; font-weight:800; color:#ffffff; line-height:1.25; margin:0 0 16px;">
          Congratulations,<br>{candidate_name}! 🎉
        </h1>
        <p style="font-size:15px; color:#c7d2fe; line-height:1.6; margin:0;">
          We are thrilled to extend this formal offer of employment for the role of
          <strong style="color:#ffffff;">{job_title}</strong> at {company_name}.
        </p>
      </td>
    </tr>

    <!-- ── ROLE HIGHLIGHT CARD ── -->
    <tr>
      <td style="background:#ffffff; padding: 0 40px;">
        <div style="background: linear-gradient(135deg, #eef2ff, #f5f3ff);
                    border: 1px solid #c7d2fe; border-radius:12px;
                    padding: 24px 28px; margin-top: -20px; margin-bottom: 32px;
                    box-shadow: 0 4px 20px rgba(99,102,241,0.12);">
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="width:50%; padding-right:16px; border-right:1px solid #c7d2fe;">
                <p style="font-size:10px; font-weight:700; color:#6366f1; letter-spacing:2px;
                           text-transform:uppercase; margin-bottom:6px;">Position</p>
                <p style="font-size:17px; font-weight:700; color:#1e1b4b;">{job_title}</p>
              </td>
              <td style="width:50%; padding-left:16px;">
                <p style="font-size:10px; font-weight:700; color:#6366f1; letter-spacing:2px;
                           text-transform:uppercase; margin-bottom:6px;">Date Issued</p>
                <p style="font-size:17px; font-weight:700; color:#1e1b4b;">{formatted_date}</p>
              </td>
            </tr>
          </table>
        </div>
      </td>
    </tr>

    <!-- ── BODY CONTENT ── -->
    <tr>
      <td style="background:#ffffff; padding: 0 40px 36px;">
        <p style="font-size:15px; color:#374151; line-height:1.8; margin-bottom:20px;">
          Dear <strong style="color:#1e1b4b;">{candidate_name}</strong>,
        </p>
        <p style="font-size:15px; color:#374151; line-height:1.8; margin-bottom:20px;">
          {safe_message}
        </p>

        <!-- Divider -->
        <div style="border-top:2px solid #f3f4f6; margin: 28px 0;"></div>

        <!-- next steps -->
        <p style="font-size:11px; font-weight:700; color:#6366f1; letter-spacing:2px;
                  text-transform:uppercase; margin-bottom:16px;">Next Steps</p>

        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="vertical-align:top; padding-bottom:14px;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:32px; height:32px; background:#eef2ff; border-radius:50%;
                              text-align:center; vertical-align:middle; font-size:13px;
                              font-weight:800; color:#4f46e5;">1</td>
                  <td style="padding-left:14px; font-size:14px; color:#374151; line-height:1.6;">
                    <strong style="color:#1e1b4b;">Review this offer</strong> carefully and reach out if you have any questions.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="vertical-align:top; padding-bottom:14px;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:32px; height:32px; background:#eef2ff; border-radius:50%;
                              text-align:center; vertical-align:middle; font-size:13px;
                              font-weight:800; color:#4f46e5;">2</td>
                  <td style="padding-left:14px; font-size:14px; color:#374151; line-height:1.6;">
                    <strong style="color:#1e1b4b;">Reply to this email</strong> to confirm your acceptance of the offer.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="vertical-align:top;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="width:32px; height:32px; background:#eef2ff; border-radius:50%;
                              text-align:center; vertical-align:middle; font-size:13px;
                              font-weight:800; color:#4f46e5;">3</td>
                  <td style="padding-left:14px; font-size:14px; color:#374151; line-height:1.6;">
                    Our HR team will <strong style="color:#1e1b4b;">contact you</strong> with onboarding details.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>

        <!-- CTA Button -->
        <div style="text-align:center; margin-top:36px;">
          <a href="mailto:{recruiter_email}?subject=Re: {job_title} Offer Acceptance"
             style="display:inline-block; background:linear-gradient(135deg,#4f46e5,#7c3aed);
                    color:#ffffff; font-size:15px; font-weight:700; padding:14px 40px;
                    border-radius:10px; letter-spacing:0.3px;
                    box-shadow:0 4px 20px rgba(99,102,241,0.35);">
            Accept This Offer →
          </a>
        </div>
      </td>
    </tr>

    <!-- ── SIGNATURE ── -->
    <tr>
      <td style="background:#f8faff; border-top:1px solid #e5e7eb; border-left:1px solid #e5e7eb;
                 border-right:1px solid #e5e7eb; padding: 28px 40px;">
        <p style="font-size:14px; color:#6b7280; margin-bottom:4px;">Warm regards,</p>
        <p style="font-size:17px; font-weight:700; color:#1e1b4b; margin-bottom:2px;">{recruiter_name}</p>
        <p style="font-size:13px; color:#6366f1; margin-bottom:2px;">Talent Acquisition · {company_name}</p>
        <p style="font-size:13px; color:#9ca3af;">
          <a href="mailto:{recruiter_email}" style="color:#6366f1;">{recruiter_email}</a>
        </p>
      </td>
    </tr>

    <!-- ── FOOTER ── -->
    <tr>
      <td style="background:#1e1b4b; border-radius:0 0 16px 16px; padding:24px 40px; text-align:center;">
        <p style="font-size:12px; color:#818cf8; margin-bottom:6px;">
          © {current_year} {company_name}. All rights reserved.
        </p>
        <p style="font-size:11px; color:#4c5899; line-height:1.6;">
          This email and any attachments are confidential and intended solely for the named recipient.
          If you received this in error, please disregard and notify the sender.
        </p>
      </td>
    </tr>

  </table>
</body>
</html>"""
    return html


class RecruiterSendOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        
        try:
            application = Application.objects.select_related(
                'job', 'job__recruiter', 'user'
            ).get(
                id=application_id,
                job__recruiter=request.user
            )
        except Application.DoesNotExist:
            return Response(
                {"success": False, "message": "Application not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if application.status != "SHORTLISTED":
            return Response(
                {"success": False, "message": "Only shortlisted applicants can be sent an offer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        subject = request.data.get("subject")
        message = request.data.get("message")

        if not subject or not message:
            return Response(
                {"success": False, "message": "Subject and message are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        recruiter = request.user
        company_name  = getattr(recruiter, 'company_name', None) or getattr(recruiter, 'username', 'Our Company')
        recruiter_name = (
            getattr(recruiter, 'contact_person', None)
            or getattr(recruiter, 'get_full_name', lambda: None)()
            or recruiter.username
        )
        recruiter_email = recruiter.email
        candidate_name  = application.user.get_full_name() or application.user.username or "Candidate"
        job_title       = application.job.title if hasattr(application.job, 'title') else "the position"
        recipient_email = getattr(application, 'email', None) or application.user.email

        
        html_content = build_offer_email_html(
            candidate_name=candidate_name,
            job_title=job_title,
            company_name=company_name,
            recruiter_name=recruiter_name,
            recruiter_email=recruiter_email,
            custom_message=message,
        )

        
        plain_text = (
            f"Dear {candidate_name},\n\n"
            f"{message}\n\n"
            f"Best regards,\n{recruiter_name}\n{company_name}\n{recruiter_email}"
        )

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
                reply_to=[recruiter_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

        except Exception as e:
            print(f"Error sending offer email: {str(e)}")
            return Response({
                "success": False,
                "message": "Something went wrong sending the offer email. Please try again.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

         
        try:
            application.status = "ACCEPTED"
            application.save()
        except Exception as db_err:
            return Response({
                "success": False,
                "message": "Offer email sent but failed to update application status.",
                "error": str(db_err)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "success": True,
            "message": "Offer email sent successfully and application accepted"
        }, status=status.HTTP_200_OK)
