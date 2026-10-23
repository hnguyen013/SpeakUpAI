"""SpeakUp AI – Home: Unit (T01) + thu âm (T02) + STT (T03) + TTS (T04)."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from services.stt import audio_fingerprint, is_mock_mode, transcribe_audio
from services.tts import synthesize_speech, text_fingerprint

load_dotenv()

UNITS_DIR = Path(__file__).parent / "units"

# Câu mẫu AI Teacher (T04 độc lập LLM; T05 sẽ tạo động)
SAMPLE_AI_LINE = (
    "Hi! What do you usually do in your free time? "
    "Do you like sports or reading?"
)


def load_units() -> list[dict]:
    """Load all unit JSON files from units/ directory."""
    units: list[dict] = []
    if not UNITS_DIR.is_dir():
        return units
    for path in sorted(UNITS_DIR.glob("unit*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "id" in data and "title" in data:
                units.append(data)
        except (json.JSONDecodeError, OSError):
            continue
    return units


def is_audio_empty(audio_value) -> bool:
    """Return True if audio input is missing or has no bytes."""
    if audio_value is None:
        return True
    try:
        data = audio_value.getvalue()
    except Exception:
        return True
    return len(data) == 0


def _render_tts_section(text: str, state_prefix: str) -> None:
    """Synthesize and play TTS for text; cache by fingerprint in session_state."""
    fp = text_fingerprint(text)
    fp_key = f"{state_prefix}_fp"
    bytes_key = f"{state_prefix}_bytes"
    fmt_key = f"{state_prefix}_fmt"
    err_key = f"{state_prefix}_error"
    mock_key = f"{state_prefix}_mock"

    need = st.session_state.get(fp_key) != fp
    if need:
        with st.spinner("Đang tổng hợp giọng nói…"):
            result = synthesize_speech(text)
        st.session_state[fp_key] = fp
        st.session_state[bytes_key] = result.audio_bytes
        st.session_state[fmt_key] = result.format
        st.session_state[err_key] = result.error
        st.session_state[mock_key] = result.mock

    err = st.session_state.get(err_key)
    audio_b = st.session_state.get(bytes_key) or b""
    fmt = st.session_state.get(fmt_key) or "audio/mp3"
    mock = st.session_state.get(mock_key, False)

    if err:
        st.error(err)
        if st.button("Thử TTS lại", key=f"retry_{state_prefix}"):
            st.session_state.pop(fp_key, None)
            st.rerun()
        return

    if not audio_b:
        st.warning("Không có dữ liệu âm thanh TTS.")
        return

    tag = " (mock – tiếng bip)" if mock else ""
    st.caption(f"Phát lại{tag}:")
    st.audio(audio_b, format=fmt)


def main() -> None:
    st.set_page_config(page_title="SpeakUp AI", page_icon="🎤", layout="centered")
    st.title("🎤 SpeakUp AI")
    st.caption("Luyện nghe – nói tiếng Anh lớp 8 | Global Success")

    units = load_units()
    if not units:
        st.error("Không tìm thấy file Unit trong thư mục `units/`.")
        return

    options = {f"{u['id']} – {u['title']}": u for u in units}
    labels = list(options.keys())

    default_index = 0
    if "selected_unit_id" in st.session_state:
        for i, u in enumerate(units):
            if u["id"] == st.session_state["selected_unit_id"]:
                default_index = i
                break

    st.subheader("Chọn Unit")
    chosen_label = st.selectbox(
        "Unit đang học",
        options=labels,
        index=default_index,
        key="unit_select",
    )
    unit = options[chosen_label]

    st.session_state["selected_unit_id"] = unit["id"]
    st.session_state["selected_unit"] = unit

    st.success(f"Đã chọn: **{unit['title']}** (`{unit['id']}`)")

    with st.expander("Chi tiết Unit", expanded=False):
        st.markdown(f"**Sách:** {unit.get('book', '—')} – Lớp {unit.get('grade', '—')}")
        st.markdown(f"**Trạng thái:** {unit.get('status', '—')}")
        goals = unit.get("goals") or []
        if goals:
            st.markdown("**Mục tiêu:**")
            for g in goals:
                st.markdown(f"- {g}")
        notes = unit.get("notes")
        if notes:
            st.caption(notes)

    st.divider()

    # --- T04: TTS độc lập (không cần micro) ---
    st.subheader("Nghe thử TTS (giọng AI)")
    st.caption(
        "Phát câu hỏi mẫu Unit 1 bằng Text-to-Speech. "
        "Không phụ thuộc micro — dùng để kiểm tra T04."
    )
    if is_mock_mode():
        st.info(
            "**Mock TTS** đang bật (chưa có `OPENAI_API_KEY`). "
            "Sẽ phát tiếng bip ngắn thay cho giọng thật."
        )
    st.markdown(f"**Nội dung AI:** {SAMPLE_AI_LINE}")
    _render_tts_section(SAMPLE_AI_LINE, "tts_sample")

    st.divider()

    # --- T02 + T03: Thu âm → STT → xác nhận ---
    st.subheader("Thu âm và nhận dạng")
    st.caption(
        "Ghi âm bằng micro. Sau khi dừng, hệ thống chuyển thành chữ (STT). "
        "Bạn có thể xác nhận transcript hoặc ghi âm lại."
    )

    if is_mock_mode():
        st.info(
            "**Mock STT** đang bật (chưa có `OPENAI_API_KEY` trong `.env`). "
            "Transcript mẫu sẽ được trả về để thử UI."
        )

    audio_value = st.audio_input(
        "Ghi âm giọng nói của bạn",
        sample_rate=16000,
        key="practice_audio",
        help="Cho phép trình duyệt truy cập micro khi được hỏi.",
    )

    if is_audio_empty(audio_value):
        st.warning("Chưa có bản ghi âm hoặc dữ liệu rỗng. Hãy ghi âm rồi thử lại.")
        for k in (
            "last_audio_bytes",
            "last_audio_size",
            "stt_fp",
            "stt_text",
            "stt_error",
            "stt_mock",
            "transcript_confirmed",
            "confirmed_transcript",
        ):
            st.session_state.pop(k, None)
        st.divider()
        st.info("Bước tiếp theo (T05+): AI Teacher (LLM) sẽ tạo câu hỏi theo Unit.")
        return

    raw = audio_value.getvalue()
    size = len(raw)
    fp = audio_fingerprint(raw)
    st.session_state["last_audio_bytes"] = raw
    st.session_state["last_audio_size"] = size

    st.success(f"Đã nhận bản ghi âm ({size:,} bytes, WAV).")
    st.audio(audio_value, format="audio/wav")

    need_stt = st.session_state.get("stt_fp") != fp
    if need_stt:
        with st.spinner("Đang nhận dạng giọng nói…"):
            result = transcribe_audio(raw, language="en")
        st.session_state["stt_fp"] = fp
        st.session_state["stt_text"] = result.text
        st.session_state["stt_error"] = result.error
        st.session_state["stt_mock"] = result.mock
        st.session_state["transcript_confirmed"] = False

    stt_error = st.session_state.get("stt_error")
    stt_text = st.session_state.get("stt_text") or ""
    stt_mock = st.session_state.get("stt_mock", False)

    if stt_error:
        st.error(stt_error)
        st.caption("Có thể do mạng, API key, hoặc dịch vụ tạm thời. Ghi âm lại hoặc thử sau.")
        if st.button("Thử nhận dạng lại", key="retry_stt"):
            st.session_state.pop("stt_fp", None)
            st.rerun()
    else:
        label = "Transcript (mock)" if stt_mock else "Transcript"
        st.markdown(f"**{label}:**")
        edited = st.text_area(
            "Nội dung nhận dạng",
            value=stt_text,
            height=100,
            key="transcript_edit",
            label_visibility="collapsed",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Xác nhận transcript", type="primary", key="confirm_tx"):
                st.session_state["stt_text"] = edited.strip()
                st.session_state["transcript_confirmed"] = True
                st.session_state["confirmed_transcript"] = edited.strip()
                st.rerun()
        with col2:
            st.caption("Muốn ghi lại: xóa bản ghi ở widget micro rồi thu âm mới.")

        if st.session_state.get("transcript_confirmed"):
            confirmed = st.session_state.get("confirmed_transcript") or ""
            st.success(f"Đã xác nhận: **{confirmed}**")
            st.markdown("**Nghe lại transcript (TTS):**")
            if confirmed:
                _render_tts_section(confirmed, "tts_confirmed")

    st.divider()
    st.info("Bước tiếp theo (T05+): AI Teacher (LLM) sẽ tạo câu hỏi theo Unit.")


if __name__ == "__main__":
    main()
