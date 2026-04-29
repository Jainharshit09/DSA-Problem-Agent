"""
LangChain tools that wrap existing agent classes from agent/ folder.
This allows CrewAI to use your existing agent implementations.
"""

# 1. THIS IS THE CORRECT IMPORT. NOT 'langchain.tools'
from crewai.tools import tool

from typing import List, Dict, Any
import asyncio
import json

from agent.test_generator_agent import TestGeneratorAgent
from agent.reasoner_agent import DSAReasonerAgent
from agent.code_generator_agent import CodeGeneratorAgent
from agent.validator_agent import ValidatorAgent
from agent.complexity_agent import ComplexityAgent
from shared.memory import STM_STORE
from crew.callbacks import log_event


def get_session_id() -> str:
    """Retrieve session_id from STM_STORE"""
    return STM_STORE.get("session_id", "default_session")


def run_async_tool(coro):
    """Safely run async code in sync context"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


# 2. ADD THE '@tool' DECORATOR (from crewai)
@tool
def generate_test_cases_tool(problem_text: str) -> str:
    """Generate test cases for a DSA problem using TestGeneratorAgent.
    
    Args:
        problem_text: Description of the DSA problem
        
    Returns:
        JSON string containing test cases
    """
    session_id = get_session_id()
    log_event("TOOL_CALL", "generate_test_cases", {"problem": problem_text[:50]})
    
    try:
        agent = TestGeneratorAgent(session_id)
        tests = run_async_tool(agent.generate(problem_text))
        
        # Store in STM for context sharing
        STM_STORE["test_cases"] = tests
        log_event("TOOL_SUCCESS", "generate_test_cases", {"count": len(tests)})
        
        return json.dumps(tests, indent=2)
    except Exception as e:
        log_event("TOOL_ERROR", "generate_test_cases", {"error": str(e)})
        return json.dumps({"error": str(e), "test_cases": []})


# 3. ADD THE '@tool' DECORATOR
@tool
def analyze_problem_tool(problem_text: str) -> str:
    """Analyze a DSA problem using DSAReasonerAgent.
    
    Args:
        problem_text: Description of the DSA problem
        
    Returns:
        JSON string containing problem analysis
    """
    session_id = get_session_id()
    log_event("TOOL_CALL", "analyze_problem", {"problem": problem_text[:50]})
    
    try:
        agent = DSAReasonerAgent(session_id)
        result = run_async_tool(agent.run(problem_text))
        
        # Store in STM for context sharing
        STM_STORE["problem_analysis"] = result
        log_event("TOOL_SUCCESS", "analyze_problem", {})
        
        return json.dumps(result, indent=2)
    except Exception as e:
        log_event("TOOL_ERROR", "analyze_problem", {"error": str(e)})
        return json.dumps({"error": str(e), "analysis": None})


# 4. ADD THE '@tool' DECORATOR
@tool
def generate_code_tool(problem_text: str, language: str = "python") -> str:
    """Generate a code solution using CodeGeneratorAgent.
    
    Args:
        problem_text: Description of the DSA problem
        language: Programming language (python, cpp, java)
        
    Returns:
        Generated code as string
    """
    session_id = get_session_id()
    log_event("TOOL_CALL", "generate_code", {"language": language})
    
    try:
        agent = CodeGeneratorAgent(session_id)
        code = run_async_tool(agent.generate_code(problem_text, language))
        
        # Store in STM for context sharing
        STM_STORE["generated_code"] = code
        STM_STORE["language"] = language
        log_event("TOOL_SUCCESS", "generate_code", {"lines": len(code.splitlines())})
        
        return code
    except Exception as e:
        log_event("TOOL_ERROR", "generate_code", {"error": str(e)})
        return f"# Error generating code: {str(e)}"


# 5. ADD THE '@tool' DECORATOR
@tool
def validate_code_tool(code: str) -> str:
    """Validate code with ValidatorAgent.
    
    Args:
        code: Code to validate
        
    Returns:
        JSON string with validation results
    """
    session_id = get_session_id()
    test_cases = STM_STORE.get("test_cases", [])
    
    log_event("TOOL_CALL", "validate_code", {})
    
    try:
        agent = ValidatorAgent(session_id)
        results = agent.validate(code, test_cases)
        
        # Store in STM for context sharing
        STM_STORE["validation_results"] = results
        log_event("TOOL_SUCCESS", "validate_code", {"passed": len([r for r in results if r.get('passed')])})
        
        return json.dumps(results, indent=2)
    except Exception as e:
        log_event("TOOL_ERROR", "validate_code", {"error": str(e)})
        return json.dumps({"error": str(e), "results": []})


# 6. ADD THE '@tool' DECORATOR
@tool
def analyze_complexity_tool(code: str) -> str:
    """Analyze time and space complexity with ComplexityAgent.
    
    Args:
        code: Code to analyze
        
    Returns:
        JSON string with complexity analysis
    """
    session_id = get_session_id()
    log_event("TOOL_CALL", "analyze_complexity", {})
    
    try:
        agent = ComplexityAgent()
        tc, sc, explanation = agent.analyze(code)
        
        result = {
            "time_complexity": tc,
            "space_complexity": sc,
            "explanation": explanation
        }
        
        # Store in STM for context sharing
        STM_STORE["complexity_analysis"] = result
        log_event("TOOL_SUCCESS", "analyze_complexity", {"tc": tc, "sc": sc})
        
        return json.dumps(result, indent=2)
    except Exception as e:
        log_event("TOOL_ERROR", "analyze_complexity", {"error": str(e)})
        return json.dumps({"error": str(e), "time_complexity": "N/A", "space_complexity": "N/A"})


# 7. EXPORT THE LIST OF TOOL FUNCTIONS (now decorated)
AGENT_TOOLS = [
    generate_test_cases_tool,
    analyze_problem_tool,
    generate_code_tool,
    validate_code_tool,
    analyze_complexity_tool,
]