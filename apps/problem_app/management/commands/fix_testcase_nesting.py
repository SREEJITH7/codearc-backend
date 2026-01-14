import json
from django.core.management.base import BaseCommand
from apps.problem_app.models import Problem, TestCases

class Command(BaseCommand):
    help = 'Fixes double-nested and stringified test case inputs (e.g., [[123]] -> [123], ["123"] -> [123])'

    def handle(self, *args, **options):
        problems = Problem.objects.all()
        fixed_count = 0

        for problem in problems:
            parameters = problem.parameters
            # Detect scalar parameter indices
            scalar_indices = []
            for i, param in enumerate(parameters):
                p_type = param.get('type', '').lower()
                is_array = '[]' in p_type or 'list' in p_type or 'array' in p_type
                if not is_array:
                    scalar_indices.append(i)

            testcases = problem.testcases.all()
            for tc in testcases:
                tc_input = tc.input
                modified = False

                if not isinstance(tc_input, list):
                    # If input itself is not a list, it's severely broken (must be list of args)
                    # We skip it or try to wrap it if it's a single value
                    continue

                for i in range(len(tc_input)):
                    val = tc_input[i]
                    
                    # 1. Try to parse if it's a string (fixes "123" -> 123)
                    if isinstance(val, str):
                        try:
                            parsed = json.loads(val.strip())
                            tc_input[i] = parsed
                            val = parsed
                            modified = True
                        except:
                            pass

                    # 2. Fix double-nesting if it's a scalar parameter but we have a list of length 1
                    if i in scalar_indices:
                        if isinstance(val, list) and len(val) == 1:
                            tc_input[i] = val[0]
                            modified = True
                        elif isinstance(val, list) and len(val) > 1:
                            # This is likely a valid error where user passed a list to a non-list param
                            # We leave it for manual fix as it's ambiguous
                            pass

                if modified:
                    tc.input = tc_input
                    tc.save()
                    fixed_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Fixed testcase {tc.id} for problem: {problem.title} -> {tc_input}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} test cases.'))
