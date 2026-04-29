#
# CORRECTED: crew/a2a_client_tool.py
#
# The `data` variable is changed to use the key "src"
# to match 
import requests
from typing import Dict, Any
from shared.config import ADK_A2A_URL

def call_adk_a2a(payload: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
    data = {"src": payload}
    resp = requests.post(ADK_A2A_URL, json=data, timeout=(5, timeout))
    resp.raise_for_status()
    return resp.json()