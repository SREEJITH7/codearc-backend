import subprocess
import tempfile
import json
import os

def run_python_code(user_code, testcases, function_name):
    results = []
    console_output = ""

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
            return [], process.stderr, 0.0

        full_stdout = process.stdout
        if "---RESULT_JSON_START---" not in full_stdout:
            return [], "Judge failed to produce output", 0.0

        parts = full_stdout.split("---RESULT_JSON_START---")
        console_output = parts[0].strip()
        output_data = json.loads(parts[1].strip())

        output_results = output_data.get("results", [])
        output_runtimes = output_data.get("runtimes", [])
        peak_memory = output_data.get("peak_memory", 0.0)

        for i, tc in enumerate(testcases):
            expected = tc.expected_output
            if isinstance(expected, str):
                try: expected = json.loads(expected)
                except: pass

            actual = output_results[i] if i < len(output_results) else None
            runtime = output_runtimes[i] if i < len(output_runtimes) else 0.0
            passed = (actual == expected) if actual is not None else False

            results.append({
                "input": tc.input,
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "runtime": runtime
            })
        return results, console_output, peak_memory

    except Exception as e:
        return [], str(e), 0.0
    finally:
        if os.path.exists(file_path): os.remove(file_path)


def run_js_code(user_code, testcases, function_name):
    results = []
    console_output = ""

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
            return [], process.stderr, 0.0

        full_stdout = process.stdout
        if "---RESULT_JSON_START---" not in full_stdout:
            return [], "Judge failed to produce output", 0.0

        parts = full_stdout.split("---RESULT_JSON_START---")
        console_output = parts[0].strip()
        output_data = json.loads(parts[1].strip())
        
        output_results = output_data.get("results", [])
        output_runtimes = output_data.get("runtimes", [])
        peak_memory = output_data.get("peak_memory", 0.0)

        for i, tc in enumerate(testcases):
            expected = tc.expected_output
            if isinstance(expected, str):
                try: expected = json.loads(expected)
                except: pass

            actual = output_results[i] if i < len(output_results) else None
            runtime = output_runtimes[i] if i < len(output_runtimes) else 0.0
            passed = (actual == expected) if actual is not None else False

            results.append({
                "input": tc.input,
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "runtime": runtime
            })
        return results, console_output, peak_memory

    except Exception as e:
        return [], str(e), 0.0
    finally:
        if os.path.exists(file_path): os.remove(file_path)

def _to_java_literal(val):
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, str):
        safe = val.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe}"'
    if isinstance(val, list):
        if not val:
            return "new Object[]{}"
        first = val[0]
        if isinstance(first, int):
            return f"new int[]{{{','.join(map(str, val))}}}"
        if isinstance(first, str):
            contents = ','.join([_to_java_literal(x) for x in val])
            return f"new String[]{{{contents}}}"
        contents = ','.join([_to_java_literal(x) for x in val])
        return f"new Object[]{{{contents}}}"
    return str(val)

def run_java_code(user_code, testcases, function_name):
    # LeetCode Style: user code contains class Solution. We provide a separate Runner.
    results = []
    console_output = ""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save user code exactly as provided (must contain class Solution)
        java_solution_file = os.path.join(tmpdir, "Solution.java")
        with open(java_solution_file, "w") as f:
            f.write(user_code)
        
        # Save independent Runner to invoke Solution
        java_runner_file = os.path.join(tmpdir, "Runner.java")
        with open(java_runner_file, "w") as f:
            f.write(f"""
import java.util.*;

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
        } catch (Exception e) {
            System.out.println("ERR:" + e.getMessage());
        }
    }
}
""")

        # Compile both files
        compile_process = subprocess.run(
            ["javac", "Solution.java", "Runner.java"],
            cwd=tmpdir,
            capture_output=True,
            text=True
        )
        
        if compile_process.returncode != 0:
            return [], f"Compilation Error:\\n{compile_process.stderr}", 0.0

        # Run the Runner
        run_process = subprocess.run(
            ["java", "Runner"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=5
        )

        if run_process.stderr:
            return [], run_process.stderr, 0.0

        full_stdout = run_process.stdout
        if "---RESULT_JSON_START---" not in full_stdout:
            return [], "Judge failed to produce output", 0.0

        parts = full_stdout.split("---RESULT_JSON_START---")
        console_output = parts[0].strip()
        lines = parts[1].strip().split("\n")
        
        parsed_results = []
        parsed_runtimes = []
        for line in lines:
            if line.startswith("RES:"):
                val = line[4:].strip()
                if val.startswith("[") and val.endswith("]"):
                    try: val = json.loads(val)
                    except: pass
                parsed_results.append(val)
            elif line.startswith("TIME:"):
                try: parsed_runtimes.append(float(line[5:].strip()))
                except: parsed_runtimes.append(0.0)

        for i, tc in enumerate(testcases):
            expected = tc.expected_output
            if isinstance(expected, str):
                try: expected = json.loads(expected)
                except: pass

            actual = parsed_results[i] if i < len(parsed_results) else None
            runtime = parsed_runtimes[i] if i < len(parsed_runtimes) else 0.0
            
            is_passed = str(actual).replace(" ", "") == str(expected).replace(" ", "")
            if isinstance(actual, (list, int, str, bool, float)) and isinstance(expected, (list, int, str, bool, float)):
                is_passed = actual == expected

            results.append({
                "input": tc.input,
                "expected": expected,
                "actual": actual,
                "passed": is_passed,
                "runtime": runtime
            })

    return results, console_output, 0.0

def _to_cpp_literal(val):
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, str):
        safe = val.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe}"'
    if isinstance(val, list):
        contents = ','.join([_to_cpp_literal(x) for x in val])
        return f"{{ {contents} }}"
    return str(val)

