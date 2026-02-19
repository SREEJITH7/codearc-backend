from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from apps.recruiter_app.models import Application

class RecruiterSendOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, application_id):
        try:
             application = Application.objects.select_related('job', 'user').get(
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

        try:
             
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [application.email],
                fail_silently=False,
            )

             
            application.status = "ACCEPTED"
            application.save()

            return Response({
                "success": True,
                "message": "Offer email sent successfully and application accepted"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error sending offer email: {str(e)}")
            return Response({
                "success": False,
                "message": "Something went wrong sending the offer email. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
