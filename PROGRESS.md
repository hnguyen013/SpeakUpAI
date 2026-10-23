# PROGRESS.md

## Trạng thái hiện tại
- **Task đang làm:** T08 (chờ nghiệm thu feedback)
- **Task đã nghiệm thu:** T00–T07
- **Mốc tiếp theo:** T08 feedback schema

## Nhật ký
### 2026-10-23 – T07
- PASS (người dùng nghiệm thu) — MVP A

### 2026-10-23 – T08 – Feedback cuối buổi
- **Thực hiện:** `services/feedback.py` – schema strengths/issues/tips/uncertain; cấm pronunciation từ text; mock heuristic; LLM JSON. UI hiện sau khi kết thúc phiên. D011.
- **File:** `services/feedback.py`, `app.py`, `docs/DECISIONS.md`, `TASKS.md` (T07 [x]), `PROGRESS.md`.
- **Test gợi ý:** gõ "I playing football", "I goes to park", "[unclear] something"; kết thúc phiên → xem evidence/suggestion; không có mục pronunciation.
- **Kết quả:** CHƯA KIỂM THỬ trên máy người dùng
- **Tiếp theo:** PASS T08 → T09 SQLite
