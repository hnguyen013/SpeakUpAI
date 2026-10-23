"""Practice session state helpers (T06).

Pure functions + dict schema stored in st.session_state.
Survives Streamlit reruns; supports turn ids and request dedupe fingerprints.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Optional

# Keys inside the session dict
K_SESSION_ID = "session_id"
K_UNIT_ID = "unit_id"
K_TURNS = "turns"
K_NEXT_TURN_ID = "next_turn_id"
K_STATUS = "status"  # active | ended
K_CREATED_AT = "created_at"
K_LAST_REQUEST_FP = "last_request_fp"
K_LAST_REQUEST_TURN_ID = "last_request_turn_id"


def new_session_id() -> str:
    return str(uuid.uuid4())


def create_session(unit_id: str) -> dict[str, Any]:
    """Create a fresh practice session dict."""
    return {
        K_SESSION_ID: new_session_id(),
        K_UNIT_ID: unit_id,
        K_TURNS: [],
        K_NEXT_TURN_ID: 1,
        K_STATUS: "active",
        K_CREATED_AT: time.time(),
        K_LAST_REQUEST_FP: None,
        K_LAST_REQUEST_TURN_ID: None,
    }


def is_active(session: Optional[dict[str, Any]]) -> bool:
    return bool(session) and session.get(K_STATUS) == "active"


def turn_count(session: Optional[dict[str, Any]]) -> int:
    if not session:
        return 0
    return len(session.get(K_TURNS) or [])


def history_for_llm(session: Optional[dict[str, Any]]) -> list[dict[str, str]]:
    """Map internal turns to {role, text} for the LLM service."""
    if not session:
        return []
    out: list[dict[str, str]] = []
    for t in session.get(K_TURNS) or []:
        role = t.get("role")
        text = (t.get("text") or "").strip()
        if role in {"teacher", "student"} and text:
            out.append({"role": role, "text": text})
    return out


def append_turn(
    session: dict[str, Any],
    role: str,
    text: str,
    *,
    request_fp: Optional[str] = None,
) -> dict[str, Any]:
    """Append a turn and advance next_turn_id. Mutates and returns session.

    If request_fp matches last_request_fp, skip append (dedupe) and return session unchanged.
    """
    if session.get(K_STATUS) != "active":
        return session

    cleaned = (text or "").strip()
    if not cleaned:
        return session

    if request_fp and session.get(K_LAST_REQUEST_FP) == request_fp:
        # Same request already applied (e.g. Streamlit double-submit / rerun)
        return session

    turn_id = int(session.get(K_NEXT_TURN_ID) or 1)
    session.setdefault(K_TURNS, []).append(
        {
            "turn_id": turn_id,
            "role": role,
            "text": cleaned,
            "ts": time.time(),
        }
    )
    session[K_NEXT_TURN_ID] = turn_id + 1
    if request_fp:
        session[K_LAST_REQUEST_FP] = request_fp
        session[K_LAST_REQUEST_TURN_ID] = turn_id
    return session


def should_skip_request(session: Optional[dict[str, Any]], request_fp: str) -> bool:
    """True if this fingerprint was already handled in the current session."""
    if not session or not request_fp:
        return False
    return session.get(K_LAST_REQUEST_FP) == request_fp


def end_session(session: dict[str, Any]) -> dict[str, Any]:
    session[K_STATUS] = "ended"
    return session


def ensure_session(
    stored: Optional[dict[str, Any]],
    unit_id: str,
    *,
    recreate_if_unit_changed: bool = True,
) -> dict[str, Any]:
    """Return an active session; create new if missing, ended, or unit changed."""
    if not stored or stored.get(K_STATUS) != "active":
        return create_session(unit_id)
    if recreate_if_unit_changed and stored.get(K_UNIT_ID) != unit_id:
        return create_session(unit_id)
    # Shallow copy lists so callers can mutate safely after assign
    if not isinstance(stored.get(K_TURNS), list):
        stored[K_TURNS] = []
    return stored
