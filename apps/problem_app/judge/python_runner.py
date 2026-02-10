import subprocess
import tempfile
import json
import os
from .execution_base import ExecutionResult

def run_python(user_code, testcases, function_name):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        file_path = f.name
        f.write(user_code.encode())
        f.write(b"\n\n")
        f.write(b"""
import json
import time
import tracemalloc

tracemalloc.start()

RESULT_DELIMITER = '---RESULT_JSON_START---'
results = []
runtimes = []

testcases = []
""")
        for tc in testcases:
            f.write(f"testcases.append({tc.input})\n".encode())

        f.write(f"""
for args in testcases:
    start = time.perf_counter()
    try:
        if isinstance(args, list):
            res = {function_name}(*args)
        else:
            res = {function_name}(args)
    except Exception as e:
        res = str(e)
    end = time.perf_counter()

    results.append(res)
    runtimes.append((end - start) * 1000)

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(RESULT_DELIMITER)
print(json.dumps({{
    "results": results,
    "runtimes": runtimes,
    "peak_memory": peak / 1024 / 1024
}}))
""".encode())

    try:
        process = subprocess.run(
            ["python", file_path],
            capture_output=True,
            text=True,
            timeout=5
        )

        if process.stderr:
            return ExecutionResult(error=process.stderr, error_type="Runtime Error")

        full_stdout = process.stdout
        if "---RESULT_JSON_START---" not in full_stdout:
            return ExecutionResult(error="Judge failed to produce output", error_type="Internal Error")

        parts = full_stdout.split("---RESULT_JSON_START---")
        stdout = parts[0].strip()
        
        try:
            data = json.loads(parts[1].strip())
            return ExecutionResult(
                outputs=data.get("results", []),
                runtimes=data.get("runtimes", []),
                memory=data.get("peak_memory", 0.0),
                stdout=stdout
            )
        except (json.JSONDecodeError, KeyError) as e:
            return ExecutionResult(error=f"Failed to parse results: {str(e)}", error_type="Internal Error", stdout=stdout)

    except subprocess.TimeoutExpired:
        return ExecutionResult(error="Execution timed out", error_type="Timeout Error")
    except Exception as e:
        return ExecutionResult(error=str(e), error_type="Runtime Error")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
