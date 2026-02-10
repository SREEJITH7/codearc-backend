from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.recruiter_app.models import Application
from apps.recruiter_app.utils.coding_stats import (
    calculate_coding_stats,
    calculate_ranks_for_users
)

from django.contrib.auth import get_user_model


class RecruiterUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request , user_id):
        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found"},
                status= status.HTTP_404_NOT_FOUND
            )
        
        coding_stats = calculate_coding_stats(user)
        rank_map = calculate_ranks_for_users()

        return Response({
            "success" : True,
            "data":{
                "id": user.id,
                "name" : user.get_full_name() or user.username,
                "email": user.email,
                "codingStats": {
                    **coding_stats,
                    "rank": rank_map.get(user.id)
                }
            }
        }, status = status.HTTP_200_OK)





