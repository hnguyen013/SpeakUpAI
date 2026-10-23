# PROGRESS.md – Nhật ký tiến độ

## Trạng thái hiện tại
- **Task đang làm:** T05 (code đã đẩy, chờ nghiệm thu LLM mock + thật bằng văn bản)
- **Task đã nghiệm thu:** T00–T04
- **Mốc tiếp theo:** T05 – AI Teacher theo Unit 1, test text-only.
- **Blocker:** Không có (mock mode không cần key).

## Nhật ký
### 2026-10-23 – T04 – Text-to-Speech
- **Kết quả:** PASS (người dùng nghiệm thu)

### 2026-10-23 – T05 – AI Teacher (LLM)
- **Thực hiện:** `services/llm.py` – `gpt-4o-mini`, mode opening/followup, system prompt giới hạn Unit 1 / A2 / không sửa lỗi giữa buổi; mock câu leisure time; `prompt_fingerprint`. UI lab văn bản: opening, gõ lời học sinh, follow-up, lịch sử, TTS câu AI. D008.
- **File thay đổi:** `services/llm.py` (mới), `app.py`, `docs/DECISIONS.md`, `.env.example`, `TASKS.md` (T04 [x]), `PROGRESS.md`.
- **Cách kiểm thử:** unit mock opening/followup/empty; compile. **Chờ:** người dùng bấm opening + gõ tiếng Anh trên UI (mock hoặc có key).
- **Kết quả:** CHƯA KIỂM THỬ đầy đủ trên máy người dùng
- **Task tiếp theo:** Sau PASS T05 → T06 (session_state).
