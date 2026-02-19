

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.recruiter_app.models import Application
from apps.recruiter_app.utils.coding_stats import (
    calculate_coding_stats,
    calculate_ranks_for_users
)

class RecruiterApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, application_id):
        try:
            application = Application.objects.select_related(
                "job", "user", "user__profile"
            ).get(
                id=application_id,
                job__recruiter=request.user
            )
        except Application.DoesNotExist:
            return Response(
                {"success": False, "message": "Application not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        coding_stats = {}
        rank = None

        if application.user:
            coding_stats = calculate_coding_stats(application.user)
            rank_map = calculate_ranks_for_users()
            rank = rank_map.get(application.user.id)

        profile_image = None
        if application.user and hasattr(application.user, 'profile') and application.user.profile.profileImage:
            profile_image = application.user.profile.profileImage.url

        return Response({
            "success" : True,
            "data": {
                "application":{
                    "id": application.id,
                    "status": application.status,
                    "created_at": application.created_at,

                    "job" : {
                        "id": application.job.id,
                        "title":application.job.title,
                        "location":application.job.location,
                    },

                    "applicant":{
                        "id":application.user.id if application.user else None,
                        "name": application.name,
                        "email":application.email,
                        "contactNo":application.contactNo,
                        "location": application.location,
                        "profileImage": profile_image,
                    },

                    "profile": {
                        "about": application.aboutYourself,
                        "skills": application.skills,
                        "education": application.education,
                        "experience": application.workExperience,
                    },

                    "codingStats":{
                        **coding_stats,
                        "rank": rank,
                    },

                    "resume" : application.resume.url if application.resume else None,
                    "certificates": {
                        "plusTwo": application.plusTwoCertificate.url if application.plusTwoCertificate else None,
                        "degree": application.degreeCertificate.url if application.degreeCertificate else None,
                        "pg": application.pgCertificate.url if application.pgCertificate else None,
                    },
                    "links": application.links,


                }
            }
        }, status= status.HTTP_200_OK) 
    

class RecruiterUpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, application_id):
        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {"success": False, "message": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = new_status.upper()

        if new_status == "ACCEPTED":
             return Response(
                {
                    "success": False,
                    "message": "Use Send Offer to accept an application"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in ["SHORTLISTED", "REJECTED"]:
            return Response(
                {"success": False, "message": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            application = Application.objects.get(
                id=application_id,
                job__recruiter=request.user
            )
        except Application.DoesNotExist:
            return Response(
                {"success": False, "message": "Application not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "message": "Database error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Allowed transitions at this endpoint
        valid_transitions = {
            "PENDING": ["SHORTLISTED", "REJECTED"],
            "SHORTLISTED": ["REJECTED"],
        }

        if (
            application.status not in valid_transitions or
            new_status not in valid_transitions[application.status]
        ):
            return Response(
                {
                    "success": False,
                    "message": "This action is not allowed at the current stage"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            application.status = new_status
            application.save()

            return Response(
                {
                    "success": True,
                    "message": f"Application {new_status.lower()} successfully"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to update application status",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    