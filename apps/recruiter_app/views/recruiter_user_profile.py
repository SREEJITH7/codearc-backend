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
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"success": False, "message": "User not found"},
                    status= status.HTTP_404_NOT_FOUND
                )
            
            try:
                coding_stats = calculate_coding_stats(user)
                rank_map = calculate_ranks_for_users()
            except Exception as stats_err:
                print(f"Error calculating stats for user {user_id}: {stats_err}")
                coding_stats = {}
                rank_map = {}

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
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred fetching user profile",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





