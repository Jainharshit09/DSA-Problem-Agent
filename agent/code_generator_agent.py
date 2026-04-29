# In agent/code_generator_agent.py
import asyncio
from utils.gemini_wrapper import call_gemini
from shared.memory import STM_STORE
import re  # <-- ADD THIS IMPORT

class CodeGeneratorAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id

    async def generate_code(self, problem_text: str, language: str = "python") -> str:
        prompt = f"""
You are an expert competitive programmer. 
Generate a single, complete Python code block that contains a 'Solution' class with the required method.

### Required Format (VERY IMPORTANT):
- **LeetCode-style** `Solution` class.
- DO NOT include `sys.stdin` or `print()` calls.
- DO NOT include any `main` function or test harness.
- Return ONLY one clean code block containing the `import` statements and the `class Solution: ...`.

### Problem:
{problem_text}

Return ONLY one code block with the solution code.
        """

        response = call_gemini(prompt)
        content = response.get("text", "")
        
        # --- FIX: Extract code block if Gemini adds markdown ---
        match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", content, re.DOTALL)
        if match:
            content = match.group(1).strip()
        # --- END FIX ---
        
        STM_STORE.set_session_value(self.session_id, "generated_code_raw", content) # <-- Use set_session_value
        return content