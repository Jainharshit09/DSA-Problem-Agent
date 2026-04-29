import ast
import re
import json
from typing import Tuple
from utils.gemini_wrapper import call_gemini

# ---------------------------
# AST fallback analyzer
# ---------------------------
def _ast_analyze(code: str) -> Tuple[str, str, str]:
    """
    Pure-AST fallback: reasonably accurate detection of loops, recursion,
    two-pointer, dp-table, binary-search, heap usage, adjacency list patterns.
    Returns (time, space, explanation)
    """
    try:
        tree = ast.parse(code)
    except Exception as e:
        return "Unknown", "Unknown", f"Could not parse code: {e}"

    loop_count = 0
    max_depth = 0
    uses_adj_list = False
    uses_queue = False
    uses_heap = False
    uses_sort = False
    uses_dp_table = False
    uses_binary_search = False
    uses_two_pointer = False
    recursive_calls = []
    function_defs = set()

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.maxd = 0

        def visit_FunctionDef(self, node):
            function_defs.add(node.name)
            self.generic_visit(node)

        def visit_Call(self, node):
            try:
                fname = ast.unparse(node.func).lower()
            except Exception:
                fname = ""
            if "heappush" in fname or "heappop" in fname:
                nonlocal uses_heap
                uses_heap = True
            if "bisect" in fname:
                nonlocal uses_binary_search
                uses_binary_search = True
            if "sort" in fname:
                nonlocal uses_sort
                uses_sort = True

            # detect recursion
            if isinstance(node.func, ast.Name):
                recursive_calls.append(node.func.id)

            self.generic_visit(node)

        def visit_Assign(self, node):
            try:
                text = ast.unparse(node).lower()
            except Exception:
                text = ""
            if "graph" in text and "append" in text:
                nonlocal uses_adj_list
                uses_adj_list = True
            if "dp" in text and "[" in text:
                nonlocal uses_dp_table
                uses_dp_table = True
            # detect two-pointer variable names
            if any(n in text for n in ("left", "right", "l=", "r=", "l =", "r =")):
                nonlocal uses_two_pointer
                uses_two_pointer = True
            self.generic_visit(node)

        def visit_For(self, node):
            nonlocal loop_count
            loop_count += 1
            self.depth += 1
            self.maxd = max(self.maxd, self.depth)
            self.generic_visit(node)
            self.depth -= 1

        def visit_While(self, node):
            nonlocal loop_count
            loop_count += 1
            self.depth += 1
            self.maxd = max(self.maxd, self.depth)
            # check two-pointer style compare
            try:
                if isinstance(node.test, ast.Compare):
                    names = {n.id for n in ast.walk(node.test) if isinstance(n, ast.Name)}
                    if {"l", "r"} & names or {"left", "right"} & names:
                        nonlocal uses_two_pointer
                        uses_two_pointer = True
            except Exception:
                pass
            self.generic_visit(node)
            self.depth -= 1

    v = Visitor()
    v.visit(tree)

    max_depth = getattr(v, "maxd", 0)
    recursive = any(c in function_defs for c in recursive_calls)

    # Heuristic decision tree (AST-only)
    if uses_adj_list or uses_heap or uses_binary_search:
        if uses_heap:
            return "O((V + E) log V)", "O(V)", "Detected heap usage: likely Dijkstra/Prim"
        if uses_adj_list:
            return "O(V + E)", "O(V)", "Detected adjacency-list graph traversal (BFS/DFS)"
        if uses_binary_search:
            return "O(log n)", "O(1)", "Detected binary search (bisect)"
    if uses_dp_table:
        return "O(n * m)", "O(n * m)", "Detected DP table structures"
    if uses_two_pointer:
        return "O(n)", "O(1)", "Detected two-pointer / sliding window pattern"
    if max_depth >= 3:
        return "O(n^3)", "O(n)", "Detected nested loops depth >= 3"
    if max_depth == 2:
        return "O(n^2)", "O(n)", "Detected nested loops (depth 2)"
    if loop_count >= 1:
        return "O(n)", "O(1)", "Detected linear loop(s)"
    if recursive:
        return "Possibly O(2^n) or O(n) with memoization", "O(n)", "Detected recursion (memoization not guaranteed)"
    # default
    return "O(1)", "O(1)", "No loops/recursion detected (constant-time heuristic)"

# ---------------------------
# LLM-based analyzer (primary)
# ---------------------------
def _call_llm_for_complexity(code: str) -> Tuple[str, str, str, str]:
    """
    Call Gemini (via call_gemini) to request a structured JSON with
    time_complexity, space_complexity, algorithm, reasoning.

    Returns tuple: (time, space, explanation, source) where source is "LLM" or raises/returns None on failure.
    """
    prompt = (
        "You are a precise complexity analyst. Analyze the CODE provided and return ONLY a valid JSON object.\n"
        "JSON keys: time_complexity, space_complexity, algorithm, reasoning.\n"
        "Be succinct and use formal big-O notation (examples: \"O(V+E)\", \"O((V+E) log V)\", \"O(n log n)\").\n\n"
        "CODE:\n\n"
        f"{code}\n\n"
        "Return only JSON. No explanation outside JSON."
    )

    try:
        out = call_gemini(prompt)
        text = out.get("text", "") if isinstance(out, dict) else str(out)
    except Exception as e:
        return None

    if not text:
        return None

    # Extract JSON block
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None

    try:
        parsed = json.loads(m.group(0))
    except Exception:
        return None

    # Validate fields
    time_c = parsed.get("time_complexity")
    space_c = parsed.get("space_complexity")
    reasoning = parsed.get("reasoning") or parsed.get("explanation") or ""
    algorithm = parsed.get("algorithm") or ""

    if not time_c or not space_c:
        return None

    explanation = f"{algorithm}. {reasoning}".strip()
    return time_c, space_c, explanation, "LLM"

# ---------------------------
# Public analyze_complexity entry
# ---------------------------
def analyze_complexity(code: str) -> Tuple[str, str, str]:
    """
    Main entry — attempt LLM analysis first, then fallback to AST analysis.
    Returns (time_complexity, space_complexity, explanation).
    """
    try:
        llm_res = _call_llm_for_complexity(code)
    except Exception:
        llm_res = None

    if llm_res:
        time_c, space_c, explanation, source = llm_res
        # Basic sanity: if time_c looks ok return it; otherwise fallback
        if isinstance(time_c, str) and time_c.strip():
            return time_c, space_c, f"[LLM] {explanation}"
    # fallback
    tc, sc, expl = _ast_analyze(code)
    return tc, sc, f"[AST-Fallback] {expl}"
