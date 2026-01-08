from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from apps.auth_app.models import UserProfile
from apps.user_app.serializers.profile_serializer import (
    UserProfileUpdateSerializer
)

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, user_id):
        if request.user.id != user_id:
            return Response(
                {"detail": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )
        # response = Response()
        # response["Allow"] = "GE T, POST, PUT, PATCH, DELETE, OPTIONS"

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        serializer = UserProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "profile": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)