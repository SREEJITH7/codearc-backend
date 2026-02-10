from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Problem, TestCases
from ..judge.dispatcher import dispatch
from ..judge.comparison import judge


class RunCodeView(APIView):
    def post(self, request):
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language")

        if not all([problem_id, code, language]):
            return Response({"message": "Missing fields"}, status=400)

        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return Response({"message": "Problem not found"}, status=404)

        testcases = TestCases.objects.filter(problem=problem).order_by("order")

        exec_result = dispatch(language, code, testcases, problem.function_name)
        results = judge(exec_result, testcases)

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
        })
