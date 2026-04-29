#
# CORRECTED: crew/coordinator_agent_v2.py
#
# This file has been significantly updated to fix a deadlock in the crew execution.
# The `run_async_tool` bridge was unreliable. The new, more robust strategy is:
#
# 1.  **Pre-computation:** Run the async `DSAReasonerAgent` and `TestGeneratorAgent`
#     directly *before* starting the crew. This avoids the sync/async conflict.
# 2.  **Context Injection:** Pass the results of the analysis and test generation
#     into the CrewAI task as context.
# 3.  **Focused Crew:** The CrewAI agent's task is now simpler and more reliable:
#     generate and validate code using the provided context.
#

import asyncio
import json
from typing import Dict, Any

from shared.memory import STM_STORE
from crew.a2a_client_tool import call_adk_a2a
from crew.callbacks import log_event, CrewAICallback
from crew.crewai_agents import create_coordinator_crew
import uuid

# --- Import agents directly for pre-computation ---
from agent.reasoner_agent import DSAReasonerAgent
from agent.test_generator_agent import TestGeneratorAgent
# ---

def new_session_id() -> str:
    return str(uuid.uuid4())

async def coordinate(user_input: dict) -> Dict[str, Any]:
    """
    Main coordination function with a corrected, more stable workflow.
    """
    session_id = new_session_id()
    problem_text = user_input.get("problem_text", "")
    language = user_input.get("language", "python")

    # Initialize callback for monitoring
    callback = CrewAICallback(session_id)

    log_event("session_start", session_id, {
        "title": user_input.get("title", ""),
        "language": language
    })

    # Store initial context in STM
    STM_STORE.create_session(session_id)
    STM_STORE.set(session_id, "problem_text", problem_text)
    STM_STORE.set(session_id, "language", language)

    try:
        # --- STEP 1: Pre-computation (Stable Async Calls) ---
        log_event("precomputation_start", session_id)
        reasoner = DSAReasonerAgent(session_id)
        tester = TestGeneratorAgent(session_id)

        # Run analysis and test generation in parallel
        analysis_task = asyncio.create_task(reasoner.run(problem_text))
        tests_task = asyncio.create_task(tester.generate(problem_text))

        analysis_result = await analysis_task
        generated_tests = await tests_task
        
        # Store results in memory for the crew to use
        STM_STORE.set(session_id, "problem_analysis", analysis_result)
        STM_STORE.set(session_id, "generated_tests", generated_tests)
        log_event("precomputation_finish", session_id, {"test_count": len(generated_tests)})
        
        # --- STEP 2: Focused CrewAI Execution ---
        log_event("crewai_start", session_id)
        
        # The crew will use the pre-computed data from STM
        crew = create_coordinator_crew(session_id, problem_text, language, analysis_result, generated_tests)

        loop = asyncio.get_running_loop()
        crew_result = await loop.run_in_executor(None, crew.kickoff)
        log_event("crewai_finish", session_id, {"result_type": type(crew_result).__name__})
        
        # --- STEP 3: Build Payload and make the A2A call ---
        # This step is now reliably reached
        
        # Extract the generated code from memory (set by the crew's tools)
        solution_code =STM_STORE.get_session_value(session_id, "generated_code", "# Code not generated")

        payload = {
            "title": user_input.get("title", "Coordinated DSA Solution"),
            "problem_text": problem_text,
            "language": language,
            "test_cases": generated_tests,
            "solution_code": solution_code,
            "crewai_context": {
                "analysis": analysis_result,
                "crewai_raw_output": str(crew_result)
            }
        }

        log_event("a2a_request_start", session_id)
        adk_response = call_adk_a2a(payload)
        log_event("a2a_request_finish", session_id)
        
        # --- STEP 4: Finalize Result ---
        final_result = {
            **adk_response,
            "session_id": session_id,
            "stm_summary": STM_STORE.dump(session_id),
        }

        return final_result

    except Exception as e:
        log_event("coordination_error", session_id, {
            "error_type": type(e).__name__,
            "error_message": str(e),
        })
        callback.on_error(e)
        # Raise a more informative error
        raise RuntimeError(f"Coordinator failed: {e}") from e