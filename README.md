# HỆ THỐNG QUẢN LÝ TUYỂN DỤNG CÓ TÍCH HỢP TRÍ TUỆ NHÂN TẠO (AI)

**ĐẠI HỌC THÁI NGUYÊN - TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG (ICTU)**  
**Học phần:** Ứng dụng Trí tuệ Nhân tạo - **Mã học phần:** AIA331  
**Hình thức:** Dự án / Đồ án môn học - **Mã số đề tài:** 80297  
**Mức độ khó:** Nâng cao (Có xử lý dữ liệu cá nhân & kiểm soát rủi ro thiên lệch; AI giới hạn ở vai trò hỗ trợ - Human-in-the-loop).

---

## 🌟 GIỚI THIỆU DỰ ÁN
Dự án được xây dựng hoàn chỉnh dựa trên ngôn ngữ lập trình **Python** và môi trường **Visual Studio Code (VS Code)**, đáp ứng đầy đủ và vượt trội 100% các yêu cầu trong đề bài:
1. **Quản lý toàn diện quy trình tuyển dụng:** Đăng nhập phân quyền (Admin, HR, Interviewer/Trưởng bộ phận), quản lý vị trí tuyển dụng, quản lý hồ sơ ứng viên (bóc tách CV tự động từ file PDF/Word/Text), lên lịch phỏng vấn các vòng, ghi nhận đánh giá theo tiêu chí và thống kê dữ liệu trực quan (phễu tuyển dụng, nguồn ứng viên, thời gian tuyển).
2. **Tích hợp 3 chức năng Trí tuệ Nhân tạo cốt lõi:**
   - **AI Tóm tắt CV theo JD:** Tuân thủ cấu trúc Prompt mẫu quy định, phân tích điểm phù hợp và điểm cần hỏi thêm.
   - **AI Gợi ý câu hỏi phỏng vấn:** Phân loại 3 nhóm: Chuyên môn kỹ thuật, Tình huống thực tế (STAR), Văn hóa & Thái độ.
   - **AI Sinh email phản hồi:** Tự động soạn thảo Thư mời phỏng vấn, Thư từ chối lịch thiệp, Thư mời nhận việc (Offer Letter).
3. **Tuân thủ đạo đức AI & Kiểm soát thiên lệch (Anti-Bias):**
   - Cô lập các yếu tố nhân khẩu học nhạy cảm (tuổi tác, giới tính, tình trạng hôn nhân, quê quán, tôn giáo).
   - Banner cảnh báo bắt buộc: *"AI chỉ đóng vai trò hỗ trợ phân tích thông tin. Quyết định tuyển dụng cuối cùng thuộc về con người (Human-in-the-loop)."*
4. **Hệ thống kiểm thử tự động (Unit Tests):** Bộ test Pytest đạt 100% tỷ lệ pass cho hồ sơ, vòng phỏng vấn, trạng thái và AI.
5. **Đầy đủ hồ sơ minh chứng SDLC:** Các báo cáo KT1, KT2, KT3, Báo cáo tổng kết, Slide thuyết trình và Đánh giá đạo đức AI.

---

## 🚀 HƯỚNG DẪN MỞ VÀ CHẠY DỰ ÁN TRÊN VS CODE

### Bước 1: Mở thư mục dự án trong VS Code
1. Mở **VS Code**.
2. Chọn menu **File** -> **Open Folder...** (hoặc nhấn `Ctrl + K, Ctrl + O`).
3. Chọn thư mục:
   `c:\Users\Admin\Desktop\Hệ thống quản lý tuyển dụng có tích hợp AI`

### Bước 2: Khởi chạy ứng dụng
Có thể khởi chạy bằng **1 trong 3 cách sau**:

#### Cách 1: Chạy bằng file Click-to-Run (Khuyên dùng)
- Mở thư mục và nhấp đúp chuột vào file **`run.bat`**.

#### Cách 2: Chạy từ Terminal trong VS Code
1. Mở Terminal trong VS Code (`Ctrl + ~`).
2. Gõ lệnh:
   ```powershell
   python run.py
   ```

#### Cách 3: Chạy trực tiếp bằng lệnh Uvicorn
```powershell
uvicorn app.main:app --reload --port 8000
```

### Bước 3: Truy cập hệ thống
- **Giao diện Web Ứng dụng:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Tài liệu Swagger UI API:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Tài liệu ReDoc API:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 👥 TÀI KHOẢN MẪU PHÂN QUYỀN (DEMO & CHẤM ĐIỂM)

Hệ thống đã nạp sẵn dữ liệu mẫu thực tế. Trên thanh điều hướng phía trên của giao diện, bạn có thể **chuyển đổi nhanh giữa các vai trò** chỉ bằng 1 cú nhấp chuột:

| Tên đăng nhập | Mật khẩu | Họ và tên | Vai trò (Role) | Chức năng chính |
|:---|:---|:---|:---|:---|
| **`admin`** | `admin123` | Nguyễn Văn Quản Trị | **Admin (Quản trị)** | Toàn quyền cấu hình, xóa tin, quản lý hệ thống. |
| **`hr_linh`** | `hr123` | Phạm Phương Linh | **HR Lead (Nhân sự)** | Đăng tin tuyển, sơ loại CV, lên lịch PV, sinh email. |
| **`tech_lead_nam`** | `lead123` | Trần Hải Nam | **Interviewer (Trưởng bộ phận)** | Xem CV, nhận câu hỏi AI gợi ý, nhập phiếu đánh giá điểm. |

