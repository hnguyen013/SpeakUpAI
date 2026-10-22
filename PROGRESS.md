# PROGRESS.md – Nhật ký tiến độ

## Trạng thái hiện tại
- **Task đang làm:** T02 (code đã đẩy, chờ nghiệm thu thu âm trên máy thật)
- **Task đã nghiệm thu:** T00, T01
- **Mốc tiếp theo:** T02 – Thu âm bằng `st.audio_input()`, phát lại, kiểm tra dữ liệu rỗng.
- **Blocker:** Cần xác nhận record/playback trên máy có micro (trình duyệt).

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
- **Thực hiện:** Thêm section "Thu âm thử" sau chọn Unit. Dùng `st.audio_input(..., sample_rate=16000)`. Hàm `is_audio_empty()` kiểm tra None hoặc `getvalue()` rỗng → warning. Có dữ liệu → success + `st.audio` phát lại + lưu `last_audio_bytes` / `last_audio_size` vào session_state. Giữ nguyên T01.
- **File thay đổi:** `app.py`.
- **Cách kiểm thử (đã chạy):** unit test `is_audio_empty(None)` / FakeEmpty / FakeAudio; `compile(app.py)`. **Chưa chạy:** record/playback micro thật trên trình duyệt.
- **Kết quả:** CHƯA KIỂM THỬ (phần micro trên máy thật)
- **Vấn đề còn lại:** Cần người dùng chạy `streamlit run app.py`, cho phép micro, ghi âm và nghe lại để nghiệm thu.
- **Task tiếp theo:** Sau khi PASS T02 → T03 (STT).
