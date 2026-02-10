from .python_runner import run_python
from .js_runner import run_js
from .java_runner import run_java
from .cpp_runner import run_cpp

def dispatch(language, code, testcases, fn):
    lang = language.lower()
    if lang == "python": return run_python(code,testcases,fn)
    if lang == "javascript": return run_js(code,testcases,fn)
    if lang == "java": return run_java(code,testcases,fn)
    if lang == "cpp": return run_cpp(code,testcases,fn)
    raise ValueError("Unsupported language")
