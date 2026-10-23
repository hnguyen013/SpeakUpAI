# PROGRESS.md – Nhật ký tiến độ

## Trạng thái hiện tại
- **Task đang làm:** T03 (code đã đẩy, chờ nghiệm thu STT mock + thật)
- **Task đã nghiệm thu:** T00, T01, T02
- **Mốc tiếp theo:** T03 – STT, transcript, xác nhận/ghi lại.
- **Blocker:** Không có (mock mode chạy không cần key).

## Mẫu ghi nhật ký (chép cho mỗi task)
### YYYY-MM-DD – Txx – Tên task
- **Thực hiện:** ...
- **File thay đổi:** ...
- **Cách kiểm thử:** ...
- **Kết quả:** PASS/FAIL/CHƯA KIỂM THỬ
- **Vấn đề còn lại:** ...
- **Task tiếp theo:** ...

## Nhật ký
### 2026-10-22 – Chuẩn bị repository
- **Thực hiện:** Tạo bộ khung tài liệu, file cấu hình và giao diện Home tối thiểu.
- **File thay đổi:** README.md, AGENTS.md, TASKS.md, PROGRESS.md, app.py, requirements.txt, .gitignore, .env.example, units/unit01.json, docs/DECISIONS.md.
- **Kết quả:** Chưa kiểm thử thực tế trên thiết bị của người dùng. Không đánh dấu T00 hoàn thành.

### 2026-10-22 – T00 – Cài môi trường và khởi chạy Home mẫu
- **Thực hiện:** Kiểm tra `.gitignore` (che `.env`, `.venv/`, `*.db`, audio). Tạo venv Python 3.12, cài `requirements.txt` (streamlit 1.66.1, python-dotenv). Chạy `streamlit run app.py` (headless), nhận HTTP 200, trang Home hiển thị đúng tiêu đề và caption. `app.py` compile OK. Commit đầu đã có sẵn trên `main`.
- **File thay đổi:** `TASKS.md` (đánh dấu `[x]` T00), `PROGRESS.md` (nhật ký này).
- **Cách kiểm thử:** `python -m venv .venv` → `source .venv/bin/activate` → `pip install -r requirements.txt` → `streamlit run app.py` → mở http://localhost:8501; `git check-ignore` xác nhận rule; `python -c "compile(open('app.py').read(), ...)"`.
- **Kết quả:** PASS
- **Vấn đề còn lại:** Cần xác nhận thêm trên máy Windows/macOS của người phát triển nếu khác môi trường Linux.
- **Task tiếp theo:** T01

### 2026-10-22 – T01 – Trang Home chọn Unit từ JSON
- **Thực hiện:** Viết `load_units()` đọc `units/unit*.json`. Hiển thị selectbox chọn Unit, lưu `selected_unit_id` và `selected_unit` vào `st.session_state`. Hiển thị chi tiết Unit (title, goals, book, grade, status). Ứng dụng khởi động không lỗi, HTTP 200.
- **File thay đổi:** `app.py` (thay giao diện khung bằng chọn Unit).
- **Cách kiểm thử:** `python -c "from app import load_units; assert load_units()[0]['id']=='unit01'"`; `streamlit run app.py` → chọn Unit 1 → xác nhận success message và expander chi tiết; reload trang vẫn giữ lựa chọn nhờ session_state.
- **Kết quả:** PASS
- **Vấn đề còn lại:** Hiện chỉ có Unit 1; thêm Unit sau ở T13. Chưa có nút "Bắt đầu luyện" (sẽ gắn ở task hội thoại).
- **Task tiếp theo:** T02

### 2026-10-22 – T02 – Thu âm st.audio_input, phát lại, kiểm tra rỗng
- **Thực hiện:** Thêm section "Thu âm thử". `st.audio_input(sample_rate=16000)`. `is_audio_empty()`; phát lại `st.audio`; lưu bytes vào session_state.
- **File thay đổi:** `app.py`.
- **Cách kiểm thử:** unit test empty/non-empty; compile; người dùng xác nhận record/playback trên máy thật.
- **Kết quả:** PASS (người dùng nghiệm thu)
- **Vấn đề còn lại:** Không có.
- **Task tiếp theo:** T03

### 2026-10-23 – T03 – Speech-to-Text, transcript, xác nhận/ghi lại
- **Thực hiện:** `services/stt.py` – Whisper API (`whisper-1`, language=en), mock khi không có key, fingerprint tránh gọi trùng khi rerun, bắt lỗi mạng/API. UI: hiện transcript, text_area sửa, nút Xác nhận, nút Thử lại khi lỗi; ghi âm lại bằng xóa widget micro. D006 ghi vào DECISIONS.
- **File thay đổi:** `services/stt.py` (mới), `app.py`, `requirements.txt` (openai), `.env.example`, `docs/DECISIONS.md`, `TASKS.md` (T02 [x]), `PROGRESS.md`.
- **Cách kiểm thử:** unit test mock + empty + fingerprint (chạy local); compile. **Chưa:** gọi Whisper thật với key + tiếng Anh thực tế trên máy người dùng.
- **Kết quả:** CHƯA KIỂM THỬ đầy đủ (mock logic sẵn; API thật cần key)
- **Vấn đề còn lại:** Người dùng cần `pip install -r requirements.txt`, (tuỳ chọn) điền `OPENAI_API_KEY` trong `.env`, chạy app, ghi âm tiếng Anh, xác nhận transcript.
- **Task tiếp theo:** Sau PASS T03 → T04 (TTS).
