#
# UPDATED: adk_agent/specialist_agent.py
#
import asyncio
import re
import time
import json  # <-- 1. ADD THIS IMPORT AT THE TOP
from typing import Any, Dict, List

from shared.memory import STM_STORE
from agent.reasoner_agent import DSAReasonerAgent
from agent.test_generator_agent import TestGeneratorAgent
from agent.code_generator_agent import CodeGeneratorAgent
from agent.validator_agent import ValidatorAgent
from .pydantic_models import DSAResult, TestCase, TestCaseResult
from .mcp import analyze_complexity
from crew.callbacks import log_event


def extract_code(text: str) -> str:
    # ... (this function is unchanged) ...
    m = re.search(r"```(?:\w+)?\n([\s\S]*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


async def _maybe_await(fn, *a, **kw):
    # ... (this function is unchanged) ...
    r = fn(*a, **kw)
    return await r if asyncio.iscoroutine(r) else r


async def handle_dsa_request(payload: Dict[str, Any]) -> DSAResult:
    src = payload.get("src", {})
    session_id = src.get("session_id", "adk_session")
    
    problem = src.get("problem_text") or src.get("problem") or src.get("description", "")
    language = src.get("language", "python")

    STM_STORE.create_session(session_id)
    log_event("ADK_SPECIALIST_START", session_id)

    reasoner = DSAReasonerAgent(session_id)
    tester = TestGeneratorAgent(session_id)
    generator = CodeGeneratorAgent(session_id)
    validator = ValidatorAgent(session_id)

    # ... (parallel tasks section is unchanged) ...
    analysis_future = asyncio.create_task(_maybe_await(reasoner.run, problem))
    tests_future = asyncio.create_task(_maybe_await(tester.generate, problem))

    raw_analysis = await analysis_future
    analysis = raw_analysis.get("analysis", {}) if isinstance(raw_analysis, dict) else {}
    if not isinstance(analysis, dict):
        analysis = {}

    raw_tests = await tests_future
    tests = [TestCase(**t.dict()) if hasattr(t, 'dict') else TestCase(**t) for t in raw_tests if isinstance(t, (dict, TestCase))]


    raw_code = await _maybe_await(generator.generate_code, problem, language)
    solution_code = extract_code(raw_code)

    test_dicts = [t.dict() for t in tests]
    
    results_raw = await _maybe_await(
        validator.validate,   
        solution_code,
        test_dicts
    )

    results = []
    for r in results_raw:
        results.append(
            TestCaseResult(
                input=r.get("input"),
                expected_output=r.get("expected_output"), 
                actual_output=r.get("actual_output"), 
                passed=r.get("passed", False),
                error=r.get("error")
            )
        )

    try:
        tc, sc, exp = await _maybe_await(analyze_complexity, solution_code)
    except:
        tc = sc = exp = "Analysis Failed"

    # --- 2. ADD THIS FIX BLOCK ---
    obs_data = analysis.get("observations", "")
    if isinstance(obs_data, list):
        observations_str = "\n".join(f"- {item}" for item in obs_data)
    else:
        observations_str = str(obs_data)

    # Coerce validation (which is a dict) to a string
    val_data = analysis.get("validation", "")
    if isinstance(val_data, dict):
        validation_str = json.dumps(val_data, indent=2) # Pretty-print the dict
    else:
        validation_str = str(val_data)
    # --- END FIX BLOCK ---


    return DSAResult(
        problem_title=src.get("problem_title", ""),
        solution_code=solution_code,
        driver_code="", 
        explanation=analysis.get("approach", ""),
        
        # --- 3. USE THE FIXED STRINGS ---
        observations=observations_str,
        approach_validation=validation_str,
        # --- END FIX ---

        analysis=analysis,
        time_complexity=tc,
        space_complexity=sc,
        complexity_explanation=exp,
        test_cases=tests,
        test_case_results=results,
        similar_problems=raw_analysis.get("similar_problems", []),
        stm_summary=STM_STORE.dump(session_id),
        references=[],
        ltm_updates={}
    )