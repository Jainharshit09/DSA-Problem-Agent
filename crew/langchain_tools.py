"""
LangChain tool wrappers for MCP tools.
These tools can be used by CrewAI agents.
"""

# Use langchain.tools for CrewAI compatibility (not langchain_core.tools)
from langchain.tools import tool
from typing import List, Dict, Any
from adk_agent.mcp import (
    validate_code_against_tests,
    analyze_complexity,
    find_similar_problems
)


@tool
def execute_code_tool(code: str, tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Execute Python code against test cases and return validation results.
    
    Args:
        code: Python code string to execute
        tests: List of test case dictionaries with 'input', 'expected_output', and 'description'
    
    Returns:
        List of test results with 'passed', 'actual_output', 'error' fields
    """
    return validate_code_against_tests(code, tests)


@tool
def analyze_complexity_tool(code: str) -> Dict[str, str]:
    """
    Analyze the time and space complexity of Python code.
    
    Args:
        code: Python code string to analyze
    
    Returns:
        Dictionary with 'time_complexity', 'space_complexity', and 'explanation'
    """
    tc, sc, explanation = analyze_complexity(code)
    return {
        "time_complexity": tc,
        "space_complexity": sc,
        "explanation": explanation
    }


@tool
def search_similar_problems_tool(problem_text: str, topic: str = "", pattern: str = "") -> List[str]:
    """
    Search for similar DSA problems using web search API.
    
    Args:
        problem_text: The problem description
        topic: DSA topic (e.g., "DP", "Graph", "Two Pointers")
        pattern: Algorithm pattern (e.g., "Sliding Window", "BFS")
    
    Returns:
        List of similar problem links and titles
    """
    return find_similar_problems(problem_text, topic, pattern)


# Export all tools
MCP_TOOLS = [
    execute_code_tool,
    analyze_complexity_tool,
    search_similar_problems_tool
]