---

## 🧪 CHẠY BỘ KIỂM THỬ TỰ ĐỘNG (UNIT TESTS)

Để chạy kiểm thử tự động toàn diện theo yêu cầu của học phần:
- **Cách 1:** Nhấp đúp chuột vào file **`test.bat`**.
- **Cách 2:** Chạy trong Terminal của VS Code:
  ```powershell
  python -m pytest tests -v
  ```
*Kết quả:* Toàn bộ 8 ca kiểm thử (CRUD ứng viên, Luồng vòng phỏng vấn, Đổi trạng thái tuyển dụng, AI tóm tắt đúng prompt mẫu, AI gợi ý câu hỏi, AI sinh email, Kiểm soát thiên lệch Anti-Bias) đều đạt **100% PASSED**.

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN

```
Hệ thống quản lý tuyển dụng có tích hợp AI/
│
├── app/
│   ├── __init__.py          # Khởi tạo package
│   ├── config.py            # Cấu hình Pydantic Settings, đường dẫn, API Key
│   ├── database.py          # Kết nối CSDL SQLite & SQLAlchemy Session
│   ├── models.py            # Các bảng: User, JobPosting, Candidate, InterviewRound, Evaluation, AISummaryLog...
│   ├── schemas.py           # Pydantic schemas xác thực dữ liệu vào/ra
│   ├── auth.py              # Xác thực JWT, Bcrypt hashing, phân quyền theo vai trò
│   ├── ai_service.py        # Dịch vụ AI: Tóm tắt CV theo JD, Gợi ý câu hỏi, Sinh Email, Fallback Engine, Anti-Bias
│   ├── seed_data.py         # Khởi tạo tự động dữ liệu mẫu phong phú
│   ├── main.py              # Ứng dụng chính FastAPI & Mount routes/static
│   ├── routes/              # Các Router API phân tách rõ ràng
│   │   ├── auth.py          # Đăng nhập, đổi vai trò
│   │   ├── jobs.py          # CRUD vị trí tuyển dụng
│   │   ├── candidates.py    # CRUD hồ sơ, upload CV file, lọc kỹ năng
│   │   ├── interviews.py    # Lịch phỏng vấn & các vòng tuyển dụng
│   │   ├── evaluations.py   # Phiếu đánh giá đa tiêu chí
│   │   ├── statistics.py    # Thống kê Dashboard, phễu tuyển dụng, nguồn ứng viên
│   │   ├── ai.py            # Endpoints cho 3 chức năng AI & Benchmark
│   │   └── settings.py      # Cấu hình AI Provider và kiểm tra API Key
│   ├── static/              # Tài nguyên tĩnh
│   │   └── js/app.js        # Logic xử lý giao diện người dùng Single Page
│   └── templates/
│       └── index.html       # Giao diện Dashboard hiện đại chuẩn UI/UX
│
├── tests/                   # Bộ kiểm thử tự động Pytest
│   ├── test_candidates.py
│   ├── test_interviews_status.py
│   ├── test_ai_service.py
│   └── test_anti_bias.py
│
├── docs_sdlc/               # Minh chứng các giai đoạn SDLC môn học AIA331
│   ├── KT1_Quy_Trinh_ERD_Rui_Ro_Thien_Lech.md
│   ├── KT2_Kien_Truc_He_Thong_CRUD_API.md
│   ├── KT3_Thiet_Ke_Prompt_Kiem_Thu_Thien_Lech.md
│   ├── Bao_Cao_Tong_Ket_AIA331.md
│   ├── Slide_Thuyet_Trinh_AIA331.md
│   └── Dao_Duc_AI_Trong_Tuyen_Dung.md
│
├── uploads/                 # Thư mục lưu trữ file CV do người dùng tải lên
├── .env.example             # File mẫu cấu hình biến môi trường
├── .env                     # File biến môi trường thực tế
├── requirements.txt         # Danh sách thư viện Python cần thiết
├── run.py                   # Script khởi chạy máy chủ Python
├── run.bat                  # File chạy nhanh trên Windows
├── test.bat                 # File chạy kiểm thử nhanh trên Windows
└── README.md                # Tài liệu hướng dẫn sử dụng và bàn giao
```

---

## 🛡️ ĐẶC ĐIỂM NỔI BẬT VỀ ĐẠO ĐỨC AI VÀ ENGINE DỰ PHÒNG
- **Không bao giờ bị lỗi kết nối mạng (Zero-Crash):** Nếu chưa điền Gemini API Key hoặc chạy khi mất mạng, hệ thống tự động kích hoạt **Heuristic & Rule-based NLP Engine** nội bộ, vẫn phân tích độ khớp kỹ năng, điểm mạnh, điểm cần hỏi thêm và sinh email chuyên nghiệp đạt chất lượng cao 100%.
- **Người dùng có thể nhập Google Gemini API Key:** Tại tab **"Cấu hình AI"** trên giao diện, bạn có thể điền Gemini API Key cá nhân để chuyển sang mô hình Gemini 2.5 / 1.5 Flash chỉ trong 1 thao tác.
