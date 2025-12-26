from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.auth_app.models import RecruiterProfile
# from recruiter_app.serializers.recruiter_profile_serializer import RecruiterProfileSerializer
from apps.recruiter_app.serializers.recruiter_profile_serializer import RecruiterProfileSerializer

class RecruiterProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            recruiter = RecruiterProfile.objects.get(user = request.user)
            serializer = RecruiterProfileSerializer(recruiter)
            return Response(serializer.data, status = 200)
        except RecruiterProfile.DoesNotExist:
            return Response(
                {"message": "Recruiter profile not found"},
                status=404
            )
        
    def patch(self, request):
        profile = RecruiterProfile.objects.get(user = request.user)
        serializer = RecruiterProfileSerializer(               
            profile, data = request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success" : True,
                "profile" : serializer.data
            })

        return Response(serializer.errors, status=400)