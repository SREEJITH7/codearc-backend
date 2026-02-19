from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Problem
from ..serializers import ProblemSerializer

import logging

logger = logging.getLogger(__name__)


class AdminProblemCreateView(APIView):
    def post(self, request):
        try:
            title = request.data.get('title')
            try:
                if title and Problem.objects.filter(title__iexact=title).exists():
                    return Response({
                        "success": False,
                        "message": "This problem title already exists"
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error checking for existing problem title: {str(e)}")

            serializer = ProblemSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response({
                        "success": True,
                        "data": serializer.data
                    }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.error(f"Error saving new problem: {str(e)}")
                    return Response({
                        "success": False,
                        "message": "Failed to save the new problem"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            logger.error(f"Problem creation validation failed: {serializer.errors}")
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An unexpected error occurred during problem creation",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProblemUpdateView(APIView):
    def put(self, request, problem_id):
        try:
            try:
                problem = Problem.objects.get(id=problem_id)
            except Problem.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Problem not found"
                }, status=status.HTTP_404_NOT_FOUND)
            except (ValueError, TypeError):
                 return Response({
                    "success": False,
                    "message": "Invalid problem ID format"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = ProblemSerializer(problem, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response({
                        "success": True,
                        "data": serializer.data
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"Error updating problem ID {problem_id}: {str(e)}")
                    return Response({
                        "success": False,
                        "message": "Failed to update problem"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An unexpected error occurred during problem update",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProblemDeleteView(APIView):
    def delete(self, request, problem_id):
        try:
            try:
                problem = Problem.objects.get(id=problem_id)
            except Problem.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Problem not found"
                }, status=status.HTTP_404_NOT_FOUND)
            except (ValueError, TypeError):
                return Response({
                    "success": False,
                    "message": "Invalid problem ID format"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                problem.delete()
                return Response({
                    "success": True,
                    "message": "Problem deleted successfully"
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error deleting problem ID {problem_id}: {str(e)}")
                return Response({
                    "success": False,
                    "message": "Failed to delete problem"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An unexpected error occurred during problem deletion",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProblemToggleView(APIView):
    def patch(self, request, problem_id):
        try:
            try:
                problem = Problem.objects.get(id=problem_id)
            except Problem.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Problem not found"
                }, status=status.HTTP_404_NOT_FOUND)
            except (ValueError, TypeError):
                 return Response({
                    "success": False,
                    "message": "Invalid problem ID format"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                problem.is_active = not problem.is_active
                problem.save()

                serializer = ProblemSerializer(problem)
                return Response({
                    "success": True,
                    "message": f"Problem {'activated' if problem.is_active else 'deactivated'} successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error toggling problem status ID {problem_id}: {str(e)}")
                return Response({
                    "success": False,
                    "message": "Failed to toggle problem status"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An unexpected error occurred during problem status toggle",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
