# TASKS.md – Lộ trình chia task SpeakUp AI

**Quy ước:** `[ ]` chưa bắt đầu; `[~]` đang làm (dùng trong PROGRESS); `[x]` chỉ sau khi đã chạy/kiểm thử và nghiệm thu.

## Phase 0 – Khởi tạo
- [x] **T00** Cài môi trường, khởi chạy `streamlit run app.py`, kiểm tra `.gitignore`, tạo commit đầu.
- [x] **T01** Trang Home hiển thị và chọn Unit 1 từ JSON.

## Phase 1 – Xử lý âm thanh độc lập
- [x] **T02** Thu âm bằng `st.audio_input()`, phát lại, kiểm tra dữ liệu rỗng.
- [x] **T03** Gọi Speech-to-Text, hiển thị transcript, cơ chế xác nhận/ghi lại.
- [x] **T04** Gọi Text-to-Speech và phát tiếng AI.
- [x] **T05** AI Teacher (LLM) tạo câu hỏi theo giới hạn Unit 1.

## Phase 2 – Hội thoại hoàn chỉnh
- [x] **T06** Quản lý `session_state`, `session_id`, `turn_id`, số lượt và lịch sử.
- [ ] **T07** Ghép STT → LLM → TTS, hiển thị phụ đề, không sửa lỗi giữa buổi. **Done khi:** hội thoại 5 lượt Unit 1 chạy được.

## Phase 3 – Feedback cuối buổi
- [ ] **T08** Tổng hợp feedback cuối buổi theo schema rõ ràng, có lỗi và ví dụ sửa, không suy diễn pronunciation.

## Phase 4 – Lưu trữ và tiến độ
- [ ] **T09** Tạo schema SQLite (students, sessions, turns, feedback, progress), init DB.
- [ ] **T10** Lưu phiên và feedback, truy xuất lại sau restart.
- [ ] **T11** My Progress: số buổi, Unit, tần suất lỗi, biểu đồ.

## Phase 5 – Cá nhân hóa
- [ ] **T12** Quy tắc đề xuất nội dung dựa trên lịch sử.

## Phase 6 – Mở rộng và chuẩn bị thi STEM
- [ ] **T13** Bổ sung, kiểm duyệt nội dung 12 Unit sách Global Success 8.
- [ ] **T14** Kiểm thử tích hợp desktop/mobile, micro, mạng yếu, API lỗi.
- [ ] **T15** Hoàn thiện tài liệu kiến trúc, poster, kịch bản demo.

## Mốc nghiệm thu
- **MVP A:** T00–T07 – Hội thoại Unit 1 thật.
- **MVP B:** T08–T11 – Feedback và lưu tiến độ.
- **MVP C:** T12–T15 – Cá nhân hóa và sản phẩm STEM.
