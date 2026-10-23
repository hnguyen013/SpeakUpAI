# Quyết định kỹ thuật (Architecture Decision Log)

## D001 – Chọn Streamlit, chưa dùng FastAPI
- Lý do: ít thành phần, Python thống nhất, dễ học và demo.
- Xem xét lại khi số lượng người dùng đồng thời hoặc yêu cầu mở rộng tăng.

## D002 – AI xử lý qua API
- STT → LLM → TTS (theo từng lượt), không phải hội thoại realtime.
- Không cam kết độ trễ trước khi đo thực tế.

## D003 – Feedback cuối buổi
- Trong buổi chỉ hiện phụ đề lời học sinh và nội dung đáp lời AI; không xen lời nhận xét/sửa lỗi.
- Khi kết thúc, AI phân tích toàn bộ transcript đã được xác nhận.

## D004 – SQLite cho MVP
- Thuận tiện, không cần server DB riêng; cần lưu trữ bền vững nếu deploy lên cloud.

## D005 – Phạm vi ban đầu
- Lớp 8 Global Success; hoàn chỉnh Unit 1 trước, 12 Unit là mục tiêu mở rộng.

## D006 – STT dùng OpenAI Whisper (T03)
- Model: `whisper-1` qua API, language=`en`.
- API key chỉ từ `OPENAI_API_KEY` (python-dotenv); không hardcode.
- Không có key → **mock mode** trả transcript mẫu để phát triển UI offline.
- Lỗi mạng/API: trả message trong `STTResult.error`, không crash app.
- Fingerprint SHA-256 của audio bytes để tránh gọi lại API khi Streamlit rerun cùng clip.
- Học sinh được sửa/xác nhận transcript trước khi dùng cho bước sau (STT có thể nhận sai).
