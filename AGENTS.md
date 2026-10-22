# AGENTS.md – Quy tắc giao nhiệm vụ cho AI

Áp dụng cho mọi AI/cộng tác viên sửa repository này.

## Bối cảnh bất biến
- SpeakUp AI: luyện nghe–nói tiếng Anh lớp 8, sách Global Success.
- Stack: Streamlit + Python + AI APIs + SQLite. **Chưa dùng FastAPI.**
- Giao tiếp theo từng lượt. Trong buổi học chỉ hiện phụ đề, **không nhận xét/sửa lỗi từng lượt**; Feedback chỉ xuất hiện **sau khi kết thúc phiên**.
- Không chấm phát âm chỉ bằng text transcript.

## Quy trình bắt buộc cho mỗi task
1. Đọc `README.md`, `TASKS.md`, `PROGRESS.md` và các file liên quan.
2. Chỉ làm **một task ID** được giao; không tự thêm feature/phụ thuộc/framework mới.
3. Nêu ngắn gọn danh sách file sẽ sửa và lý do.
4. Giữ code dễ đọc, hàm ngắn, tách API với UI khi phù hợp; không over-engineer.
5. API key chỉ từ biến môi trường; tuyệt đối không hardcode hoặc in key ra log.
6. Với API AI, có xử lý timeout/lỗi, tránh gọi lại do Streamlit rerun, tránh gửi trùng lượt.
7. Tạo hoặc sửa test tối thiểu cho logic có thể kiểm thử độc lập. Không khẳng định "đã chạy" nếu chưa thực chạy.
8. Cuối task: nêu file thay đổi, cách chạy, test đã chạy/kết quả, hạn chế còn lại.
9. Cập nhật `TASKS.md` (checkbox) và `PROGRESS.md` khi task được kiểm thử và nghiệm thu, không đánh dấu hoàn thành chỉ vì đã viết code.
10. Không commit database thật, bản ghi âm, transcript có danh tính hoặc các file bí mật.

## Tiêu chí chất lượng
- Ứng dụng khởi động không lỗi.
- Các thay đổi không phá vỡ task đã hoàn thành.
- UI dễ dùng trên máy tính, có thể kiểm thử mobile ở giai đoạn sau.
- Kịch bản theo Unit, không tự bịa rằng nội dung đã được đối chiếu từng trang SGK.
- Feedback cuối buổi dựa trên bằng chứng từ transcript đã xác nhận, không suy diễn lỗi phát âm.

## Mẫu yêu cầu AI
> Thực hiện **Txx** trong `TASKS.md`. Đọc `AGENTS.md` trước. Chỉ sửa các file cần thiết. Đưa ra cách chạy/test và không triển khai task khác. Nếu có lỗi hoặc chưa kiểm thử, nói rõ.
