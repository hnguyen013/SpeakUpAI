# SpeakUp AI

**Ứng dụng hỗ trợ luyện nghe – nói tiếng Anh dành cho học sinh lớp 8, theo sách Global Success.**

## Mục tiêu
- Học sinh chọn Unit và hội thoại bằng giọng nói với AI theo từng lượt.
- Sau mỗi lượt nói: hiển thị phụ đề, **không sửa lỗi hoặc đọc nhận xét**; AI tiếp tục hội thoại tự nhiên.
- Sau khi kết thúc buổi: AI tổng hợp lỗi ngôn ngữ, điểm tốt và gợi ý cải thiện.
- Lưu phiên học, transcript, feedback, tiến độ vào SQLite để cá nhân hóa các buổi sau.

## Công nghệ đã chốt
- **Giao diện & quản lý phiên:** Python + Streamlit
- **AI:** Speech-to-Text (STT), LLM, Text-to-Speech (TTS) qua API
- **Lưu trữ:** SQLite
- **Chưa dùng FastAPI**, React, FlutterFlow hoặc MIT App Inventor ở MVP.
- **Không chấm phát âm** dựa trên transcript. AI chỉ nhận xét nội dung/diễn đạt khi chưa có mô hình đánh giá âm học.

## Luồng học dự kiến
`Chọn Unit → AI phát câu hỏi → Học sinh thu âm → STT hiện phụ đề → AI trả lời bằng giọng nói → lặp lại → Kết thúc → Feedback → Lưu tiến độ → Đề xuất luyện tập`

> STT có thể nhận sai lời học sinh: cần cơ chế nghe lại/ghi âm lại hoặc xác nhận transcript trước khi đưa vào phân tích lỗi.

## Tiến độ
- Danh sách công việc và điều kiện hoàn thành: [TASKS.md](TASKS.md)
- Quy tắc dành cho AI/cộng tác viên: [AGENTS.md](AGENTS.md)
- Nhật ký các mốc hoàn thành: [PROGRESS.md](PROGRESS.md)
- Quyết định kỹ thuật: [docs/DECISIONS.md](docs/DECISIONS.md)

## Cấu trúc repository
```text
SpeakUpAI/
├── app.py                     # Giao diện Streamlit mẫu T00
├── services/                  # Các mô-đun AI và cá nhân hóa (tạo ở task tương ứng)
├── units/                     # Cấu hình Unit Global Success 8
├── tests/                     # Kiểm thử
├── docs/                      # Tài liệu kiến trúc và quyết định
├── .github/ISSUE_TEMPLATE/    # Mẫu issue cho từng task
├── .env.example               # Tên biến môi trường, không có bí mật
├── .gitignore
├── requirements.txt
├── README.md
├── AGENTS.md
├── TASKS.md
└── PROGRESS.md
```

## Bắt đầu (T00)
Yêu cầu: Python 3.11+ (khuyến nghị, có thể dùng phiên bản tương thích với Streamlit).

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Mở địa chỉ do Streamlit hiển thị (thường là `http://localhost:8501`). Hiện tại chỉ có **giao diện khung**, chưa kết nối AI/SQLite.

## Quy tắc an toàn dữ liệu
- Không commit `.env`, API key, file `.db` thật, audio của học sinh hoặc nhật ký chứa thông tin cá nhân.
- Chỉ lưu dữ liệu cần thiết; hạn chế lưu audio gốc; sử dụng mã học sinh giả khi demo.
- Nếu deploy lên cloud, SQLite phải có ổ đĩa lưu trữ bền vững; không mặc định file trên host tồn tại mãi.
- Người dùng cần được thông báo về việc xử lý âm thanh và dữ liệu, có sự đồng ý phù hợp với học sinh chưa thành niên.

## Phạm vi MVP
Hoàn chỉnh **Unit 1 – Leisure Time** trước. Sau khi chạy ổn định mới mở rộng các Unit khác.
