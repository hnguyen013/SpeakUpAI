# PROGRESS.md – Nhật ký tiến độ

## Trạng thái hiện tại
- **Task đang làm:** T07 (code đã đẩy, chờ hội thoại 5 lượt trên máy thật/mock)
- **Task đã nghiệm thu:** T00–T06
- **Mốc tiếp theo:** T07 – STT→LLM→TTS, 5 lượt Unit 1.
- **Blocker:** Không có (có tab gõ chữ + mock).

## Nhật ký
### 2026-10-23 – T06 – Session state
- **Kết quả:** PASS (người dùng nghiệm thu)

### 2026-10-23 – T07 – Ghép hội thoại STT→LLM→TTS
- **Thực hiện:** UI hội thoại: Bắt đầu → opening LLM+TTS → thu âm/STT phụ đề → xác nhận (không sửa lỗi) → follow-up LLM+TTS; progress 5 lượt học sinh; tab gõ chữ; session panel giữ T06. D010.
- **File thay đổi:** `app.py` (viết lại luồng chính), `docs/DECISIONS.md`, `TASKS.md` (T06 [x]), `PROGRESS.md`.
- **Cách kiểm thử:** mock – 5 lần gõ chữ + opening; hoặc micro thật. Compile app.
- **Kết quả:** CHƯA KIỂM THỬ đầy đủ trên máy người dùng
- **Task tiếp theo:** Sau PASS T07 → T08 (feedback cuối buổi).
