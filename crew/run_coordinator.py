import asyncio
from .coordinator_agent_v2 import coordinate as _coordinate

async def coordinate(payload: dict):
    """
    Async wrapper exported for app.py. Delegates to coordinator_agent_v2.coordinate.
    Supports either async or sync implementations in coordinator_agent_v2.
    """
    if asyncio.iscoroutinefunction(_coordinate):
        return await _coordinate(payload)
    # sync function: run in thread to avoid blocking event loop
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _coordinate(payload))


# --- Helper function for Markdown formatting (from previous step) ---
def _format_result_to_markdown(result: dict) -> str:
    """Formats the DSAResult dictionary into a readable Markdown string."""
    
    md = [
        f"# 🧩 DSA Problem Solution: {result.get('problem_title', 'Untitled')}\n",
        "---",
        "## 📝 Problem Analysis & Explanation\n",
        f"**Approach:** {result.get('observations', 'No detailed explanation provided.')}\n",
        "\n### Approach Validation\n",
        f"**Complexity & Test Pass Rate:** {result.get('approach_validation', 'No validation performed.')}\n",
        f"**Time Complexity:** `{result.get('time_complexity', 'Unknown')}`\n",
        f"**Space Complexity:** `{result.get('space_complexity', 'Unknown')}`\n",
        f"**Optimization Tips:** {result.get('optimization_tips', '-')}\n",
        "\n## 💻 Generated Code\n",
        "\n```python\n",
        result.get('solution_code', '# No code generated'),
        "\n```\n",
        "\n## 🧪 Test Execution\n"
    ]
    
    test_results = result.get('test_case_results', [])
    if test_results:
        md.append("| Test # | Status | Input (Snippet) | Expected | Actual | Error Snippet |\n")
        md.append("|---|---|---|---|---|---|\n")
        for i, res in enumerate(test_results):
            status = "✅ PASS" if res.get('passed') else "❌ FAIL"
            input_val = str(res.get('input', ''))[:20].replace('\n', ' / ')
            actual_output = str(res.get('actual_output', ''))[:20].replace('\n', ' / ')
            error = str(res.get('error', '-'))[:20]
            md.append(f"| {i} ({res.get('description', 'auto')}) | **{status}** | `{input_val}` | `{res.get('expected_output', '')}` | `{actual_output}` | `{error}` |\n")
    else:
        md.append("No test results found.\n")

    md.append("\n## 🔗 Similar Problems\n")
    similar = result.get('similar_problems', [])
    if similar:
        for link in similar:
            md.append(f"* {link}\n")
    else:
        md.append("No similar problems found.\n")

    md.append("\n---\n")
    md.append(f"### Execution Metadata\n")
    md.append(f"* **Problem Title:** {result.get('problem_title')}\n")
    md.append(f"* **Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    return "\n".join(md)
# -------------------------------------------------------------------------


async def run_solver_headless(problem_text: str, lang: str = "python") -> dict:
    """
    NEW ENTRY POINT: Core solver logic callable by Streamlit or another service.
    Accepts input as arguments, runs the coordinator, and returns the result dictionary.
    """
    
    payload = {
        "title": "Streamlit Submitted Problem",
        "problem_text": problem_text,
        "constraints": "",
        "language": lang,
        "sample_tests": []
    }
    
    # Run the coordination flow
    result = await coordinate(payload)
    
    return result


async def run_interactive():
    print("\n=== AI-Powered DSA Problem Solver ===")
    print("Enter a DSA problem description or paste a LeetCode/Codeforces/GFG link.")
    print("Press ENTER when done.\n")

    problem_text = input("Problem description or link: ").strip()
    if not problem_text:
        print("[ERROR] No input provided.")
        return

    lang = input("Language (default python): ").strip() or "python"
    
    print("\n[INFO] Running Coordinator...\n")
    
    # Use the new core logic function
    result = await run_solver_headless(problem_text, lang)

    # Save logic remains in the interactive function for CLI experience
    title = result.get("problem_title", "dsa_solution").replace(" ", "_").replace(":", "").replace("/", "_").replace("\\", "_")[:50]
    output_dir = "output"
    filename = f"{output_dir}/{title}_result.md"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    md_content = _format_result_to_markdown(result)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"\n======= FINAL RESULT SAVED =======\n")
    print(f"Full solution saved to: {filename}")
    print(f"Execution logs stored in: dsa_logs.jsonl")
    print("\n============================\n")


def main():
    asyncio.run(run_interactive())


if __name__ == "__main__":
    main()