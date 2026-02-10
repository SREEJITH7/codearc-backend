# Normalize outputs from different languages
# Compare actual vs expected safely
# Generate per-testcase judge results

import json

def _normalize(val):
    if val is None:
        return None
    
     
    if isinstance(val, (bool, int, float, list, dict)):
        if isinstance(val, list):
            return [_normalize(x) for x in val]
        return val
    
     
    if isinstance(val, str):
        val_stripped = val.strip()
        if val_stripped.lower() == "true": return True
        if val_stripped.lower() == "false": return False
        
        try:
            parsed = json.loads(val_stripped)
            return _normalize(parsed)  
        except:
            return val_stripped 
            
    return val

def compare(actual, expected):
    norm_actual = _normalize(actual)
    norm_expected = _normalize(expected)
    
    return str(norm_actual).replace(" ", "") == str(norm_expected).replace(" ", "")

def judge(exec_result, testcases):
    results = []
    if exec_result.error and not exec_result.outputs:
        for tc in testcases:
            results.append({
                "input": tc.input,
                "expected": tc.expected_output,
                "actual": None,
                "passed": False,
                "runtime": 0,
                "error": exec_result.error,
                "error_type": exec_result.error_type
            })
        return results

    for i, tc in enumerate(testcases):
        actual = exec_result.outputs[i] if i < len(exec_result.outputs) else None
        passed = compare(actual, tc.expected_output)
        
        results.append({
            "input": tc.input,
            "expected": tc.expected_output,
            "actual": actual,
            "passed": passed,
            "runtime": exec_result.runtimes[i] if i < len(exec_result.runtimes) else 0,
            "error": exec_result.error if not passed and i >= len(exec_result.outputs) else None
        })
    return results
