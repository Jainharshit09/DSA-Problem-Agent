import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LTM_DB_PATH = os.environ.get("LTM_DB_PATH", "./shared/ltm.db")
REDIS_URL = os.environ.get("REDIS_URL", None)
ADK_A2A_URL = os.environ.get("ADK_A2A_URL", "http://localhost:8000/dsa")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")