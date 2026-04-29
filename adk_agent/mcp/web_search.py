import requests
from shared.config import SERPAPI_KEY
from typing import List, Union


# ------------------------------
# NORMALIZATION HELPERS
# ------------------------------
def normalize_field(value: Union[str, List[str], None]) -> str:
    """
    Ensures topic/pattern is ALWAYS a clean string.
    - If list → join into string
    - If None → empty string
    - If already string → strip
    """
    if isinstance(value, list):
        return " ".join(str(v) for v in value if v).strip()

    if value is None:
        return ""

    return str(value).strip()


# ------------------------------
# QUERY BUILDER
# ------------------------------
def build_query(problem_text: str, topic: str = "", pattern: str = "") -> str:
    """
    Build optimized Serper query.
    Avoids duplication + generates strong conceptual queries.
    """

    topic = normalize_field(topic)
    pattern = normalize_field(pattern)

    parts = []

    # 1. Pattern has the strongest signal (binary search / DP / sliding window)
    if pattern and pattern.lower() not in ["unknown", "n/a", "none"]:
        parts.append(f"similar {pattern} problems")

    # 2. Add topic variations
    if topic and topic.lower() not in ["unknown", "n/a", "none"]:
        parts.append(f"{topic} interview coding question")

    # 3. Short description chunk (first 120 chars)
    problem_summary = problem_text[:120].replace("\n", " ").strip()
    if problem_summary and len(problem_summary.split()) > 5:
        parts.append(f"problems similar to {problem_summary}")

    # 4. Avoid showing the same original problem
    if "http" in problem_text:
        parts.append(f"-site:{problem_text.split('?')[0]}")

    # 5. Always enforce site restriction to improve precision
    parts.append("(site:leetcode.com OR site:geeksforgeeks.org OR site:codeforces.com)")

    # Dedup logic
    final_query = []
    seen = set()

    for part in parts:
        key = part.lower()
        if key not in seen:
            seen.add(key)
            final_query.append(part)

    # KEEP MAX 3 MEANINGFUL PARTS + site filter
    if len(final_query) > 4:
        final_query = final_query[:3] + [final_query[-1]]

    return " AND ".join(final_query)


# ------------------------------
# SERPER SEARCH
# ------------------------------
def search_similar_problems_serper(query: str, max_results: int = 10) -> List[str]:
    """
    Perform Serper API search.
    """

    if not SERPAPI_KEY:
        return ["[ERROR] SERPAPI_KEY missing — set it in .env"]

    url = "https://google.serper.dev/search"

    payload = {
        "q": query,
        "num": max_results,
        "gl": "us",
        "hl": "en"
    }

    headers = {
        "X-API-KEY": SERPAPI_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return [f"[SERPER ERROR] {e}"]

    results = []

    for item in data.get("organic", [])[:max_results]:
        title = item.get("title", "").strip()
        link = item.get("link", "")

        # Strict filter for coding sites
        if any(domain in link for domain in [
            "leetcode.com",
            "geeksforgeeks.org",
            "codeforces.com",
            "hackerrank.com"
        ]):
            results.append(f"{title} - {link}")

    return results


# ------------------------------
# PUBLIC ENTRY
# ------------------------------
def find_similar_problems(problem_text: str, topic: str = "", pattern: str = "") -> List[str]:
    """
    Clean input → build query → run Serper → get similar problems
    """

    query = build_query(problem_text, topic, pattern)
    return search_similar_problems_serper(query)
