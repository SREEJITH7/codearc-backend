from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Problem, TestCases
from ..judge.dispatcher import dispatch
from ..judge.comparison import judge


class RunCodeView(APIView):
    def post(self, request):
        try:
            problem_id = request.data.get("problem_id")
            code = request.data.get("code")
            language = request.data.get("language")

            if not all([problem_id, code, language]):
                return Response({
                    "success": False,
                    "message": "Problem ID, code, and language are required"
                }, status=status.HTTP_400_BAD_REQUEST)

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
                testcases = TestCases.objects.filter(problem=problem).order_by("order")
            except Exception as e:
                logger.error(f"Error fetching test cases: {str(e)}")
                return Response({
                    "success": False,
                    "message": "Failed to fetch test cases"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                exec_result = dispatch(language, code, testcases, problem.function_name)
                results = judge(exec_result, testcases)
            except Exception as e:
                logger.error(f"Error during code execution: {str(e)}")
                return Response({
                    "success": False,
                    "message": "An error occurred during code execution",
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            error_msg = exec_result.error or ""
            
            if exec_result.error_type:
                error_msg = f"{exec_result.error_type}:\n{error_msg}"

            overall = "Accepted" if results and all(r["passed"] for r in results) else "Wrong Answer"
            if exec_result.error and not results:
                overall = "Error"

            return Response({
                "success": True,
                "overallStatus": overall,
                "testResults": results,
                "consoleOutput": exec_result.stdout,
                "error": error_msg,
                "memory": round(exec_result.memory, 2),
                "runtime": round(sum(exec_result.runtimes), 2)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "message": "An unexpected error occurred during code execution",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
