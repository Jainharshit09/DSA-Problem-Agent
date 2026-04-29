# In agent/test_generator_agent.py
import asyncio
import json
import re
from typing import List, Dict, Any
from shared.memory import STM_STORE
from utils.gemini_wrapper import call_gemini

class TestGeneratorAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id

    async def generate(self, problem_text: str) -> List[Dict[str, Any]]:
        """
        Generates test cases by asking the LLM to extract examples and create edge cases
        in the format required by the code executor.
        """
        prompt = (
            "Analyze the following DSA problem and return a JSON array ONLY. "
            "Each object in the array must have three keys: 'input', 'expected_output', and 'description'.\n"
            
            # --- THIS IS THE CRITICAL CHANGE ---
            "The 'input' key MUST be a JSON OBJECT mapping argument names to their values (e.g., {{\"nums1\": [1,3], \"nums2\": [2]}}).\n"
            # --- END CHANGE ---
            
            "Use the problem's examples if available, and generate one or two edge cases.\n"
            f"Problem: {problem_text}\n\n"
            "Return ONLY the JSON array. No explanation outside JSON."
        )

        loop = asyncio.get_running_loop()
        out = await loop.run_in_executor(None, call_gemini, prompt)
        response = out.get("text", "")

        tests: List[Dict[str, Any]]
        try:
            match = re.search(r"\[[\s\S]*\]", response)
            if match:
                parsed = json.loads(match.group(0))
                # Validate the new structure
                if isinstance(parsed, list) and all(
                    isinstance(item, dict) and 
                    'input' in item and 
                    'expected_output' in item and 
                    isinstance(item['input'], dict)  # <-- Check that 'input' is a dict
                for item in parsed):
                    tests = parsed
                else:
                    raise ValueError("JSON structure incorrect or 'input' is not an object")
            else:
                raise ValueError("No JSON array found in response")
        except Exception as e:
            tests = [{"input": {}, "expected_output": "", "description": f"auto (LLM generation failed: {e})"}]

        STM_STORE.set_session_value(self.session_id, "generated_tests", tests) # <-- Use set_session_value
        return tests