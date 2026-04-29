#
# CORRECTED: adk_agent/pydantic_models.py
#
# 1. Added `analysis: Dict[str, Any] = Field(default_factory=dict)`
#    to the DSAResult model so it can be saved and displayed.
#

from typing import List, Any, Dict, Optional, Union
from pydantic import BaseModel, Field, model_validator
import json

class TestCase(BaseModel):
    input: Any
    expected_output: Any
    description: Optional[str] = None

class TestCaseResult(BaseModel):
    input: Any
    expected_output: Any
    actual_output: Any
    passed: bool
    error: Optional[str] = None

class DSAResult(BaseModel):
    problem_title: str = ""
    solution_code: str = ""
    driver_code: str = ""
    explanation: str = ""
    observations: str   = ""
    approach_validation: str = ""
    time_complexity: str = ""
    space_complexity: str = ""
    
    # --- FIX IS HERE ---
    analysis: Dict[str, Any] = Field(default_factory=dict)
    # --- END FIX ---
    
    test_cases: List[TestCase] = Field(default_factory=list)
    test_case_results: List[TestCaseResult] = Field(default_factory=list)
    optimization_tips: str = ""
    references: List[str] = Field(default_factory=list)
    similar_problems: List[str] = Field(default_factory=list)
    stm_summary: Dict[str, Any] = Field(default_factory=dict)
    ltm_updates: Dict[str, Any] = Field(default_factory=dict)

class ADKRequest(BaseModel):
    # Accept dict or JSON-encoded string for src
    src: Union[Dict[str, Any], str]
    extra: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    def ensure_src_is_object(cls, values):
        """
        Pre-parse validation: coerce `src` JSON string -> dict, and ensure it's a dict.
        This replaces the old root_validator(pre=True).
        """
        src = values.get("src")
        if src is None:
            raise ValueError("src property is required and must be a valid JSON object")
        if isinstance(src, str):
            try:
                values["src"] = json.loads(src)
            except Exception as e:
                raise ValueError("src property must be a valid json object") from e
        elif not isinstance(src, dict):
            raise ValueError("src property must be a valid json object")
        return values