# PROGRESS.md – Nhật ký tiến độ

## Trạng thái hiện tại
- **Task đang làm:** T06 (code đã đẩy, chờ nghiệm thu session trên UI)
- **Task đã nghiệm thu:** T00–T05
- **Mốc tiếp theo:** T06 – session_id, turn_id, lịch sử, chống trùng request.
- **Blocker:** Không có.

## Nhật ký
### 2026-10-23 – T05 – AI Teacher
- **Kết quả:** PASS (người dùng nghiệm thu)

### 2026-10-23 – T06 – Session state
- **Thực hiện:** `services/session.py` – create_session, append_turn (dedupe theo fingerprint), end_session, ensure_session, history_for_llm, turn_count. UI panel phiên: session_id, số lượt, bắt đầu mới / kết thúc, lịch sử turn_id. Lab LLM ghi turn vào practice_session; skip request trùng.
- **File thay đổi:** `services/session.py` (mới), `app.py`, `docs/DECISIONS.md` (D009), `TASKS.md` (T05 [x]), `PROGRESS.md`.
- **Cách kiểm thử:** unit test create/append/dedupe/end/unit-change; compile. **Chờ:** UI – opening + follow-up, reload trang vẫn giữ lượt, bấm trùng không nhân đôi.
- **Kết quả:** CHƯA KIỂM THỬ đầy đủ trên máy người dùng
- **Task tiếp theo:** Sau PASS T06 → T07 (ghép STT→LLM→TTS).
