# PROGRESS.md – Nhật ký tiến độ

## Trạng thái hiện tại
- **Task đang làm:** T04 (code đã đẩy, chờ nghiệm thu TTS mock + thật)
- **Task đã nghiệm thu:** T00, T01, T02, T03
- **Mốc tiếp theo:** T04 – TTS, phát lại, mock và bắt lỗi.
- **Blocker:** Không có (mock mode chạy không cần key).

## Nhật ký
### 2026-10-22 – T00 / T01 / T02
- Đã nghiệm thu (xem các mục trước).

### 2026-10-23 – T03 – Speech-to-Text
- **Thực hiện:** `services/stt.py` Whisper + mock; UI transcript/xác nhận/ghi lại.
- **Kết quả:** PASS (người dùng nghiệm thu)
- **Task tiếp theo:** T04

### 2026-10-23 – T04 – Text-to-Speech
- **Thực hiện:** `services/tts.py` – OpenAI `tts-1` / voice `nova` / mp3; mock = WAV bip pure Python; fingerprint text tránh gọi trùng; bắt lỗi. UI: section "Nghe thử TTS" (câu mẫu Unit 1, không cần micro) + TTS transcript đã xác nhận. D007.
- **File thay đổi:** `services/tts.py` (mới), `app.py`, `docs/DECISIONS.md`, `.env.example`, `TASKS.md` (T03 [x]), `PROGRESS.md`.
- **Cách kiểm thử:** unit mock empty/text/fingerprint; compile. **Chờ:** playback mock bip + TTS thật với key trên máy người dùng.
- **Kết quả:** CHƯA KIỂM THỬ đầy đủ (logic mock sẵn)
- **Vấn đề còn lại:** `git pull` → `streamlit run app.py` → nghe section TTS (bip nếu mock; giọng nova nếu có key).
- **Task tiếp theo:** Sau PASS T04 → T05 (LLM).
