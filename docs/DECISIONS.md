# Quyết định kỹ thuật (Architecture Decision Log)

## D001 – Chọn Streamlit, chưa dùng FastAPI
- Lý do: ít thành phần, Python thống nhất, dễ học và demo.

## D002 – AI xử lý qua API
- STT → LLM → TTS (theo từng lượt), không phải hội thoại realtime.

## D003 – Feedback cuối buổi
- Trong buổi chỉ hiện phụ đề lời học sinh và nội dung đáp lời AI; không xen lời nhận xét/sửa lỗi.
- Khi kết thúc, AI phân tích toàn bộ transcript đã được xác nhận.

## D004 – SQLite cho MVP
- Thuận tiện cho MVP; cần ổ bền vững nếu deploy cloud.

## D005 – Phạm vi ban đầu
- Lớp 8 Global Success; hoàn chỉnh Unit 1 trước.

## D006 – STT OpenAI Whisper (T03)
- `whisper-1`, language=`en`; mock khi không key; fingerprint audio.

## D007 – TTS OpenAI (T04)
- `tts-1`, voice `nova`, mp3; mock WAV bip.

## D008 – LLM AI Teacher (T05)
- `gpt-4o-mini`; opening/followup; không sửa lỗi giữa buổi; mock leisure-time.

## D009 – Session state (T06)
- `practice_session` trong `st.session_state`: session_id, turns, last_request_fp.

## D010 – Hội thoại ghép STT→LLM→TTS (T07)
- UI một vòng: opening TTS → thu âm/STT phụ đề → xác nhận (không chấm lỗi) → LLM follow-up → TTS.
- Mục tiêu nghiệm thu: ~5 lượt học sinh Unit 1; tab gõ chữ để thử nhanh khi không micro.
- Mọi lượt ghi vào `practice_session`; dedupe fingerprint giữ từ T06.
