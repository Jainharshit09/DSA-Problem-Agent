import time
import json
import threading
from typing import Any, Dict, Optional
import datetime
import traceback
import os

try:
    from shared.memory import STM_STORE
except Exception:
    STM_STORE = None

# Local file where logs will be stored
LOG_FILE_PATH = "dsa_logs.json"


# --------------------------------------------------------------------------
# Helper: write a log entry to local JSON file
# --------------------------------------------------------------------------
def _write_log_to_file(entry: dict) -> None:
    """Append single log entry to a local file dsa_logs.json."""
    try:
        # If file doesn't exist → create with empty array
        if not os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "w") as f:
                json.dump([], f, indent=2)

        # Read existing logs
        with open(LOG_FILE_PATH, "r") as f:
            logs = json.load(f)

        # Append new entry
        logs.append(entry)

        # Save back
        with open(LOG_FILE_PATH, "w") as f:
            json.dump(logs, f, indent=2)

    except Exception as e:
        print(f"[FILE_LOG_ERROR] {e}")
        print(entry)


# --------------------------------------------------------------------------
# Ensure STM_STORE['logs'] exists
# --------------------------------------------------------------------------
def _ensure_logs_list() -> None:
    if STM_STORE is None:
        return
    try:
        if "logs" not in STM_STORE:
            STM_STORE["logs"] = []
    except Exception:
        pass


# --------------------------------------------------------------------------
# Main log_event function
# --------------------------------------------------------------------------
def log_event(
    event_type: str,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:

    # Backward compatibility: second arg accidentally passed as metadata
    if session_id is not None and isinstance(session_id, dict) and metadata is None:
        metadata = session_id
        session_id = None

    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "session_id": session_id,
        "metadata": metadata or {},
    }

    # Store in memory store
    if STM_STORE is not None:
        try:
            _ensure_logs_list()
            logs = STM_STORE.get("logs", [])
            logs.append(entry)
            STM_STORE["logs"] = logs
        except Exception as e:
            print(f"[LOG_ERROR] {e}")
            print(entry)
    else:
        print(entry)

    # ---- NEW: Save to file locally ----
    _write_log_to_file(entry)


# --------------------------------------------------------------------------
# Public helper to get logs
# --------------------------------------------------------------------------
def get_all_logs() -> list:
    if STM_STORE is None:
        return []
    try:
        return STM_STORE.get("logs", [])
    except Exception:
        return []


def get_session_logs(session_id: str) -> list:
    if STM_STORE is None:
        return []
    try:
        logs = STM_STORE.get("logs", [])
        return [log for log in logs if log.get("session_id") == session_id]
    except Exception:
        return []


def clear_logs() -> None:
    if STM_STORE is not None:
        try:
            STM_STORE["logs"] = []
        except Exception:
            pass

    # Also clear local file
    try:
        with open(LOG_FILE_PATH, "w") as f:
            json.dump([], f, indent=2)
    except:
        pass


# --------------------------------------------------------------------------
# Optional: callback class for CrewAI
# --------------------------------------------------------------------------
class CrewAICallback:
    def __init__(self, session_id: Optional[str] = None) -> None:
        self.session_id = session_id

    def on_start(self, info: Optional[Dict[str, Any]] = None) -> None:
        log_event("CALLBACK_START", self.session_id, info)

    def on_end(self, info: Optional[Dict[str, Any]] = None) -> None:
        log_event("CALLBACK_END", self.session_id, info)

    def on_error(self, err: Exception, info: Optional[Dict[str, Any]] = None) -> None:
        error_info = {
            "error": str(err),
            "trace": traceback.format_exc(),
            **(info or {})
        }
        log_event("CALLBACK_ERROR", self.session_id, error_info)

    def handle(self, event_type: str, info: Optional[Dict[str, Any]] = None) -> None:
        log_event(event_type, self.session_id, info)

    def on_agent_start(self, agent_name: str, info: Optional[Dict[str, Any]] = None) -> None:
        log_event("AGENT_START", self.session_id, {"agent": agent_name, **(info or {})})

    def on_agent_end(self, agent_name: str, result: Any, info: Optional[Dict[str, Any]] = None) -> None:
        log_event("AGENT_END", self.session_id, {
            "agent": agent_name,
            "result_type": type(result).__name__,
            **(info or {})
        })

    def on_tool_call(self, tool_name: str, input_args: Dict[str, Any]) -> None:
        log_event("TOOL_CALL", self.session_id, {
            "tool": tool_name,
            "args_keys": list(input_args.keys())
        })

    def on_tool_result(self, tool_name: str, result: Any) -> None:
        log_event("TOOL_RESULT", self.session_id, {
            "tool": tool_name,
            "result_type": type(result).__name__,
        })
