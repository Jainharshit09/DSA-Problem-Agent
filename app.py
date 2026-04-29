
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import requests
import json
import re
from crew.run_coordinator import coordinate
import asyncio

st.set_page_config(page_title="AI DSA Solver", layout="wide")

st.title("🤖 AI-Powered DSA Problem Solver")
st.write("Enter a DSA problem description or paste a link from LeetCode/Codeforces/GFG.")

# ---- INPUT BOX ----
problem_input = st.text_area("Problem Description or Link", height=200)

language = st.selectbox("Select Language", ["python", "cpp", "java"], index=0)

submit = st.button("Solve Problem")

def extract_problem_from_link(link: str) -> str:
    """Fetch and clean problem statement from URLs."""
    try:
        if "leetcode.com" in link:
            page = requests.get(link).text
            match = re.findall(r'"description":"(.*?)",', page)
            if match:
                clean = match[0].replace("\\n", "\n").replace("\\u003c", "<")
                return clean
        elif "geeksforgeeks.org" in link or "gfg" in link:
            page = requests.get(link).text
            m = re.search(r'<article(.*?)</article>', page, re.S)
            if m:
                text = re.sub(r"<.*?>", "", m.group(1))
                return text
        elif "codeforces.com" in link:
            page = requests.get(link).text
            m = re.search(r'<div class="problem-statement">(.*?)</div>', page, re.S)
            if m:
                text = re.sub(r"<.*?>", "", m.group(1))
                return text
    except Exception as e:
        st.warning(f"Error extracting text: {e}")
    return link  # fallback: treat input as text


if submit:

    if not problem_input.strip():
        st.error("Please enter a DSA problem or link.")
        st.stop()

    # ---- CLEAN INPUT ----
    if problem_input.startswith("http"):
        problem_text = extract_problem_from_link(problem_input.strip())
        st.info("Problem extracted from link.")
    else:
        problem_text = problem_input

    user_payload = {
        "title": "User Submitted Problem",
        "problem_text": problem_text,
        "constraints": "",
        "language": language
    }

    st.write("⏳ Running multi-agent solver (CrewAI → ADK)...")
    with st.spinner("Processing... This may take 5–20 seconds"):

        final_result = asyncio.run(coordinate(user_payload))

    st.success("✔ Solution Generated")

    # ---- OUTPUT DISPLAY ----
    st.subheader("🧠 Problem Analysis")
    st.json(final_result.get("analysis", {}))

    st.subheader("📝 Observations & Explanation")
    st.write(final_result.get("explanation", ""))

    st.subheader("🧮 Complexity Analysis")
    st.write("Time Complexity:", final_result.get("time_complexity"))
    st.write("Space Complexity:", final_result.get("space_complexity"))

    st.subheader("🧪 Test Cases")
    st.json(final_result.get("test_cases", []))

    st.subheader("🧪 Test Results")
    st.json(final_result.get("test_case_results", []))

    st.subheader("📌 Similar Problems")
    st.write(final_result.get("similar_problems", []))

    st.subheader("💻 Generated Code")
    st.code(final_result.get("solution_code", ""), language=language)

    st.subheader("🧵 Logs / Memory Summary")
    st.json(final_result.get("stm_summary", {}))