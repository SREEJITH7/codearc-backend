import subprocess
import tempfile
import os
import json
from .execution_base import ExecutionResult

def _to_java_literal(val):
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, str):
        safe = val.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe}"'
    if isinstance(val, list):
        if not val:
            return "new int[]{}"
        first = val[0]
        if isinstance(first, int):
            return f"new int[]{{{','.join(map(str, val))}}}"
        if isinstance(first, str):
            contents = ','.join([_to_java_literal(x) for x in val])
            return f"new String[]{{{contents}}}"
        contents = ','.join([_to_java_literal(x) for x in val])
        return f"new Object[]{{{contents}}}"
    return str(val)

def run_java(user_code, testcases, function_name):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            java_solution_file = os.path.join(tmpdir, "Solution.java")
            with open(java_solution_file, "w") as f:
                f.write("import java.util.*;\nimport java.util.stream.*;\n" + user_code)
            
            java_runner_file = os.path.join(tmpdir, "Runner.java")
            with open(java_runner_file, "w") as f:
                f.write(f"""
import java.util.*;
import java.util.stream.*;

public class Runner {{
    public static void main(String[] args) {{
        Solution sol = new Solution();
        String DELIM = "---RESULT_JSON_START---";
        System.out.println(DELIM);
        
        try {{
""")
                for tc in testcases:
                    args_str = [_to_java_literal(arg) for arg in tc.input]
                    f.write(f"""
            {{
                long start = System.nanoTime();
                Object res = sol.{function_name}({", ".join(args_str)});
                long end = System.nanoTime();
                System.out.print("RES:");
                if (res instanceof int[]) System.out.println(Arrays.toString((int[])res));
                else if (res instanceof long[]) System.out.println(Arrays.toString((long[])res));
                else if (res instanceof float[]) System.out.println(Arrays.toString((float[])res));
                else if (res instanceof double[]) System.out.println(Arrays.toString((double[])res));
                else if (res instanceof boolean[]) System.out.println(Arrays.toString((boolean[])res));
                else if (res instanceof String[]) System.out.println(Arrays.toString((String[])res));
                else if (res instanceof Object[]) System.out.println(Arrays.deepToString((Object[])res));
                else System.out.println(res);
                System.out.println("TIME:" + (end - start) / 1e6);
            }}
""")
                f.write("""
        } catch (Throwable e) {
            System.out.println("ERR:" + e.toString());
        }
    }
}
""")

            compile_process = subprocess.run(
                ["javac", "Solution.java", "Runner.java"],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            
            if compile_process.returncode != 0:
                return ExecutionResult(error=compile_process.stderr, error_type="Compilation Error")

            run_process = subprocess.run(
                ["java", "Runner"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=5
            )

            if run_process.stderr:
                return ExecutionResult(error=run_process.stderr, error_type="Runtime Error")

            full_stdout = run_process.stdout
            if "---RESULT_JSON_START---" not in full_stdout:
                return ExecutionResult(error="Judge failed to produce output", error_type="Internal Error")

            parts = full_stdout.split("---RESULT_JSON_START---")
            stdout = parts[0].strip()
            lines = parts[1].strip().split("\n")
            
            outputs = []
            runtimes = []
            for line in lines:
                if line.startswith("RES:"):
                    val = line[4:].strip()
                    if val.startswith("[") and val.endswith("]"):
                        try: val = json.loads(val)
                        except: pass
                    elif val == "true": val = True
                    elif val == "false": val = False
                    elif val == "null": val = None
                    outputs.append(val)
                elif line.startswith("ERR:"):
                     return ExecutionResult(error=line[4:].strip(), error_type="Runtime Error")
                elif line.startswith("TIME:"):
                    try: runtimes.append(float(line[5:].strip()))
                    except: runtimes.append(0.0)

            return ExecutionResult(outputs=outputs, runtimes=runtimes, stdout=stdout)
    except subprocess.TimeoutExpired:
        return ExecutionResult(error="Execution timed out", error_type="Timeout Error")
    except Exception as e:
        return ExecutionResult(error=str(e), error_type="Runtime Error")
