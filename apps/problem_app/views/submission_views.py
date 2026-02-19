from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Problem, Submission, TestCases
from ..judge.dispatcher import dispatch
from ..judge.comparison import judge


class SubmitCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            problem_id = request.data.get("problem_id")
            code = request.data.get("code")
            language = request.data.get("language")

            if not all([problem_id, code, language]):
                return Response({
                    "success": False,
                    "message": "Problem ID, code, and language are required"
                }, status=400)

            try:
                problem = Problem.objects.get(id=problem_id)
            except Problem.DoesNotExist:
                return Response({"success": False, "message": "Problem not found"}, status=404)
            except (ValueError, TypeError):
                return Response({"success": False, "message": "Invalid problem ID format"}, status=400)

            testcases = TestCases.objects.filter(problem=problem)

            try:
                exec_result = dispatch(language, code, testcases, problem.function_name)
                results = judge(exec_result, testcases)
            except Exception as judge_err:
                print(f"Code execution or judging error: {judge_err}")
                return Response({
                    "success": False,
                    "message": "Error during code execution",
                    "error": str(judge_err)
                }, status=500)

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

            try:
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
            except Exception as sub_err:
                print(f"Failed to create submission record: {sub_err}")
                return Response({
                    "success": False,
                    "message": "Failed to save submission record",
                    "error": str(sub_err)
                }, status=500)

            try:
                problem.total_submissions += 1
                if status_value == "Accepted":
                    problem.accepted_submissions += 1
                problem.save()
            except Exception as prob_save_err:
                print(f"Failed to update problem stats: {prob_save_err}")

            try:
                all_submissions = Submission.objects.filter(problem=problem, status="Accepted")
                total_accepted = all_submissions.count()
                
                runtime_percentile = 100.0
                memory_percentile = 100.0
                
                if total_accepted > 1:
                    slower_submissions = all_submissions.filter(runtime__gt=total_runtime).count()
                    runtime_percentile = round((slower_submissions / total_accepted) * 100, 2)
                    
                    larger_memory = all_submissions.filter(memory__gt=memory_usage).count()
                    memory_percentile = round((larger_memory / total_accepted) * 100, 2)
            except Exception as stats_err:
                print(f"Error calculating percentiles: {stats_err}")
                runtime_percentile = 100.0
                memory_percentile = 100.0

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
        except Exception as e:
            return Response({
                "success": False,
                "message": "An unexpected error occurred during submission",
                "error": str(e)
            }, status=500)


class UserSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, problem_id):
        try:
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
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to fetch user submissions",
                "error": str(e)
            }, status=500)


class AllSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, problem_id):
        try:
            submissions = Submission.objects.filter(problem_id=problem_id, status="Accepted")
            return Response({"success": True, "data": submissions.values()})
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to fetch all submissions",
                "error": str(e)
            }, status=500)
