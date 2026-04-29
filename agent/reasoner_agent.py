import asyncio
import json
import re
from typing import Dict, Any, List

from utils.gemini_wrapper import call_gemini
from shared.memory import STM_STORE
from adk_agent.mcp.web_search import find_similar_problems


class DSAReasonerAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id

    async def _ask_gemini(self, prompt: str) -> str:
        """Run Gemini API in a background thread."""
        loop = asyncio.get_running_loop()
        out = await loop.run_in_executor(None, call_gemini, prompt)
        return out.get("text", "")

    # ------------------------------------------------------------------
    # JSON extraction helper (robust + markdown aware)
    # ------------------------------------------------------------------
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON robustly:
        - Handles ```json fenced blocks
        - Handles plain { ... }
        - Avoids capturing empty or wrong braces
        """
        try:
            # 1) Prefer fenced ```json ... ```
            fenced = re.search(r"```json\s*([\s\S]*?)```", response)
            if fenced:
                candidate = fenced.group(1).strip()
                return json.loads(candidate)

            # 2) Next, try any JSON-like block with balanced braces
            brace = re.search(r"\{[\s\S]*\}", response)
            if brace:
                candidate = brace.group(0)
                return json.loads(candidate)

        except Exception:
            pass  # fall through to fallback

        # 3) Fallback result if extraction fails
        return {
            "topic": "unknown",
            "pattern": "unknown",
            "approach": response,
            "observations": response,
            "validation": "Fallback — JSON extraction failed",
            "edge_cases": [],
            "keywords": []
        }

    # ------------------------------------------------------------------
    async def extract_dsa_intelligence(self, problem_text: str) -> Dict[str, Any]:
        """Ask Gemini to analyze the DSA problem and extract structured intelligence."""

        prompt = (
            "Analyze the following DSA problem and return a JSON object ONLY with these keys:\n"
            "- topic\n"
            "- pattern\n"
            "- approach\n"
            "- observations\n"
            "- validation\n"
            "- edge_cases (list)\n"
            "- keywords (list)\n\n"
            f"{problem_text}\n\n"
            "Return ONLY valid JSON. No markdown. No extra text."
        )

        raw = await self._ask_gemini(prompt)

        parsed = self._extract_json(raw)

        # Guarantee schema fields
        parsed["topic"] = parsed.get("topic") or "unknown"
        parsed["pattern"] = parsed.get("pattern") or "unknown"
        parsed["approach"] = parsed.get("approach") or ""
        parsed["observations"] = parsed.get("observations") or ""
        parsed["validation"] = parsed.get("validation") or ""
        parsed["edge_cases"] = parsed.get("edge_cases") or []
        parsed["keywords"] = parsed.get("keywords") or []

        STM_STORE.set(self.session_id, "problem_analysis", parsed)
        return parsed

    # ------------------------------------------------------------------
    async def fetch_similar_problems(self, problem_text: str, intelligence: Dict[str, Any]) -> List[str]:
        """Search for similar DSA problems using Serper Web Search."""
        topic = intelligence.get("topic", "")
        pattern = intelligence.get("pattern", "")

        similar = find_similar_problems(
            problem_text=problem_text,
            topic=topic,
            pattern=pattern
        )

        STM_STORE.set(self.session_id, "similar_problems", similar)
        return similar

    # ------------------------------------------------------------------
    async def run(self, problem_text: str) -> Dict[str, Any]:
        """Main reasoning pipeline."""

        intelligence = await self.extract_dsa_intelligence(problem_text)
        similar = await self.fetch_similar_problems(problem_text, intelligence)

        result = {
            "analysis": intelligence,
            "similar_problems": similar
        }

        STM_STORE.set(self.session_id, "dsa_reasoner_output", result)
        return result
