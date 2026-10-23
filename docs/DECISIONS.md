# Quyết định kỹ thuật (Architecture Decision Log)

## D001 – Streamlit, chưa FastAPI
## D002 – STT → LLM → TTS theo lượt
## D003 – Feedback chỉ sau khi kết thúc phiên; không sửa lỗi giữa buổi
## D004 – SQLite MVP
## D005 – Unit 1 Global Success 8 trước
## D006 – STT Whisper
## D007 – TTS tts-1 nova
## D008 – LLM gpt-4o-mini teacher
## D009 – practice_session state
## D010 – Hội thoại ghép T07

## D011 – Feedback cuối buổi (T08)
- Schema: `strengths[]`, `issues[{category, evidence, suggestion, note}]`, `practice_tips[]`, `uncertain_transcripts[]`.
- Category: grammar | vocabulary | structure | unclear_transcript | other.
- **Cấm** suy diễn pronunciation/accent từ text; category pronunciation bị lọc bỏ.
- Chỉ dùng transcript học sinh đã xác nhận trong session.
- Mock heuristic (I playing → I play, …) + cờ unclear; LLM trả JSON khi có key.
