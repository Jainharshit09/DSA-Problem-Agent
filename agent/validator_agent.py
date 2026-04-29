from typing import List, Dict, Any
from adk_agent.mcp.code_executor import validate_code_against_tests

class ValidatorAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id

    def validate(self, code: str, tests: List[Dict[str, Any]]):
        # Only one validator now – CF-style unified
        return validate_code_against_tests(code, tests)
