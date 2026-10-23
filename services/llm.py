"""AI Teacher (LLM) service (T05).

Generates teacher turns limited to the selected Unit (Unit 1 Leisure Time).
OpenAI chat when OPENAI_API_KEY is set; otherwise mock mode.
Does not correct pronunciation or give mid-session feedback (D003).
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Optional

from services.stt import is_mock_mode

DEFAULT_MODEL = "gpt-4o-mini"


@dataclass(frozen=True)
class LLMResult:
    text: str
    mock: bool
    error: Optional[str] = None


def prompt_fingerprint(
    unit_id: str,
    student_text: str,
    history: list[dict[str, str]],
    mode: str,
) -> str:
    payload = {
        "unit_id": unit_id,
        "student_text": student_text,
        "history": history,
        "mode": mode,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _unit_context(unit: dict[str, Any]) -> str:
    goals = unit.get("goals") or []
    goals_txt = "; ".join(str(g) for g in goals) if goals else "general speaking practice"
    return (
        f"Unit id: {unit.get('id', 'unit01')}\n"
        f"Title: {unit.get('title', 'Leisure Time')}\n"
        f"Book: {unit.get('book', 'Global Success')} Grade {unit.get('grade', 8)}\n"
        f"Goals: {goals_txt}\n"
    )


def _system_prompt(unit: dict[str, Any]) -> str:
    return (
        "You are a friendly English teacher for Grade 8 students in Vietnam "
        "using the Global Success textbook.\n"
        "Stay strictly within the current unit topic and goals.\n"
        "Speak simple English suitable for A2 level. Keep each reply short "
        "(1–3 sentences). Ask one clear follow-up question when appropriate.\n"
        "Do NOT correct grammar, spelling, or pronunciation in this reply. "
        "Do NOT give scores or feedback lists. Just continue the conversation naturally.\n"
        "Do NOT switch to Vietnamese unless the student writes only Vietnamese; "
        "prefer English.\n\n"
        f"Current unit:\n{_unit_context(unit)}"
    )


_MOCK_OPENINGS = [
    "Hi! What do you usually do in your free time?",
    "Hello! Do you like sports or reading more in your leisure time?",
    "Hi there! Tell me about a hobby you enjoy after school.",
]

_MOCK_FOLLOWUPS = [
    "That sounds fun! How often do you do that?",
    "Nice! Who do you usually do it with?",
    "Great! Why do you like that activity?",
    "Cool! Do you prefer indoor or outdoor activities?",
]


def _mock_reply(mode: str, student_text: str, history: list[dict[str, str]]) -> str:
    if mode == "opening":
        idx = len(history) % len(_MOCK_OPENINGS)
        return f"[Mock LLM] {_MOCK_OPENINGS[idx]}"
    # follow-up
    idx = (len(history) + len(student_text)) % len(_MOCK_FOLLOWUPS)
    return f"[Mock LLM] {_MOCK_FOLLOWUPS[idx]}"


def generate_teacher_turn(
    unit: dict[str, Any],
    *,
    student_text: str = "",
    history: Optional[list[dict[str, str]]] = None,
    mode: str = "followup",
    model: str = DEFAULT_MODEL,
    timeout_sec: float = 30.0,
) -> LLMResult:
    """Generate one teacher utterance.

    mode:
      - "opening": first question (ignore student_text)
      - "followup": reply to student_text given history

    history items: {"role": "teacher"|"student", "text": "..."}
    """
    history = history or []
    mode = mode if mode in {"opening", "followup"} else "followup"

    if mode == "followup" and not (student_text or "").strip():
        return LLMResult(
            text="",
            mock=True,
            error="Chưa có lời học sinh để AI đáp lại.",
        )

    if is_mock_mode():
        return LLMResult(
            text=_mock_reply(mode, student_text or "", history),
            mock=True,
            error=None,
        )

    try:
        from openai import OpenAI
    except ImportError:
        return LLMResult(
            text="",
            mock=False,
            error="Thiếu package openai. Chạy: pip install openai",
        )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": _system_prompt(unit)},
    ]
    for turn in history[-8:]:  # keep prompt short
        role = turn.get("role", "")
        text = (turn.get("text") or "").strip()
        if not text:
            continue
        if role == "teacher":
            messages.append({"role": "assistant", "content": text})
        elif role == "student":
            messages.append({"role": "user", "content": text})

    if mode == "opening":
        messages.append(
            {
                "role": "user",
                "content": (
                    "Start the speaking practice. Greet the student briefly "
                    "and ask one simple question about leisure time / free-time activities."
                ),
            }
        )
    else:
        messages.append({"role": "user", "content": student_text.strip()})

    try:
        client = OpenAI(timeout=timeout_sec)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=120,
        )
        choice = response.choices[0].message if response.choices else None
        text = (getattr(choice, "content", None) or "").strip()
        if not text:
            return LLMResult(
                text="",
                mock=False,
                error="Lỗi LLM: phản hồi rỗng.",
            )
        return LLMResult(text=text, mock=False, error=None)
    except Exception as exc:
        msg = str(exc).strip() or type(exc).__name__
        if len(msg) > 200:
            msg = msg[:200] + "…"
        return LLMResult(text="", mock=False, error=f"Lỗi LLM: {msg}")
