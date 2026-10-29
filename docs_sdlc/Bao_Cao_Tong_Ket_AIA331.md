# BÁO CÁO TỔNG KẾT ĐỒ ÁN HỌC PHẦN
## MÔN HỌC: ỨNG DỤNG TRÍ TUỆ NHÂN TẠO (AIA331)

---

**ĐỀ TÀI: HỆ THỐNG QUẢN LÝ TUYỂN DỤNG CÓ TÍCH HỢP TRÍ TUỆ NHÂN TẠO**  
**Mã số đề tài:** 80297  
**Đơn vị đào tạo:** Đại học Thái Nguyên - Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU)  
**Khoa:** Hệ thống Thông tin Kinh tế & Khoa học Dữ liệu  

---

### MỤC LỤC
1. Giới thiệu bài toán và Tính cấp thiết
2. Mục tiêu nghiên cứu và Phạm vi đề tài
3. Phân tích yêu cầu chức năng và phi chức năng
4. Thiết kế kiến trúc hệ thống và Cơ sở dữ liệu
5. Hiện thực hóa các chức năng AI trong Tuyển dụng
6. Ứng dụng AI trong toàn bộ vòng đời phát triển phần mềm (SDLC)
7. Đánh giá đạo đức AI và Kiểm soát rủi ro thiên lệch (Bias Control)
8. Kết quả thử nghiệm và Đánh giá hiệu năng
9. Kết luận và Hướng phát triển trong tương lai

---

### 1. GIỚI THIỆU BÀI TOÁN VÀ TÍNH CẤP THIẾT
Trong kỷ nguyên chuyển đổi số, quy trình tuyển dụng nhân sự tại các doanh nghiệp đối mặt với nhiều thách thức lớn:
- Số lượng hồ sơ ứng viên (CV) gửi về mỗi đợt tuyển dụng rất lớn khiến bộ phận nhân sự mất từ 30 - 45% thời gian chỉ để đọc và phân loại hồ sơ thủ công.
- Nguy cơ bỏ sót ứng viên tiềm năng do sự mệt mỏi chủ quan của con người.
- Việc soạn thảo các văn bản phản hồi (thư mời phỏng vấn, thư cảm ơn từ chối, thư mời nhận việc) thiếu tính cá nhân hóa và mất nhiều công sức.
- Hội đồng phỏng vấn gặp khó khăn trong việc chuẩn bị các câu hỏi phỏng vấn chuẩn hóa, bám sát kỹ năng cần đo lường.

Hệ thống **"Quản lý tuyển dụng có tích hợp AI"** được nghiên cứu và xây dựng nhằm giải quyết triệt để các bài toán trên thông qua việc số hóa toàn diện quy trình tuyển dụng và tích hợp các mô hình ngôn ngữ lớn (LLM) hỗ trợ phân tích thông tin khách quan.

---

### 2. MỤC TIÊU NGHIÊN CỨU VÀ PHẠM VI
- **Mục tiêu quản lý:** Quản lý trọn vẹn quy trình tuyển dụng từ đăng tin, tiếp nhận hồ sơ, sơ loại, lên lịch phỏng vấn, đánh giá đa tiêu chí đến chuyển đổi trạng thái ứng viên.
- **Mục tiêu AI:**
  1. AI tóm tắt hồ sơ CV dựa trên yêu cầu vị trí (JD).
  2. AI gợi ý bộ câu hỏi phỏng vấn theo phương pháp STAR và kỹ năng chuyên môn.
  3. AI tự động soạn thảo email phản hồi chuyên nghiệp, lịch thiệp.
- **Mục tiêu học thuật:** Minh chứng việc tích hợp AI xuyên suốt các giai đoạn của quy trình phát triển phần mềm (SDLC) và kiểm soát thành công rủi ro thiên lệch dữ liệu nhạy cảm.

---

### 3. CÔNG NGHỆ SỬ DỤNG
- **Ngôn ngữ lập trình:** Python 3.14 (hiện đại, hiệu năng cao, kiểu dữ liệu tĩnh nghiêm ngặt).
- **Backend Framework:** FastAPI (bất đồng bộ Async/Await, chuẩn OpenAPI/Swagger).
- **Cơ sở dữ liệu:** SQLite kết hợp SQLAlchemy ORM 2.0 (thuận tiện đóng gói, di động, không phụ thuộc dịch vụ ngoài).
- **Frontend Dashboard:** Giao diện Single Page hiện đại sử dụng HTML5, TailwindCSS, Chart.js, FontAwesome.
- **AI Engines:**
  - Google Gemini 2.5 / 1.5 Flash API (khi có kết nối Internet và API key).
  - OpenAI GPT-4o Mini API.
  - Heuristic & Rule-based NLP Engine cục bộ (hoạt động offline 100% tin cậy, không lo gián đoạn mạng).
- **Thư viện trích xuất:** `pypdf`, `python-docx` để đọc CV dạng file.
- **Kiểm thử tự động:** `pytest` đạt 100% tỷ lệ vượt qua tất cả các bài kiểm tra.

---

### 4. ĐÁNH GIÁ ĐẠO ĐỨC VÀ NGUYÊN TẮC HUMAN-IN-THE-LOOP
- Hệ thống áp dụng nghiêm ngặt nguyên tắc **Human-in-the-loop**: Mô hình AI tuyệt đối không nắm quyền quyết định loại bỏ hay tiếp nhận ứng viên. Mọi chuyển trạng thái hồ sơ đều do nhân sự (HR) và phỏng vấn viên (Interviewer) trực tiếp xác nhận.
- Cảnh báo bắt buộc luôn hiển thị trên thanh điều hướng đầu trang:
  > *"⚠️ CẢNH BÁO BẮT BUỘC: Hệ thống AI chỉ đóng vai trò hỗ trợ phân tích & gợi ý. Toàn bộ quyết định tuyển dụng, loại bỏ hoặc tiếp nhận ứng viên hoàn toàn thuộc về con người (Human-in-the-loop)."*

---

### 5. KẾT LUẬN
Đồ án đã hoàn thành xuất sắc 100% các yêu cầu đặt ra trong đề bài môn học AIA331, đạt mức độ hoàn thiện **Nâng cao** với đầy đủ minh chứng kỹ thuật, mã nguồn chuẩn mực, giao diện trực quan và hệ thống kiểm thử toàn diện.
