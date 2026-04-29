"""
MCP Code Executor (Upgraded for LeetCode + CF)

Supports both:
1. LeetCode-style: (class Solution: def methodName(self, ...))
   - Dynamically finds the method name.
   - Parses 'input' as a JSON object of arguments.
2. Codeforces-style: (reads from sys.stdin)
   - Passes 'input' as a raw string to stdin.
"""

import subprocess
import tempfile
import os
import sys
import json
import re
from typing import List, Dict, Any

# ===============================================================
# 🔥 Run Python code with CF-style stdin → stdout capture
# ===============================================================
def run_python_code_return_output(code: str, stdin_data: str = "", timeout: int = 5):
    """
    Writes code to a temporary file and runs it using system Python.
    Captures stdout & stderr.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        fname = f.name

    try:
        proc = subprocess.run(
            [sys.executable, fname],
            input=stdin_data.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")
        return stdout, stderr, proc.returncode

    except subprocess.TimeoutExpired:
        return "", f"Timeout after {timeout} seconds", -1
    finally:
        try:
            os.unlink(fname)
        except:
            pass

# ===============================================================
# 🔥 Helper to build a dynamic test driver
# ===============================================================
def build_leetcode_driver(code: str, method_name: str, input_args: Dict[str, Any]) -> str:
    """
    Appends a driver script to the LeetCode code.
    """
    # We must import all libraries the user's code might need
    driver = f"""
import sys
import json
import math
import heapq
from collections import *

# --- User's Code ---
{code}
# --- End User's Code ---

try:
    # 1. Instantiate the class
    sol = Solution()
    
    # 2. Prepare the arguments from the JSON object
    args = {json.dumps(input_args)}
    
    # 3. Call the method by name with unpacked arguments
    result = sol.{method_name}(**args)
    
    # 4. Print the result to stdout
    # (Use json.dumps for complex types like lists, etc.)
    if isinstance(result, (str, int, float, bool, list, dict)) or result is None:
        print(json.dumps(result))
    else:
        print(str(result))

except Exception as e:
    # Print any runtime errors to stderr
    import traceback
    print(f"Execution Error: {{e}}\\n{{traceback.format_exc()}}", file=sys.stderr)
"""
    return driver

# ===============================================================
# 🔥 NEW GENERAL-PURPOSE VALIDATOR
# ===============================================================
def validate_code_against_tests(code: str, tests: List[Dict[str, Any]]):
    """
    Validates EITHER CF-style OR LeetCode-style solutions.
    """
    results = []
    FLOAT_TOLERANCE = 1e-5

    # --- Detect solution type ---
    is_leetcode_style = "class Solution" in code and "sys.stdin" not in code
    method_name = None

    if is_leetcode_style:
        # Try to find the first function defined inside class Solution
        match = re.search(r"class Solution:\s+def (\w+)\(self,", code)
        if match:
            method_name = match.group(1)
        else:
            # Fallback if regex fails (e.g., no 'self', different spacing)
            match = re.search(r"class Solution:\s*def (\w+)\(", code)
            if match:
                method_name = match.group(1)
    
    for t in tests:
        inp = t.get("input") # This is now a dict for LeetCode
        expected = t.get("expected_output")
        
        full_script = code
        stdin_payload = ""

        if is_leetcode_style and method_name and isinstance(inp, dict):
            # 1. LeetCode Style: Build a dynamic driver for each test case
            full_script = build_leetcode_driver(code, method_name, inp)
            stdin_payload = "" # Input is passed via the script itself
        elif not is_leetcode_style:
            # 2. Codeforces Style: Pass 'input' as stdin
            full_script = code
            stdin_payload = str(inp)
        else:
            # 3. Error Case: Can't validate
             results.append({
                "input": inp, "expected_output": expected, "actual_output": "",
                "passed": False, "error": "Validation failed: Could not determine test type (CF/LC) or find method name in Solution class."
            })
             continue

        # Run the test
        stdout, stderr, rc = run_python_code_return_output(full_script, stdin_data=stdin_payload)
        actual = stdout.strip()
        
        # Handle JSON or string expected output
        try:
            expected_norm = json.dumps(expected)
        except:
            expected_norm = str(expected).strip()

        stderr_norm = stderr.strip() or None
        passed = False

        if rc != 0 or stderr_norm:
            passed = False
        else:
            # Try numeric/float comparison
            try:
                # Try parsing both as JSON (since driver outputs JSON)
                actual_val = json.loads(actual)
                expected_val = expected if isinstance(expected, (int, float, list, dict)) else json.loads(expected_norm)

                if isinstance(actual_val, (int, float)) and isinstance(expected_val, (int, float)):
                    if abs(float(actual_val) - float(expected_val)) < FLOAT_TOLERANCE:
                        passed = True
                elif actual_val == expected_val:
                    passed = True
            except Exception:
                # Fallback to simple string compare
                if actual == expected_norm:
                    passed = True

        results.append({
            "input": inp,
            "expected_output": expected,
            "actual_output": actual,
            "passed": passed,
            "error": stderr_norm
        })

    return results