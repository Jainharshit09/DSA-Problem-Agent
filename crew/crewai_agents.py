#
# UPDATED: crew/crewai_agents.py
#
# This version is updated to work with the new, more stable orchestration flow.
# The agent now receives pre-computed analysis and test cases as context,
# and its task is more focused on code generation and validation.
#

import langchain
if not hasattr(langchain, "verbose"):
    langchain.verbose = False
import json
from crewai import Agent, Task, Crew
from crewai.llm import LLM
from typing import Dict, Any, List

from crew.agent_tools import AGENT_TOOLS
from shared.config import GEMINI_API_KEY
from shared.memory import STM_STORE

def get_gemini_llm():
    return LLM(model="gemini/gemini-2.5-flash", api_key=GEMINI_API_KEY, temperature=0.2)

def create_dsa_specialist_agent(session_id: str) -> Agent:
    STM_STORE["session_id"] = session_id
    return Agent(
        role="Expert Code Generation and Validation Agent",
        goal="Generate an optimal code solution based on a provided analysis and validate it against provided test cases.",
        backstory="You are an expert competitive programmer. You are given a detailed problem analysis and a set of test cases. Your job is to write the most efficient and correct code that satisfies these requirements, then prove its correctness.",
        tools=AGENT_TOOLS,
        llm=get_gemini_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )

def create_coordinator_crew(
    session_id: str, 
    problem_text: str, 
    language: str,
    analysis: Dict[str, Any], # <-- New parameter
    test_cases: List[Dict[str, Any]] # <-- New parameter
) -> Crew:
    
    STM_STORE["session_id"] = session_id
    specialist_agent = create_dsa_specialist_agent(session_id)

    # Convert context to a readable string for the prompt
    analysis_summary = json.dumps(analysis, indent=2)
    test_cases_summary = json.dumps(test_cases, indent=2)

    # The task is now more focused
    code_generation_task = Task(
        description=(
            f"Your mission is to write and validate a code solution.\n\n"
            f"**Problem:**\n{problem_text}\n\n"
            f"**Language:** {language}\n\n"
            "You have been provided with the following critical context:\n"
            f"**1. Problem Analysis (Approach, Pattern, etc.):**\n{analysis_summary}\n\n"
            f"**2. Pre-Generated Test Cases:**\n{test_cases_summary}\n\n"
            "Follow these steps:\n"
            "1.  **Generate Code:** Based on the analysis, use the `generate_code_tool` to write a full solution.\n"
            "2.  **Validate Code:** Use the `validate_code_tool` to run your generated code against the provided test cases.\n"
            "3.  **Analyze Complexity:** Finally, use the `analyze_complexity_tool` on your final, validated code."
        ),
        agent=specialist_agent,
        expected_output="The final, validated source code and a summary of the validation and complexity analysis results.",
    )

    return Crew(
       agents=[specialist_agent],
        tasks=[code_generation_task],
        verbose=True,
    )