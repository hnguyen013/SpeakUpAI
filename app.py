"""SpeakUp AI – hội thoại + feedback cuối buổi (T01–T08)."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from services.feedback import (
    feedback_fingerprint,
    generate_feedback,
    student_lines_from_session,
)
from services.llm import generate_teacher_turn, prompt_fingerprint
from services.session import (
    append_turn,
    create_session,
    end_session,
    ensure_session,
    history_for_llm,
    should_skip_request,
    turn_count,
)
from services.stt import audio_fingerprint, is_mock_mode, transcribe_audio
from services.tts import synthesize_speech, text_fingerprint

load_dotenv()

UNITS_DIR = Path(__file__).parent / "units"
SS_PRACTICE = "practice_session"
TARGET_STUDENT_TURNS = 5


def load_units() -> list[dict]:
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
    if audio_value is None:
        return True
    try:
        return len(audio_value.getvalue()) == 0
    except Exception:
        return True


def _get_practice_session(unit_id: str) -> dict:
    sess = ensure_session(st.session_state.get(SS_PRACTICE), unit_id)
    st.session_state[SS_PRACTICE] = sess
    return sess


def _student_turn_count(sess: dict) -> int:
    return sum(1 for t in (sess.get("turns") or []) if t.get("role") == "student")


def _last_teacher_text(sess: dict) -> str:
    for t in reversed(sess.get("turns") or []):
        if t.get("role") == "teacher" and (t.get("text") or "").strip():
            return t["text"].strip()
    return ""


def _play_tts(text: str, state_prefix: str) -> None:
    if not (text or "").strip():
        return
    fp = text_fingerprint(text)
    fp_key = f"{state_prefix}_fp"
    bytes_key = f"{state_prefix}_bytes"
    fmt_key = f"{state_prefix}_fmt"
    err_key = f"{state_prefix}_error"
    mock_key = f"{state_prefix}_mock"

    if st.session_state.get(fp_key) != fp:
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
        return
    if not audio_b:
        return
    tag = " (mock bip)" if mock else ""
    st.caption(f"Giọng AI{tag}")
    st.audio(audio_b, format=fmt)


def _start_opening(unit: dict, sess: dict) -> None:
    hist = history_for_llm(sess)
    fp = prompt_fingerprint(unit["id"], "", hist, "opening")
    if should_skip_request(sess, fp):
        return
    with st.spinner("AI đang mở đầu…"):
        result = generate_teacher_turn(unit, mode="opening", history=hist)
    if result.error:
        st.session_state["conv_error"] = result.error
        return
    if result.text:
        append_turn(sess, "teacher", result.text, request_fp=fp)
        st.session_state[SS_PRACTICE] = sess
        st.session_state["conv_error"] = None
        st.session_state.pop("pending_stt_fp", None)
        st.session_state.pop("pending_transcript", None)


def _complete_student_turn(unit: dict, sess: dict, student_text: str) -> None:
    cleaned = (student_text or "").strip()
    if not cleaned:
        st.session_state["conv_error"] = "Transcript trống."
        return
    hist = history_for_llm(sess)
    fp = prompt_fingerprint(unit["id"], cleaned, hist, "followup")
    if should_skip_request(sess, fp):
        return
    with st.spinner("AI đang đáp…"):
        result = generate_teacher_turn(
            unit, student_text=cleaned, history=hist, mode="followup"
        )
    if result.error:
        st.session_state["conv_error"] = result.error
        return
    append_turn(sess, "student", cleaned)
    if result.text:
        append_turn(sess, "teacher", result.text, request_fp=fp)
    st.session_state[SS_PRACTICE] = sess
    st.session_state["conv_error"] = None
    st.session_state.pop("pending_stt_fp", None)
    st.session_state.pop("pending_transcript", None)


def _render_feedback(unit: dict, sess: dict) -> None:
    """T08: end-of-session feedback panel."""
    st.subheader("Feedback cuối buổi")
    st.caption(
        "Chỉ dựa trên transcript đã xác nhận. "
        "**Không** chấm phát âm từ chữ viết."
    )

    lines = student_lines_from_session(sess)
    if not lines:
        st.info("Chưa có lời học sinh trong phiên — luyện vài lượt rồi xem feedback.")
        return

    fp = feedback_fingerprint(unit["id"], lines)
    if (
        st.session_state.get("fb_fp") != fp
        or st.session_state.get("fb_report") is None
        or st.button("Tạo / làm mới feedback", key="fb_refresh")
    ):
        with st.spinner("Đang tổng hợp feedback…"):
            report = generate_feedback(unit, sess)
        st.session_state["fb_fp"] = fp
        st.session_state["fb_report"] = report.to_dict()

    data = st.session_state.get("fb_report") or {}
    if data.get("error"):
        st.error(data["error"])
        return

    tag = " (mock)" if data.get("mock") else ""
    st.markdown(f"**Báo cáo{tag}**")

    strengths = data.get("strengths") or []
    if strengths:
        st.markdown("#### Điểm tốt")
        for s in strengths:
            st.markdown(f"- {s}")

    issues = data.get("issues") or []
    if issues:
        st.markdown("#### Gợi ý sửa (dựa trên transcript)")
        for i, iss in enumerate(issues, 1):
            st.markdown(
                f"**{i}. [{iss.get('category', 'other')}]**  \n"
                f"- Evidence: _{iss.get('evidence', '')}_  \n"
                f"- Suggestion: **{iss.get('suggestion', '')}**  \n"
                f"- Note: {iss.get('note', '')}"
            )
    else:
        st.markdown("#### Gợi ý sửa")
        st.write("Không thấy lỗi ngôn ngữ rõ trên transcript đã xác nhận.")

    uncertain = data.get("uncertain_transcripts") or []
    if uncertain:
        st.markdown("#### Transcript chưa chắc")
        st.caption("Có thể do STT — không tính là lỗi phát âm.")
        for u in uncertain:
            st.markdown(f"- _{u}_")

    tips = data.get("practice_tips") or []
    if tips:
        st.markdown("#### Luyện thêm")
        for t in tips:
            st.markdown(f"- {t}")

    with st.expander("JSON schema (debug)", expanded=False):
        st.json(data)


def _render_conversation(unit: dict, sess: dict) -> None:
    st.subheader("Hội thoại luyện nói")
    st.caption(
        f"AI (TTS) → thu âm → phụ đề → xác nhận → AI tiếp. "
        f"Không sửa lỗi giữa buổi. Mục tiêu ~{TARGET_STUDENT_TURNS} lượt học sinh."
    )
    if is_mock_mode():
        st.info("Mock STT/LLM/TTS/Feedback đang bật (chưa có `OPENAI_API_KEY`).")

    if sess.get("status") != "active":
        st.warning("Phiên đã kết thúc.")
        _render_feedback(unit, sess)
        return

    n_student = _student_turn_count(sess)
    st.progress(
        min(1.0, n_student / TARGET_STUDENT_TURNS),
        text=f"Lượt học sinh: {n_student}/{TARGET_STUDENT_TURNS}",
    )

    if turn_count(sess) == 0:
        if st.button("Bắt đầu hội thoại", type="primary", key="conv_start"):
            _start_opening(unit, sess)
            st.rerun()
        st.caption("AI sẽ chào và hỏi về leisure time.")
        return

    turns = sess.get("turns") or []
    with st.expander(f"Phụ đề & lịch sử ({len(turns)} lượt)", expanded=True):
        for t in turns:
            who = "🧑 Bạn" if t.get("role") == "student" else "🤖 AI"
            st.markdown(f"**#{t.get('turn_id')}** {who}: {t.get('text', '')}")

    teacher_line = _last_teacher_text(sess)
    if teacher_line:
        st.markdown(f"**AI nói:** {teacher_line}")
        _play_tts(teacher_line, "tts_teacher_live")

    if n_student >= TARGET_STUDENT_TURNS:
        st.success(f"Đã đủ {TARGET_STUDENT_TURNS} lượt học sinh.")
        if st.button("Kết thúc phiên & xem feedback", type="primary", key="conv_end_ok"):
            end_session(sess)
            st.session_state[SS_PRACTICE] = sess
            st.session_state.pop("fb_fp", None)
            st.session_state.pop("fb_report", None)
            st.rerun()

    err = st.session_state.get("conv_error")
    if err:
        st.error(err)

    st.markdown("**Lượt của bạn**")
    tab_mic, tab_text = st.tabs(["Thu âm (STT)", "Gõ chữ (thử nhanh)"])

    with tab_mic:
        audio_value = st.audio_input(
            "Ghi âm câu trả lời",
            sample_rate=16000,
            key="conv_audio",
        )
        if not is_audio_empty(audio_value):
            raw = audio_value.getvalue()
            fp = audio_fingerprint(raw)
            st.audio(audio_value, format="audio/wav")
            if st.session_state.get("pending_stt_fp") != fp:
                with st.spinner("Đang nhận dạng…"):
                    stt = transcribe_audio(raw, language="en")
                st.session_state["pending_stt_fp"] = fp
                st.session_state["pending_transcript"] = stt.text
                st.session_state["pending_stt_error"] = stt.error
                st.session_state["pending_stt_mock"] = stt.mock

            if st.session_state.get("pending_stt_error"):
                st.error(st.session_state["pending_stt_error"])
                if st.button("Thử STT lại", key="conv_stt_retry"):
                    st.session_state.pop("pending_stt_fp", None)
                    st.rerun()
            else:
                mock = st.session_state.get("pending_stt_mock", False)
                label = "Phụ đề (mock)" if mock else "Phụ đề"
                edited = st.text_area(
                    label,
                    value=st.session_state.get("pending_transcript") or "",
                    key="conv_transcript_edit",
                    height=80,
                )
                st.caption("Chỉ phụ đề — không sửa lỗi ngữ pháp ở bước này.")
                if st.button("Xác nhận & gửi cho AI", type="primary", key="conv_confirm_mic"):
                    _complete_student_turn(unit, sess, edited)
                    st.rerun()
        else:
            st.caption("Thu âm xong để hiện phụ đề.")

    with tab_text:
        typed = st.text_input(
            "Gõ câu tiếng Anh",
            key="conv_text_input",
            placeholder="I usually play football after school.",
        )
        if st.button("Gửi câu đã gõ", key="conv_confirm_text"):
            _complete_student_turn(unit, sess, typed)
            st.rerun()


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
        "Unit đang học", options=labels, index=default_index, key="unit_select"
    )
    unit = options[chosen_label]
    st.session_state["selected_unit_id"] = unit["id"]
    st.session_state["selected_unit"] = unit
    st.success(f"Đã chọn: **{unit['title']}** (`{unit['id']}`)")

    with st.expander("Chi tiết Unit", expanded=False):
        st.markdown(f"**Sách:** {unit.get('book', '—')} – Lớp {unit.get('grade', '—')}")
        goals = unit.get("goals") or []
        if goals:
            st.markdown("**Mục tiêu:**")
            for g in goals:
                st.markdown(f"- {g}")

    st.divider()

    sess = _get_practice_session(unit["id"])
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Lượt (tổng)", turn_count(sess))
    with c2:
        st.caption("session_id")
        sid = sess.get("session_id") or ""
        st.code((sid[:8] + "…") if sid else "—", language=None)
    with c3:
        st.write(sess.get("status", "—"))

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Bắt đầu phiên mới", key="sess_new"):
            st.session_state[SS_PRACTICE] = create_session(unit["id"])
            for k in list(st.session_state.keys()):
                if (
                    k.startswith("tts_")
                    or k.startswith("pending_")
                    or k.startswith("fb_")
                    or k in {"conv_error"}
                ):
                    st.session_state.pop(k, None)
            st.rerun()
    with b2:
        if sess.get("status") == "active" and st.button("Kết thúc phiên", key="sess_end"):
            end_session(sess)
            st.session_state[SS_PRACTICE] = sess
            st.session_state.pop("fb_fp", None)
            st.session_state.pop("fb_report", None)
            st.rerun()

    st.divider()
    _render_conversation(unit, sess)

    st.divider()
    st.caption("T08 feedback sau khi kết thúc phiên. Lưu DB → T09–T10.")


if __name__ == "__main__":
    main()
