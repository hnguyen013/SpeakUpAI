# TASKS.md – Lộ trình chia task SpeakUp AI

**Quy ước:** `[ ]` chưa bắt đầu; `[~]` đang làm (dùng trong PROGRESS); `[x]` chỉ sau khi đã chạy/kiểm thử và nghiệm thu. Mỗi issue/PR tương ứng **một task**. Các task chưa hoàn thành được giữ `[ ]` ở đây.

## Phase 0 – Khởi tạo
- [x] **T00** Cài môi trường, khởi chạy `streamlit run app.py`, kiểm tra `.gitignore`, tạo commit đầu. **Done khi:** chạy Home mẫu trên máy.
- [x] **T01** Trang Home hiển thị và chọn Unit 1 từ JSON. **Done khi:** chọn Unit, lưu lựa chọn trong `st.session_state`.

## Phase 1 – Xử lý âm thanh độc lập
- [ ] **T02** Thu âm bằng `st.audio_input()`, phát lại, kiểm tra dữ liệu rỗng. **Done khi:** record/playback trên máy thật.
- [ ] **T03** Gọi Speech-to-Text, hiển thị transcript, cơ chế xác nhận/ghi lại. **Done khi:** xử lý được tiếng Anh thực tế, có lỗi mạng và mock mode.
- [ ] **T04** Gọi Text-to-Speech và phát tiếng AI. **Done khi:** phát lại được, có bắt lỗi và mock mode.
- [ ] **T05** AI Teacher (LLM) tạo câu hỏi theo giới hạn Unit 1. **Done khi:** test bằng văn bản, không phụ thuộc micro.

## Phase 2 – Hội thoại hoàn chỉnh
- [ ] **T06** Quản lý `session_state`, `session_id`, `turn_id`, số lượt và lịch sử. **Done khi:** Streamlit rerun không mất phiên/không trùng request.
- [ ] **T07** Ghép STT → LLM → TTS, hiển thị phụ đề, không sửa lỗi giữa buổi. **Done khi:** hội thoại 5 lượt Unit 1 chạy được.

## Phase 3 – Feedback cuối buổi
- [ ] **T08** Tổng hợp feedback cuối buổi theo schema rõ ràng, có lỗi và ví dụ sửa, không suy diễn pronunciation. **Done khi:** test với transcript đúng/sai/nhận dạng không chắc chắn.

## Phase 4 – Lưu trữ và tiến độ
- [ ] **T09** Tạo schema SQLite (students, sessions, turns, feedback, progress), init DB. **Done khi:** test CRUD với dữ liệu giả.
- [ ] **T10** Lưu phiên và feedback, truy xuất lại sau restart. **Done khi:** không mất dữ liệu, không lưu audio mặc định.
- [ ] **T11** My Progress: số buổi, Unit, tần suất lỗi, biểu đồ. **Done khi:** biểu đồ đọc dữ liệu từ DB, có trạng thái chưa có dữ liệu.

## Phase 5 – Cá nhân hóa
- [ ] **T12** Quy tắc đề xuất nội dung dựa trên lịch sử; có giải thích lý do và test biên. **Done khi:** cùng dữ liệu cho cùng đề xuất, không dùng số lỗi thô làm chỉ số duy nhất.

## Phase 6 – Mở rộng và chuẩn bị thi STEM
- [ ] **T13** Bổ sung, kiểm duyệt nội dung 12 Unit sách Global Success 8. **Done khi:** các Unit có mục tiêu, vốn từ, tình huống; giáo viên rà soát.
- [ ] **T14** Kiểm thử tích hợp trên desktop/mobile, micro, mạng yếu, API lỗi và quyền dữ liệu. **Done khi:** ghi lại kết quả thực tế.
- [ ] **T15** Hoàn thiện tài liệu kiến trúc, poster, kịch bản demo, báo cáo thử nghiệm. **Done khi:** nhóm học sinh có thể giải thích rõ phần tự làm.

## Mốc nghiệm thu
- **MVP A:** T00–T07 – Hội thoại Unit 1 thật.
- **MVP B:** T08–T11 – Feedback và lưu tiến độ.
- **MVP C:** T12–T15 – Cá nhân hóa và sản phẩm STEM.
