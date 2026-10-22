"""SpeakUp AI – Home: chọn Unit (T01) + thu âm (T02)."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

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

    # --- T02: Thu âm, phát lại, kiểm tra rỗng ---
    st.subheader("Thu âm thử")
    st.caption(
        "Bấm nút micro bên dưới để ghi âm. Sau khi dừng, bản ghi sẽ được phát lại. "
        "Sample rate 16 kHz phù hợp nhận dạng giọng nói (STT ở T03)."
    )

    audio_value = st.audio_input(
        "Ghi âm giọng nói của bạn",
        sample_rate=16000,
        key="practice_audio",
        help="Cho phép trình duyệt truy cập micro khi được hỏi.",
    )

    if is_audio_empty(audio_value):
        st.warning("Chưa có bản ghi âm hoặc dữ liệu rỗng. Hãy ghi âm rồi thử lại.")
        st.session_state.pop("last_audio_bytes", None)
        st.session_state.pop("last_audio_size", None)
    else:
        raw = audio_value.getvalue()
        size = len(raw)
        st.session_state["last_audio_bytes"] = raw
        st.session_state["last_audio_size"] = size

        st.success(f"Đã nhận bản ghi âm ({size:,} bytes, WAV).")
        st.audio(audio_value, format="audio/wav")
        st.caption("Nghe lại bản ghi ở trên. Xóa hoặc ghi lại bằng widget thu âm nếu cần.")

    st.divider()
    st.info(
        "Bước tiếp theo (T03+): Speech-to-Text, hội thoại AI và feedback sẽ dùng "
        "Unit đã chọn và bản ghi âm ở trên."
    )


if __name__ == "__main__":
    main()