def run_cpp_code(user_code, testcases, function_name):
    # LeetCode Style: user code contains class Solution. Backend appends main.
    results = []
    console_output = ""

    with tempfile.TemporaryDirectory() as tmpdir:
        cpp_file = os.path.join(tmpdir, "solution.cpp")
        binary_file = os.path.join(tmpdir, "solution")
        if os.name == 'nt':
            binary_file += ".exe"
        
        test_calls = []
        for tc in testcases:
            args_str = [_to_cpp_literal(arg) for arg in tc.input]
            test_calls.append(f"""
            {{
                auto start = std::chrono::high_resolution_clock::now();
                auto res = sol.{function_name}({", ".join(args_str)});
                auto end = std::chrono::high_resolution_clock::now();
                auto duration = std::chrono::duration<double, std::milli>(end - start).count();
                std::cout << "RES:";
                print_res(res);
                std::cout << std::endl;
                std::cout << "TIME:" << duration << std::endl;
            }}
            """)

        with open(cpp_file, "w") as f:
            f.write(f"""
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>

using namespace std;

// --- USER CODE START ---
{user_code}
// --- USER CODE END ---

// Helper to print results
void print_res(int v) {{ std::cout << v; }}
void print_res(long long v) {{ std::cout << v; }}
void print_res(double v) {{ std::cout << v; }}
void print_res(const std::string& v) {{ std::cout << v; }}
void print_res(bool v) {{ std::cout << (v ? "true" : "false"); }}
template<typename T>
void print_res(const std::vector<T>& v) {{
    std::cout << "[";
    for(size_t i=0; i<v.size(); ++i) {{
        print_res(v[i]);
        if(i < v.size()-1) std::cout << ",";
    }}
    std::cout << "]";
}}

int main() {{
    Solution sol;
    std::cout << "---RESULT_JSON_START---" << std::endl;
    {" ".join(test_calls)}
    return 0;
}}
""")

        # Compile
        compile_cmd = ["g++", "solution.cpp", "-o", "solution"]
        compile_process = subprocess.run(
            compile_cmd,
            cwd=tmpdir,
            capture_output=True,
            text=True
        )

        if compile_process.returncode != 0:
            return [], f"Compilation Error:\\n{compile_process.stderr}", 0.0

        # Run
        run_process = subprocess.run(
            [binary_file],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=5
        )

        if run_process.stderr:
            return [], run_process.stderr, 0.0

        full_stdout = run_process.stdout
        if "---RESULT_JSON_START---" not in full_stdout:
            return [], "Judge failed to produce output", 0.0

        parts = full_stdout.split("---RESULT_JSON_START---")
        console_output = parts[0].strip()
        lines = parts[1].strip().split("\n")
        
        parsed_results = []
        parsed_runtimes = []
        for line in lines:
            if line.startswith("RES:"):
                val = line[4:].strip()
                if val.startswith("[") and val.endswith("]"):
                    try: val = json.loads(val)
                    except: pass
                parsed_results.append(val)
            elif line.startswith("TIME:"):
                try: parsed_runtimes.append(float(line[5:].strip()))
                except: parsed_runtimes.append(0.0)

        for i, tc in enumerate(testcases):
            expected = tc.expected_output
            if isinstance(expected, str):
                try: expected = json.loads(expected)
                except: pass

            actual = parsed_results[i] if i < len(parsed_results) else None
            runtime = parsed_runtimes[i] if i < len(parsed_runtimes) else 0.0
            
            is_passed = str(actual).replace(" ", "") == str(expected).replace(" ", "")
            if isinstance(actual, (list, int, str, bool, float)) and isinstance(expected, (list, int, str, bool, float)):
                is_passed = actual == expected

            results.append({
                "input": tc.input,
                "expected": expected,
                "actual": actual,
                "passed": is_passed,
                "runtime": runtime
            })

    return results, console_output, 0.0

def run_code(language, user_code, testcases, function_name):
    lang = language.lower()
    if lang == "python":
        return run_python_code(user_code, testcases, function_name)
    elif lang == "javascript":
        return run_js_code(user_code, testcases, function_name)
    elif lang == "java":
        return run_java_code(user_code, testcases, function_name)
    elif lang == "cpp":
        return run_cpp_code(user_code, testcases, function_name)
    else:
        return [], f"Unsupported language: {language}", 0.0
