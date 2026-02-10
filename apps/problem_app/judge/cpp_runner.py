import subprocess
import tempfile
import os
import json
from .execution_base import ExecutionResult

def _to_cpp_literal(val):
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, str):
        safe = val.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{safe}"'
    if isinstance(val, list):
        if not val:
            # Empty list is ambiguous, but usually vector<int> in these problems
            return "std::vector<int>{}" 
        
        contents = ','.join([_to_cpp_literal(x) for x in val])
        first = val[0]
        if isinstance(first, int):
            return f"std::vector<int>{{ {contents} }}"
        if isinstance(first, str):
            return f"std::vector<std::string>{{ {contents} }}"
        if isinstance(first, bool):
             return f"std::vector<bool>{{ {contents} }}"
        # Fallback for nested vectors or other types could be added here
        return f"{{ {contents} }}"
    return str(val)

def run_cpp(user_code, testcases, function_name):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            cpp_file = os.path.join(tmpdir, "solution.cpp")
            binary_file = os.path.join(tmpdir, "solution")
            if os.name == 'nt':
                binary_file += ".exe"
            
            test_calls = []
            for tc in testcases:
                args_str = [_to_cpp_literal(arg) for arg in tc.input]
                args_decl = ""
                arg_names = []
                for idx, arg in enumerate(args_str):
                    var_name = f"arg{idx}"
                    args_decl += f"auto {var_name} = {arg};\n"
                    arg_names.append(var_name)
                
                test_calls.append(f"""
                {{
                    auto start = std::chrono::high_resolution_clock::now();
                    {args_decl}
                    auto res = sol.{function_name}({", ".join(arg_names)});
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

            compile_cmd = ["g++", "solution.cpp", "-o", "solution"]
            compile_process = subprocess.run(
                compile_cmd,
                cwd=tmpdir,
                capture_output=True,
                text=True
            )

            if compile_process.returncode != 0:
                return ExecutionResult(error=compile_process.stderr, error_type="Compilation Error")

            run_process = subprocess.run(
                [binary_file],
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
                    outputs.append(val)
                elif line.startswith("TIME:"):
                    try: runtimes.append(float(line[5:].strip()))
                    except: runtimes.append(0.0)

            return ExecutionResult(outputs=outputs, runtimes=runtimes, stdout=stdout)
    except subprocess.TimeoutExpired:
        return ExecutionResult(error="Execution timed out", error_type="Timeout Error")
    except Exception as e:
        return ExecutionResult(error=str(e), error_type="Runtime Error")
