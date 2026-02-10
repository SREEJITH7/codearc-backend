import subprocess
import tempfile
import json
import os
from .execution_base import ExecutionResult

def run_js(user_code, testcases, function_name):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as f:
        file_path = f.name
        f.write(user_code.encode())
        f.write(b"\n\n")
        f.write(f"""
const RESULT_DELIMITER = '---RESULT_JSON_START---';
const testcases = {json.dumps([tc.input for tc in testcases])};
const results = [];
const runtimes = [];

testcases.forEach(args => {{
    const start = performance.now();
    try {{
        const res = {function_name}(...args);
        results.push(res);
    }} catch (e) {{
        results.push(e.message);
    }}
    const end = performance.now();
    runtimes.push(end - start);
}});

process.stdout.write("\\n" + RESULT_DELIMITER + "\\n");
process.stdout.write(JSON.stringify({{
    results: results,
    runtimes: runtimes,
    peak_memory: process.memoryUsage().heapUsed / 1024 / 1024
}}));
""".encode())

    try:
        process = subprocess.run(
            ["node", file_path],
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
