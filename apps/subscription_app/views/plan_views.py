from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.subscription_app.models import Plan
from apps.subscription_app.serializers.plan_serializer import PlanSerializer


class ListPlansView(APIView):
  
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.query_params.get('role', '').upper()

        plans = Plan.objects.filter(is_active=True)
        if role in ['USER', 'RECRUITER']:
            plans = plans.filter(role_type=role)

        serializer = PlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)