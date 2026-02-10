from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Problem, Submission, TestCases
from ..judge.dispatcher import dispatch
from ..judge.comparison import judge


class SubmitCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language")

        problem = Problem.objects.get(id=problem_id)
        testcases = TestCases.objects.filter(problem=problem)

        exec_result = dispatch(language, code, testcases, problem.function_name)
        results = judge(exec_result, testcases)

        if not results and exec_result.error:
            status_value = exec_result.error_type if exec_result.error_type else "Runtime Error"
            passed = 0
            total = testcases.count()
            total_runtime = 0.0
            memory_usage = 0.0
        else:
            passed = sum(1 for r in results if r.get("passed", False))
            total = len(results)
            total_runtime = sum(r.get("runtime", 0.0) for r in results)
            status_value = "Accepted" if passed == total else "Wrong Answer"
            memory_usage = exec_result.memory

        
        submission = Submission.objects.create(
            user=user,
            problem=problem,
            language=language,
            code=code,
            status=status_value,
            passed_count=passed,
            total_count=total,
            runtime=total_runtime,
            memory=memory_usage,
        )

        
        problem.total_submissions += 1
        if status_value == "Accepted":
            problem.accepted_submissions += 1
        problem.save()

       
        all_submissions = Submission.objects.filter(problem=problem, status="Accepted")
        total_accepted = all_submissions.count()
        
        runtime_percentile = 100.0
        memory_percentile = 100.0
        
        if total_accepted > 1:
            slower_submissions = all_submissions.filter(runtime__gt=total_runtime).count()
            runtime_percentile = round((slower_submissions / total_accepted) * 100, 2)
            
            larger_memory = all_submissions.filter(memory__gt=memory_usage).count()
            memory_percentile = round((larger_memory / total_accepted) * 100, 2)

        error_msg = exec_result.error or ""
        if exec_result.error_type and exec_result.error:
            error_msg = f"{exec_result.error_type}:\n{error_msg}"

        return Response({
            "success": True,
            "submission_id": submission.id,
            "overallStatus": status_value,
            "passed": passed,
            "total": total,
            "runtime": round(total_runtime, 2),
            "memory": round(memory_usage, 2),
            "runtime_percentile": runtime_percentile,
            "memory_percentile": memory_percentile,
            "consoleOutput": exec_result.stdout,
            "error": error_msg,
            "testResults": results
        })


class UserSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, problem_id):
        submissions = Submission.objects.filter(
            user=request.user, problem_id=problem_id
        ).order_by("-created_at")

        data = [{
            "id": s.id,
            "status": s.status,
            "runtime": s.runtime,
            "memory": s.memory,
            "language": s.language,
            "code": s.code,
            "created_at": s.created_at
        } for s in submissions]

        return Response({"success": True, "data": data})


class AllSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, problem_id):
        submissions = Submission.objects.filter(problem_id=problem_id, status="Accepted")
        return Response({"success": True, "data": submissions.values()})
