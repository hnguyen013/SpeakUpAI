"""SpeakUp AI – Home: chọn Unit (T01) + thu âm (T02) + STT (T03)."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from services.stt import audio_fingerprint, is_mock_mode, transcribe_audio

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


def main() -> None:
    st.set_page_config(page_title="SpeakUp AI", page_icon="🎤", layout="centered")
    st.title("🎤 SpeakUp AI")
    st.caption("Luyện nghe – nói tiếng Anh lớp 8 | Global Success")

    units = load_units()
    if not units:
        st.error("Không tìm thấy file Unit trong thư mục `units/`.")
        return

    # Map display label -> unit dict
    options = {f"{u['id']} – {u['title']}": u for u in units}
    labels = list(options.keys())

    # Restore previous selection if still valid
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

    # Persist selection
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

    # --- T02 + T03: Thu âm → STT → xác nhận / ghi lại ---
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
        ):
            st.session_state.pop(k, None)
        st.divider()
        st.info("Bước tiếp theo (T04+): TTS và AI Teacher sẽ dùng transcript đã xác nhận.")
        return

    raw = audio_value.getvalue()
    size = len(raw)
    fp = audio_fingerprint(raw)
    st.session_state["last_audio_bytes"] = raw
    st.session_state["last_audio_size"] = size

    st.success(f"Đã nhận bản ghi âm ({size:,} bytes, WAV).")
    st.audio(audio_value, format="audio/wav")

    # Avoid re-calling API on Streamlit rerun for the same clip
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
        # Cho phép sửa nhẹ trước khi xác nhận (STT có thể nhận sai)
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
                st.rerun()
        with col2:
            st.caption("Muốn ghi lại: xóa bản ghi ở widget micro rồi thu âm mới.")

        if st.session_state.get("transcript_confirmed"):
            st.success(f"Đã xác nhận: **{st.session_state['stt_text']}**")
            st.session_state["confirmed_transcript"] = st.session_state["stt_text"]

    st.divider()
    st.info("Bước tiếp theo (T04+): TTS và AI Teacher sẽ dùng transcript đã xác nhận.")


if __name__ == "__main__":
    main()
