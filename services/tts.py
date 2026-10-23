"""Text-to-Speech service (T04).

Uses OpenAI TTS when OPENAI_API_KEY is set; otherwise mock mode (short beep WAV).
Never hardcodes or logs API keys.
"""
from __future__ import annotations

import hashlib
import io
import math
import os
import struct
import wave
from dataclasses import dataclass
from typing import Optional

from services.stt import is_mock_mode


@dataclass(frozen=True)
class TTSResult:
    audio_bytes: bytes
    format: str  # e.g. "audio/mp3" or "audio/wav"
    mock: bool
    error: Optional[str] = None


def text_fingerprint(text: str) -> str:
    """Stable hash so Streamlit reruns do not re-call TTS for the same text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _mock_beep_wav(
    duration_sec: float = 0.4,
    sample_rate: int = 16000,
    freq_hz: float = 440.0,
) -> bytes:
    """Minimal mono WAV sine beep for offline playback testing."""
    n_samples = int(duration_sec * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            # Simple envelope to avoid click
            t = i / sample_rate
            env = 1.0
            if t < 0.02:
                env = t / 0.02
            elif t > duration_sec - 0.02:
                env = max(0.0, (duration_sec - t) / 0.02)
            sample = int(env * 0.3 * 32767 * math.sin(2 * math.pi * freq_hz * t))
            frames += struct.pack("<h", sample)
        wf.writeframes(bytes(frames))
    return buf.getvalue()


def synthesize_speech(
    text: str,
    *,
    voice: str = "nova",
    model: str = "tts-1",
    timeout_sec: float = 30.0,
) -> TTSResult:
    """Convert text to speech audio bytes.

    Returns TTSResult; network/API errors go into result.error (no raise).
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return TTSResult(
            audio_bytes=b"",
            format="audio/wav",
            mock=True,
            error="Văn bản rỗng, không thể tổng hợp giọng nói.",
        )

    if is_mock_mode():
        return TTSResult(
            audio_bytes=_mock_beep_wav(),
            format="audio/wav",
            mock=True,
            error=None,
        )

    try:
        from openai import OpenAI
    except ImportError:
        return TTSResult(
            audio_bytes=b"",
            format="audio/mp3",
            mock=False,
            error="Thiếu package openai. Chạy: pip install openai",
        )

    try:
        client = OpenAI(timeout=timeout_sec)
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=cleaned,
            response_format="mp3",
        )
        # SDK: response.content is bytes, or read()
        audio = getattr(response, "content", None)
        if audio is None and hasattr(response, "read"):
            audio = response.read()
        if not audio:
            return TTSResult(
                audio_bytes=b"",
                format="audio/mp3",
                mock=False,
                error="Lỗi TTS: phản hồi rỗng từ API.",
            )
        return TTSResult(
            audio_bytes=bytes(audio),
            format="audio/mp3",
            mock=False,
            error=None,
        )
    except Exception as exc:
        msg = str(exc).strip() or type(exc).__name__
        if len(msg) > 200:
            msg = msg[:200] + "…"
        return TTSResult(
            audio_bytes=b"",
            format="audio/mp3",
            mock=False,
            error=f"Lỗi TTS: {msg}",
        )
