# PROGRESS.md – Nhật ký tiến độ

## Trạng thái hiện tại
- **Task đang làm:** (không có)
- **Task đã nghiệm thu:** T00
- **Mốc tiếp theo:** T01 – Trang Home hiển thị và chọn Unit 1 từ JSON.
- **Blocker:** Không có.

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
