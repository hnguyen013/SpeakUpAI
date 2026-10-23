"""End-of-session feedback (T08).

Schema-based feedback from confirmed transcripts only.
Does NOT infer pronunciation errors from text alone (D003 / AGENTS).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from services.stt import is_mock_mode

DEFAULT_MODEL = "gpt-4o-mini"


@dataclass
class LanguageIssue:
    category: str  # grammar | vocabulary | structure | unclear_transcript | other
    evidence: str  # exact quote from student transcript
    suggestion: str  # corrected or clearer alternative
    note: str = ""  # short explanation in simple English or Vietnamese


@dataclass
class FeedbackReport:
    strengths: list[str] = field(default_factory=list)
    issues: list[LanguageIssue] = field(default_factory=list)
    practice_tips: list[str] = field(default_factory=list)
    uncertain_transcripts: list[str] = field(default_factory=list)
    mock: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "strengths": list(self.strengths),
            "issues": [asdict(i) for i in self.issues],
            "practice_tips": list(self.practice_tips),
            "uncertain_transcripts": list(self.uncertain_transcripts),
            "mock": self.mock,
            "error": self.error,
        }


def feedback_fingerprint(unit_id: str, student_lines: list[str]) -> str:
    payload = {"unit_id": unit_id, "lines": student_lines}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def student_lines_from_session(session: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for t in session.get("turns") or []:
        if t.get("role") == "student":
            text = (t.get("text") or "").strip()
            if text:
                lines.append(text)
    return lines


_UNCERTAIN_MARKERS = (
    "[unclear]",
    "[inaudible]",
    "...",
    "??",
    "[?]",
    "(unclear)",
)


def flag_uncertain_lines(lines: list[str]) -> list[str]:
    """Heuristic: mark lines that look like uncertain STT, not pronunciation scores."""
    out: list[str] = []
    for line in lines:
        low = line.lower()
        if any(m in low for m in _UNCERTAIN_MARKERS):
            out.append(line)
            continue
        # very short or mostly non-letters
        letters = sum(1 for c in line if c.isalpha())
        if letters < 3 and len(line) > 0:
            out.append(line)
    return out


def _mock_feedback(lines: list[str]) -> FeedbackReport:
    uncertain = flag_uncertain_lines(lines)
    issues: list[LanguageIssue] = []
    strengths: list[str] = []

    if not lines:
        return FeedbackReport(
            strengths=[],
            issues=[],
            practice_tips=["Hãy nói thêm vài câu về leisure activities rồi xem feedback."],
            uncertain_transcripts=[],
            mock=True,
        )

    strengths.append("You joined the conversation and answered in English.")
    if any("like" in ln.lower() or "play" in ln.lower() or "hobby" in ln.lower() for ln in lines):
        strengths.append("You talked about free-time activities (unit topic).")

    for ln in lines:
        # Simple grammar pattern: "I playing" / "I goes"
        if re.search(r"\bi\s+playing\b", ln, re.I):
            issues.append(
                LanguageIssue(
                    category="grammar",
                    evidence=ln,
                    suggestion=re.sub(r"\bI\s+playing\b", "I play", ln, flags=re.I),
                    note="Use present simple for habits: I play…",
                )
            )
        elif re.search(r"\bi\s+goes\b", ln, re.I):
            issues.append(
                LanguageIssue(
                    category="grammar",
                    evidence=ln,
                    suggestion=re.sub(r"\bI\s+goes\b", "I go", ln, flags=re.I),
                    note="With I/you/we/they use go, not goes.",
                )
            )
        elif re.search(r"\bhe\s+go\b|\bshe\s+go\b", ln, re.I):
            issues.append(
                LanguageIssue(
                    category="grammar",
                    evidence=ln,
                    suggestion=re.sub(r"\b(he|she)\s+go\b", r"\1 goes", ln, flags=re.I),
                    note="With he/she use goes.",
                )
            )

    for u in uncertain:
        issues.append(
            LanguageIssue(
                category="unclear_transcript",
                evidence=u,
                suggestion="(Please re-record or type the sentence clearly.)",
                note="Transcript may be incomplete — not treated as a pronunciation score.",
            )
        )

    tips = [
        "Practice 3 sentences: I usually… / I like… because… / On weekends I…",
        "After speaking, read the subtitle and fix only if the words are wrong (STT), not accent.",
    ]
    if not issues:
        tips.append("Try longer answers (two short sentences) next time.")

    return FeedbackReport(
        strengths=strengths,
        issues=issues,
        practice_tips=tips,
        uncertain_transcripts=uncertain,
        mock=True,
    )


def _parse_llm_json(raw: str) -> Optional[dict[str, Any]]:
    text = (raw or "").strip()
    if not text:
        return None
    # Strip markdown fences if present
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        # try find first { ... }
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(text[start : end + 1])
                return data if isinstance(data, dict) else None
            except json.JSONDecodeError:
                return None
    return None


def _from_llm_dict(data: dict[str, Any], uncertain: list[str]) -> FeedbackReport:
    strengths = [str(s) for s in (data.get("strengths") or []) if str(s).strip()]
    tips = [str(s) for s in (data.get("practice_tips") or []) if str(s).strip()]
    issues: list[LanguageIssue] = []
    for item in data.get("issues") or []:
        if not isinstance(item, dict):
            continue
        cat = str(item.get("category") or "other").lower()
        if cat in {"pronunciation", "accent", "phonetics"}:
            # Drop pronunciation guesses — policy
            continue
        evidence = str(item.get("evidence") or "").strip()
        suggestion = str(item.get("suggestion") or "").strip()
        note = str(item.get("note") or "").strip()
        if not evidence:
            continue
        if cat not in {"grammar", "vocabulary", "structure", "unclear_transcript", "other"}:
            cat = "other"
        issues.append(
            LanguageIssue(
                category=cat,
                evidence=evidence,
                suggestion=suggestion or evidence,
                note=note,
            )
        )
    for u in uncertain:
        if not any(i.evidence == u and i.category == "unclear_transcript" for i in issues):
            issues.append(
                LanguageIssue(
                    category="unclear_transcript",
                    evidence=u,
                    suggestion="(Re-record or type clearly.)",
                    note="Uncertain transcript — not a pronunciation score.",
                )
            )
    return FeedbackReport(
        strengths=strengths or ["You completed the practice session."],
        issues=issues,
        practice_tips=tips or ["Review the suggestions above and try again."],
        uncertain_transcripts=uncertain,
        mock=False,
    )


def generate_feedback(
    unit: dict[str, Any],
    session: dict[str, Any],
    *,
    model: str = DEFAULT_MODEL,
    timeout_sec: float = 45.0,
) -> FeedbackReport:
    """Build end-of-session feedback from confirmed student transcripts only."""
    lines = student_lines_from_session(session)
    uncertain = flag_uncertain_lines(lines)

    if is_mock_mode():
        return _mock_feedback(lines)

    if not lines:
        return FeedbackReport(
            strengths=[],
            issues=[],
            practice_tips=["No student lines recorded in this session."],
            uncertain_transcripts=[],
            mock=False,
        )

    try:
        from openai import OpenAI
    except ImportError:
        return FeedbackReport(
            error="Thiếu package openai. Chạy: pip install openai",
            mock=False,
        )

    unit_ctx = (
        f"Unit: {unit.get('title')} ({unit.get('id')}), "
        f"{unit.get('book')} grade {unit.get('grade')}. "
        f"Goals: {'; '.join(unit.get('goals') or [])}"
    )
    system = (
        "You are an English teacher for Grade 8 (Global Success). "
        "Give end-of-session feedback ONLY from the student's confirmed transcripts. "
        "Return strict JSON with keys: strengths (string[]), issues (array of "
        "{category, evidence, suggestion, note}), practice_tips (string[]). "
        "category must be one of: grammar, vocabulary, structure, unclear_transcript, other. "
        "NEVER invent pronunciation, accent, or fluency scores from text. "
        "If a line looks incomplete or marked unclear, use category unclear_transcript. "
        "evidence must quote the student line. Keep notes short and kind. A2 level."
    )
    user = (
        f"{unit_ctx}\n\nStudent transcripts (confirmed):\n"
        + "\n".join(f"- {ln}" for ln in lines)
        + "\n\nRespond with JSON only."
    )

    try:
        client = OpenAI(timeout=timeout_sec)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=600,
            response_format={"type": "json_object"},
        )
        choice = response.choices[0].message if response.choices else None
        raw = (getattr(choice, "content", None) or "").strip()
        data = _parse_llm_json(raw)
        if not data:
            return FeedbackReport(
                error="Lỗi feedback: không parse được JSON từ LLM.",
                mock=False,
            )
        return _from_llm_dict(data, uncertain)
    except Exception as exc:
        msg = str(exc).strip() or type(exc).__name__
        if len(msg) > 200:
            msg = msg[:200] + "…"
        return FeedbackReport(error=f"Lỗi feedback: {msg}", mock=False)
