# ĐÁNH GIÁ ĐẠO ĐỨC AI VÀ KIỂM SOÁT THIÊN LỆCH TRONG TUYỂN DỤNG NHÂN SỰ
## BÁO CÁO CHUYÊN ĐỀ MÔN HỌC AIA331

---

### 1. BỐI CẢNH VẤN ĐỀ ĐẠO ĐỨC AI TRONG TUYỂN DỤNG
Khi áp dụng Trí tuệ Nhân tạo vào lĩnh vực nhân sự (HR Tech), các rủi ro đạo đức lớn nhất thường xuất phát từ:
1. **Thiên kiến trong dữ liệu lịch sử:** Nếu dữ liệu quá khứ có tỷ lệ nam giới hoặc một nhóm nhân khẩu học chiếm đa số, mô hình AI có xu hướng gán điểm cao hơn cho những hồ sơ tương đồng, dẫn đến phân biệt đối xử vô thức.
2. **Ảo giác và suy diễn vô căn cứ:** AI có thể tự gán ghép tính cách hoặc suy đoán tình trạng cá nhân (ví dụ: phụ nữ có con nhỏ sẽ ít cống hiến cho công việc).
3. **Mất khả năng giải trình (Black-box problem):** Ứng viên bị từ chối mà không rõ lý do cụ thể, gây bức xúc và mất uy tín doanh nghiệp.

---

### 2. BỐN NGUYÊN TẮC ĐẠO ĐỨC ĐƯỢC ÁP DỤNG TRONG DỰ ÁN

#### 2.1. Tính Công bằng và Không thiên lệch (Fairness & Non-discrimination)
- Hệ thống thiết lập bộ lọc nhận diện các thuộc tính nhạy cảm: Giới tính, Tuổi tác, Tình trạng hôn nhân, Tôn giáo, Dân tộc và Quê quán.
- Khi phân tích độ phù hợp của CV với vị trí tuyển dụng, hệ thống chỉ tập trung vào:
  - Danh mục kỹ năng công nghệ (Technical Skills).
  - Số năm kinh nghiệm làm việc thực tế.
  - Các dự án và sản phẩm phần mềm đã từng tham gia.
  - Chứng chỉ chuyên môn và học vấn kỹ thuật.

#### 2.2. Quyền con người và Nguyên tắc Human-in-the-loop
- AI chỉ đóng vai trò là một trợ lý ảo hỗ trợ đọc nhanh và tổng hợp thông tin.
- Hệ thống **tuyệt đối không cho phép AI tự động đưa ra quyết định loại bỏ (Reject) hoặc tiếp nhận (Hire) ứng viên**.
- Mọi quyết định thay đổi trạng thái tuyển dụng, gửi thư mời hoặc từ chối đều phải qua thao tác phê duyệt của nhân sự và người phỏng vấn.

#### 2.3. Tính Minh bạch và Giải trình được (Transparency & Explainability)
- Bất kỳ điểm số phù hợp (Match Score) nào do AI đưa ra đều đi kèm 2 danh sách rõ ràng:
  - **Điểm phù hợp:** Nêu rõ các kỹ năng ứng viên có khớp với yêu cầu của JD.
  - **Điểm cần hỏi thêm:** Nêu rõ những kỹ năng hoặc kinh nghiệm chưa rõ ràng cần làm rõ trong buổi phỏng vấn.
- Toàn bộ Prompt và phản hồi đều được ghi nhận trong bảng lịch sử `ai_summary_logs` để phục vụ việc kiểm toán khi cần.

#### 2.4. Bảo vệ Dữ liệu và Quyền riêng tư (Privacy & Data Protection)
- Thông tin liên lạc cá nhân (Email, Số điện thoại) được bảo vệ, mật khẩu người dùng được băm an toàn bằng Bcrypt.
- Hệ thống hỗ trợ chế độ Heuristic NLP chạy offline hoàn toàn trên máy cục bộ, không gửi dữ liệu hồ sơ cá nhân của ứng viên ra ngoài Internet nếu doanh nghiệp yêu cầu bảo mật nội bộ nghiêm ngặt.

---
*Tài liệu thuộc hồ sơ nghiệm thu đồ án học phần AIA331.*
