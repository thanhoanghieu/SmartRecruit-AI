# KỊCH BẢN & SLIDE THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN HỌC PHẦN AIA331

**Đề tài:** Hệ thống Quản lý Tuyển dụng có Tích hợp AI  
**Mã dự án:** 80297  
**Đơn vị:** Đại học Thái Nguyên - Trường ĐH Công nghệ Thông tin và Truyền thông  

---

## SLIDE 1: TRANG TIÊU ĐỀ
- **Tên đề tài:** HỆ THỐNG QUẢN LÝ TUYỂN DỤNG CÓ TÍCH HỢP TRÍ TUỆ NHÂN TẠO
- **Học phần:** Ứng dụng Trí tuệ Nhân tạo - Mã số: AIA331
- **Mã dự án:** 80297
- **Người thực hiện:** Sinh viên thực hiện đề tài
- **Giảng viên hướng dẫn:** Giảng viên phụ trách học phần

---

## SLIDE 2: BỐI CẢNH VÀ TÍNH CẤP THIẾT
- Khối lượng hồ sơ ứng viên lớn: Mất 40% thời gian xử lý thủ công.
- Rủi ro bỏ sót nhân tài do áp lực thời gian của chuyên viên nhân sự.
- Khó khăn trong việc soạn thảo email phản hồi cá nhân hóa và thiết kế câu hỏi phỏng vấn chuẩn hóa.
- **Giải pháp:** Xây dựng phần mềm quản lý tuyển dụng khép kín có trợ lực từ các mô hình AI tiên tiến.

---

## SLIDE 3: KIẾN TRÚC KỸ THUẬT CỦA HỆ THỐNG
- **Backend:** FastAPI (Python 3.14) - Kiến trúc bất đồng bộ tốc độ cao.
- **CSDL:** SQLite & SQLAlchemy ORM - Gọn nhẹ, di động, không phụ thuộc máy chủ CSDL phức tạp.
- **Giao diện:** Modern Single Page Dashboard (HTML5, TailwindCSS, Chart.js).
- **AI Engine:** Cơ chế lai (Hybrid) - Google Gemini Flash / OpenAI / Heuristic NLP Offline Engine.

---

## SLIDE 4: BA CHỨC NĂNG AI CỐT LÕI (MỤC 3.2 ĐỀ BÀI)
1. **AI Tóm Tắt CV Theo JD:**
   - Phân tích điểm phù hợp và điểm cần hỏi thêm.
   - Tuân thủ cấu trúc Prompt mẫu chuẩn trung lập, cấm suy diễn thông tin cá nhân.
2. **AI Gợi Ý Câu Hỏi Phỏng Vấn:**
   - Phân loại 3 nhóm: Chuyên môn kỹ thuật, Tình huống thực tế (STAR), Văn hóa & Thái độ.
3. **AI Soạn Thảo Email Tuyển Dụng:**
   - Tự động sinh thư mời phỏng vấn, thư từ chối lịch thiệp, thư mời nhận việc (Offer Letter).

---

## SLIDE 5: MINH CHỨNG SDLC & KIỂM SOÁT THIÊN LỆCH (ANTI-BIAS)
- **KT1:** Phân tích quy trình nghiệp vụ, Actor, ERD và Ma trận rủi ro thiên lệch.
- **KT2:** Sinh kiến trúc CRUD vị trí, ứng viên, lịch phỏng vấn và đánh giá.
- **KT3:** Thiết kế Prompt trung lập, kiểm thử dữ liệu nhạy cảm (tuổi, giới tính, quê quán).
- **Cuối kỳ:** Báo cáo toàn diện, slide bảo vệ, tài liệu đạo đức AI và mã nguồn có kiểm thử 100% tự động.

---

## SLIDE 6: NGUYÊN TẮC ĐẠO ĐỨC & HUMAN-IN-THE-LOOP
- Luôn hiển thị thông điệp cảnh báo rõ ràng.
- Quyền quyết định cuối cùng 100% thuộc về con người.
- Không để AI tự động loại bỏ ứng viên (No ghost rejection).

---

## SLIDE 7: DEMO HỆ THỐNG TRỰC TIẾP
- Trình diễn chuyển đổi 3 vai trò (Admin, HR, Tech Lead).
- Đăng tuyển vị trí -> Thêm hồ sơ ứng viên -> AI tóm tắt CV -> Lên lịch phỏng vấn -> Đánh giá ứng viên -> Thống kê Dashboard.

---

## SLIDE 8: KẾT LUẬN & HỎI ĐÁP (Q&A)
- Hoàn thành đầy đủ các tiêu chí mức độ Nâng cao của đề bài.
- Xin trân trọng cảm ơn Thầy/Cô trong Hội đồng chấm thi!
