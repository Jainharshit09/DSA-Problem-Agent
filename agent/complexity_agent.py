from typing import Tuple
import ast

class ComplexityAgent:
    def analyze(self, code: str) -> Tuple[str, str, str]:
        try:
            tree = ast.parse(code)
        except Exception as e:
            return "Unknown", "Unknown", f"Parse error: {e}"
        max_depth = 0
        loops = 0
        recursive = False

        class V(ast.NodeVisitor):
            def __init__(self):
                self.depth = 0
                self.maxd = 0
                self.loops = 0
                self.fnames = set()
                self.calls = []
            def visit_FunctionDef(self, node):
                self.fnames.add(node.name)
                self.generic_visit(node)
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    self.calls.append(node.func.id)
                self.generic_visit(node)
            def visit_For(self, node):
                self.loops += 1
                self.depth += 1
                self.maxd = max(self.maxd, self.depth)
                self.generic_visit(node)
                self.depth -= 1
            def visit_While(self, node):
                self.loops += 1
                self.depth += 1
                self.maxd = max(self.maxd, self.depth)
                self.generic_visit(node)
                self.depth -= 1

        v = V()
        v.visit(tree)
        loops = v.loops
        max_depth = v.maxd
        recursive = any(c in v.fnames for c in v.calls)

        if max_depth >= 3:
            tc = "O(n^3) or worse"
        elif max_depth == 2:
            tc = "O(n^2)"
        elif loops >= 1:
            tc = "O(n)"
        elif recursive:
            tc = "Possibly exponential or linear with memo"
        else:
            tc = "O(1) or O(log n)"
        space = "O(1)"
        if any(x in code for x in ["list(", "[]", "dict(", "set(", "defaultdict"]):
            space = "O(n) possible"
        explanation = f"Detected {loops} loop(s), max nested depth {max_depth}, recursion: {recursive}"
        return tc, space, explanation
