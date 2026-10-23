"""Speech-to-Text service (T03).

Uses OpenAI Whisper when OPENAI_API_KEY is set; otherwise mock mode.
Never hardcodes or logs API keys.
"""
from __future__ import annotations

import hashlib
import io
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class STTResult:
    text: str
    mock: bool
    error: Optional[str] = None


def audio_fingerprint(audio_bytes: bytes) -> str:
    """Stable hash so Streamlit reruns do not re-call the API for the same clip."""
    return hashlib.sha256(audio_bytes).hexdigest()


def is_mock_mode() -> bool:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return not key or key.lower() in {"", "your_key_here", "sk-..."}


def transcribe_audio(
    audio_bytes: bytes,
    *,
    language: str = "en",
    timeout_sec: float = 30.0,
) -> STTResult:
    """Transcribe WAV/audio bytes to English text.

    Returns STTResult with text, mock flag, and optional error message.
    Does not raise for network/API failures — errors are in result.error.
    """
    if not audio_bytes:
        return STTResult(text="", mock=True, error="Audio rỗng.")

    if is_mock_mode():
        return STTResult(
            text=(
                "[Mock STT] I like playing football in my free time. "
                "What about you?"
            ),
            mock=True,
            error=None,
        )

    try:
        from openai import OpenAI  # lazy import so app starts without openai installed in edge cases
    except ImportError:
        return STTResult(
            text="",
            mock=False,
            error="Thiếu package openai. Chạy: pip install openai",
        )

    try:
        client = OpenAI(timeout=timeout_sec)
        # Whisper expects a file-like object with a name for format detection
        buffer = io.BytesIO(audio_bytes)
        buffer.name = "recording.wav"
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            language=language,
            response_format="text",
        )
        # SDK may return str or object with .text
        if isinstance(response, str):
            text = response.strip()
        else:
            text = (getattr(response, "text", None) or str(response)).strip()
        return STTResult(text=text, mock=False, error=None)
    except Exception as exc:  # network, auth, rate limit, timeout
        msg = str(exc).strip() or type(exc).__name__
        # Never include request payload or key material
        if len(msg) > 200:
            msg = msg[:200] + "…"
        return STTResult(text="", mock=False, error=f"Lỗi STT: {msg}")
