from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Problem
from ..serializers import ProblemSerializer

import logging

logger = logging.getLogger(__name__)


class AdminProblemCreateView(APIView):
    def post(self, request):
        title = request.data.get('title')
        if title and Problem.objects.filter(title__iexact=title).exists():
            return Response({"message": "This problem is already added"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProblemUpdateView(APIView):
    def put(self, request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"error": "Problem not found"}, status=404)

        serializer = ProblemSerializer(problem, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})

        return Response(serializer.errors, status=400)


class ProblemDeleteView(APIView):
    def delete(self, request, problem_id):
        try:
            Problem.objects.get(id=problem_id).delete()
            return Response({"success": True})
        except Problem.DoesNotExist:
            return Response({"message": "Problem not found"}, status=404)


class ProblemToggleView(APIView):
    def patch(self, request, problem_id):
        try:
            problem = Problem.objects.get(id=problem_id)
            problem.is_active = not problem.is_active
            problem.save()

            serializer = ProblemSerializer(problem)
            return Response({
                "success": True,
                "message": f"Problem {'activated' if problem.is_active else 'deactivated'} successfully",
                "data": serializer.data
            })
        except Problem.DoesNotExist:
            return Response({
                "success": False,
                "message": "Problem not found"
            }, status=status.HTTP_404_NOT_FOUND)
