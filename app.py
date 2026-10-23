"""SpeakUp AI – Unit, audio, STT, TTS, AI Teacher (T01–T05)."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from services.llm import generate_teacher_turn, prompt_fingerprint
from services.stt import audio_fingerprint, is_mock_mode, transcribe_audio
from services.tts import synthesize_speech, text_fingerprint

load_dotenv()

UNITS_DIR = Path(__file__).parent / "units"


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


def _render_llm_text_lab(unit: dict) -> None:
    """T05: text-only AI Teacher lab (no microphone)."""
    st.subheader("AI Teacher (thử bằng văn bản)")
    st.caption(
        "T05 – tạo câu hỏi/đáp theo Unit, **không cần micro**. "
        "Trong buổi thật sẽ không sửa lỗi từng lượt (chỉ hội thoại tự nhiên)."
    )
    if is_mock_mode():
        st.info(
            "**Mock LLM** đang bật (chưa có `OPENAI_API_KEY`). "
            "Câu trả lời mẫu cố định theo Unit."
        )

    if "llm_history" not in st.session_state:
        st.session_state["llm_history"] = []

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Câu hỏi mở đầu (opening)", key="llm_opening"):
            fp = prompt_fingerprint(unit["id"], "", st.session_state["llm_history"], "opening")
            with st.spinner("AI đang soạn câu hỏi…"):
                result = generate_teacher_turn(
                    unit, mode="opening", history=st.session_state["llm_history"]
                )
            st.session_state["llm_last_fp"] = fp
            st.session_state["llm_last_text"] = result.text
            st.session_state["llm_last_error"] = result.error
            st.session_state["llm_last_mock"] = result.mock
            if result.text and not result.error:
                st.session_state["llm_history"] = st.session_state["llm_history"] + [
                    {"role": "teacher", "text": result.text}
                ]
            st.rerun()
    with c2:
        if st.button("Xóa lịch sử thử", key="llm_clear"):
            st.session_state["llm_history"] = []
            for k in ("llm_last_fp", "llm_last_text", "llm_last_error", "llm_last_mock"):
                st.session_state.pop(k, None)
            st.rerun()

    student_in = st.text_input(
        "Lời học sinh (gõ tiếng Anh)",
        key="llm_student_input",
        placeholder="e.g. I like playing football with my friends.",
    )
    if st.button("AI đáp lại (follow-up)", type="primary", key="llm_followup"):
        hist = st.session_state.get("llm_history") or []
        fp = prompt_fingerprint(unit["id"], student_in, hist, "followup")
        # Skip duplicate identical request only if same fp already stored as last
        with st.spinner("AI đang đáp…"):
            result = generate_teacher_turn(
                unit,
                student_text=student_in,
                history=hist,
                mode="followup",
            )
        st.session_state["llm_last_fp"] = fp
        st.session_state["llm_last_text"] = result.text
        st.session_state["llm_last_error"] = result.error
        st.session_state["llm_last_mock"] = result.mock
        if result.text and not result.error:
            st.session_state["llm_history"] = hist + [
                {"role": "student", "text": student_in.strip()},
                {"role": "teacher", "text": result.text},
            ]
        st.rerun()

    err = st.session_state.get("llm_last_error")
    text = st.session_state.get("llm_last_text") or ""
    mock = st.session_state.get("llm_last_mock", False)

    if err:
        st.error(err)
    elif text:
        tag = " (mock)" if mock else ""
        st.success(f"AI Teacher{tag}: **{text}**")
        with st.expander("Nghe TTS câu AI", expanded=False):
            _render_tts_section(text, "tts_llm")

    hist = st.session_state.get("llm_history") or []
    if hist:
        with st.expander(f"Lịch sử thử ({len(hist)} lượt)", expanded=True):
            for i, turn in enumerate(hist, 1):
                who = "🧑 Học sinh" if turn.get("role") == "student" else "🤖 AI"
                st.markdown(f"{i}. {who}: {turn.get('text', '')}")


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
    _render_llm_text_lab(unit)

    st.divider()

    # --- T04: TTS sample ---
    st.subheader("Nghe thử TTS (giọng AI)")
    st.caption("Phát câu AI gần nhất hoặc câu mẫu nếu chưa có.")
    sample = st.session_state.get("llm_last_text") or (
        "Hi! What do you usually do in your free time?"
    )
    if is_mock_mode():
        st.info("**Mock TTS** – bip ngắn nếu chưa có API key.")
    st.markdown(f"**Nội dung:** {sample}")
    _render_tts_section(sample, "tts_sample")

    st.divider()

    # --- T02 + T03: Thu âm → STT ---
    st.subheader("Thu âm và nhận dạng")
    st.caption("Ghi âm → STT → xác nhận transcript (độc lập với lab LLM ở trên).")

    if is_mock_mode():
        st.info("**Mock STT** đang bật khi chưa có `OPENAI_API_KEY`.")

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
        st.info("Bước tiếp theo (T06): quản lý session_id, turn_id và lịch sử hội thoại.")
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
            st.caption("Ghi lại: xóa bản ghi ở widget micro rồi thu âm mới.")

        if st.session_state.get("transcript_confirmed"):
            confirmed = st.session_state.get("confirmed_transcript") or ""
            st.success(f"Đã xác nhận: **{confirmed}**")
            if confirmed:
                st.markdown("**Nghe lại transcript (TTS):**")
                _render_tts_section(confirmed, "tts_confirmed")

    st.divider()
    st.info("Bước tiếp theo (T06): quản lý session_id, turn_id và lịch sử hội thoại.")


if __name__ == "__main__":
    main()
