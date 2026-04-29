import sqlite3
import json
import threading
from typing import Any, Dict, Optional, List, Tuple

class STM:
    """
    Simple in-memory Short-Term Memory (thread-safe) with dict-like interface.
    Adds session helpers and flexible .set() method.
    """
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._store: Dict[str, Any] = {}
        self._sessions: Dict[str, Dict[str, Any]] = {}

    # dict-like access
    def __getitem__(self, key: str) -> Any:
        with self._lock:
            return self._store[key]

    def __setitem__(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = value

    def __delitem__(self, key: str) -> None:
        with self._lock:
            del self._store[key]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        with self._lock:
            return self._store.get(key, default)

    def set(self, key_or_session: str, key_or_value: Any = None, value: Any = None) -> None:
        """
        Flexible .set() that handles both:
          - .set(key, value)                           (global store)
          - .set(session_id, key, value)               (session-scoped)
        """
        with self._lock:
            if value is not None:
                # Called as .set(session_id, key, value)
                session_id = key_or_session
                key = key_or_value
                if session_id not in self._sessions:
                    self._sessions[session_id] = {}
                self._sessions[session_id][key] = value
            else:
                # Called as .set(key, value)
                key = key_or_session
                val = key_or_value
                self._store[key] = val

    def pop(self, key: str, default: Optional[Any] = None) -> Any:
        with self._lock:
            return self._store.pop(key, default)

    def update(self, mapping: Dict[str, Any]) -> None:
        with self._lock:
            self._store.update(mapping)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def to_dict(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._store)

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._store

    def keys(self):
        with self._lock:
            return list(self._store.keys())

    # -----------------------
    # Session management API
    # -----------------------
    def create_session(self, session_id: str) -> None:
        """Create a new empty session container and mark current session_id."""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {}
            self._store["session_id"] = session_id

    def set_session_value(self, session_id: str, key: str, value: Any) -> None:
        """Set a value inside a specific session dict."""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {}
            self._sessions[session_id][key] = value

    def get_session_value(self, session_id: str, key: str, default: Optional[Any] = None) -> Any:
        """Get a value from a specific session dict."""
        with self._lock:
            return self._sessions.get(session_id, {}).get(key, default)
    def dump(self, session_id: str) -> Dict[str, Any]:
        """Returns a copy of the data for a specific session."""
        with self._lock:
            return dict(self._sessions.get(session_id, {}))

    def delete_session(self, session_id: str) -> None:
        """Remove a session's data."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

# Singleton instance used across the codebase
STM_STORE = STM()

class LTM:
    def __init__(self, db_path: str = "./shared/ltm.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._ensure_table()

    def _ensure_table(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.commit()

    def set(self, key: str, value: Any):
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO memory(key, value) VALUES (?, ?)", (key, json.dumps(value)))
        self.conn.commit()

    def get(self, key: str) -> Optional[Any]:
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM memory WHERE key = ?", (key,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def query_prefix(self, prefix: str) -> List[Tuple[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT key, value FROM memory WHERE key LIKE ?", (f"{prefix}%",))
        return [(k, json.loads(v)) for k, v in cur.fetchall()]

LTM_STORE = LTM()
