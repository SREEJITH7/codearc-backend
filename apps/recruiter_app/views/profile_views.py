from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from apps.auth_app.models import RecruiterProfile
from apps.recruiter_app.serializers.recruiter_profile_serializer import RecruiterProfileSerializer

class RecruiterProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            recruiter = RecruiterProfile.objects.get(user = request.user)
            serializer = RecruiterProfileSerializer(recruiter)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except RecruiterProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Recruiter profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "message": "Failed to fetch profile", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def patch(self, request):
        try:
            profile = RecruiterProfile.objects.get(user = request.user)
            serializer = RecruiterProfileSerializer(               
                profile, data = request.data, partial=True)
            
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response({
                        "success" : True,
                        "profile" : serializer.data
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response(
                        {"success": False, "message": "Failed to save profile changes", "error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except RecruiterProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Recruiter profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"success": False, "message": "An error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )