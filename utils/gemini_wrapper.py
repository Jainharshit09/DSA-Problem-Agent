import google.generativeai as genai
import os
from shared.config import GEMINI_API_KEY 

genai.configure(api_key=GEMINI_API_KEY)

# --- FIX 1: Use a valid, public model ---
# "gemini-2.5-flash" is not a public model name
MODEL = "gemini-2.5-flash" 


def call_gemini(prompt: str):
    """
    Actual Gemini API call.
    Returns dict => {"text": "..."}
    """

    try:
        response = genai.GenerativeModel(MODEL).generate_content(prompt)

        # --- FIX 2: This prevents the "NoneType" crash ---
        if hasattr(response, "text"):
            # Ensure that if response.text is None, we return ""
            return {"text": response.text or ""}
        # --- END FIX 2 ---
        else:
            return {"text": str(response)}
            
    except Exception as e:
        return {"text": f"ERROR calling Gemini: {e}"}