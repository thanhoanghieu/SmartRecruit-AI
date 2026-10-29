# BÁO CÁO GIAI ĐOẠN KT2: KIẾN TRÚC HỆ THỐNG VÀ THIẾT KẾ CRUD CHO VỊ TRÍ, ỨNG VIÊN, PHỎNG VẤN, ĐÁNH GIÁ

**Học phần:** Ứng dụng Trí tuệ Nhân tạo - AIA331  
**Mã dự án:** 80297  
**Tên đề tài:** Hệ thống quản lý tuyển dụng có tích hợp AI  
**Đơn vị:** Trường Đại học Công nghệ Thông tin và Truyền thông - Đại học Thái Nguyên  

---

## 1. KIẾN TRÚC TỔNG THỂ HỆ THỐNG

Dự án được xây dựng theo kiến trúc phân tầng hiện đại (Layered Architecture):

```
+---------------------------------------------------------------+
|              TẦNG GIAO DIỆN NGƯỜI DÙNG (FRONTEND)             |
|   HTML5 + TailwindCSS + JavaScript ES6 + Chart.js + Icons    |
|  (Cảnh báo Human-in-the-loop, Pipeline Kanban, AI Workbench)  |
+---------------------------------------------------------------+
                               │ (RESTful JSON / Multipart Form)
                               ▼
+---------------------------------------------------------------+
|                TẦNG ĐIỀU HƯỚNG & API (FASTAPI ROUTERS)        |
|  /api/auth  |  /api/jobs  |  /api/candidates  |  /api/interviews |
|  /api/evaluations  |  /api/statistics  |  /api/ai  | /api/settings|
+---------------------------------------------------------------+
            │                                      │
            ▼                                      ▼
+-----------------------+              +------------------------+
| TẦNG NGHIỆP VỤ & CSDL |              |   TẦNG AI ENGINE       |
| SQLAlchemy ORM Models |              | • Google Gemini Flash  |
| SQLite Database       |              | • OpenAI GPT-4o Mini   |
| Pydantic Schemas      |              | • Heuristic NLP Offline|
| Trích xuất PDF / Docx |              | • Anti-Bias Sanitizer  |
+-----------------------+              +------------------------+
```

---

## 2. BẢNG MÔ TẢ CÁC API CRUD CHÍNH

### 2.1. Quản lý Vị trí Tuyển dụng (`/api/jobs`)
| Phương thức | Đường dẫn API | Chức năng | Phân quyền |
|:---:|:---|:---|:---:|
| `GET` | `/api/jobs` | Lấy danh sách các vị trí tuyển dụng kèm số lượng ứng viên | Mọi vai trò |
| `GET` | `/api/jobs/{id}` | Lấy chi tiết thông tin vị trí tuyển dụng | Mọi vai trò |
| `POST` | `/api/jobs` | Đăng tin tuyển dụng mới | Admin, HR |
| `PUT` | `/api/jobs/{id}` | Cập nhật thông tin / trạng thái tuyển dụng | Admin, HR |
| `DELETE` | `/api/jobs/{id}` | Xóa vị trí tuyển dụng | Admin |

### 2.2. Quản lý Hồ sơ Ứng viên (`/api/candidates`)
| Phương thức | Đường dẫn API | Chức năng | Phân quyền |
|:---:|:---|:---|:---:|
| `GET` | `/api/candidates` | Tìm kiếm, lọc ứng viên theo kỹ năng, vị trí, trạng thái | Mọi vai trò |
| `GET` | `/api/candidates/{id}` | Xem chi tiết hồ sơ & nội dung CV trích xuất | Mọi vai trò |
| `POST` | `/api/candidates` | Tạo mới hồ sơ ứng viên (JSON) | Admin, HR |
| `POST` | `/api/candidates/upload` | Tải lên file CV (PDF, DOCX, TXT) và tự động bóc tách | Admin, HR |
| `PATCH` | `/api/candidates/{id}/status` | Cập nhật trạng thái ứng viên (APPLIED -> HIRED) | Admin, HR, Lead |
| `DELETE` | `/api/candidates/{id}` | Xóa hồ sơ ứng viên | Admin, HR |

### 2.3. Lịch Phỏng vấn & Vòng Tuyển dụng (`/api/interviews`)
| Phương thức | Đường dẫn API | Chức năng | Phân quyền |
|:---:|:---|:---|:---:|
| `GET` | `/api/interviews` | Lấy danh sách các buổi phỏng vấn theo lịch trình | Mọi vai trò |
| `POST` | `/api/interviews` | Lên lịch phỏng vấn (tự động đổi trạng thái sang INTERVIEW) | Admin, HR |
| `PUT` | `/api/interviews/{id}` | Cập nhật kết quả phỏng vấn (PASSED / FAILED / PENDING) | Admin, HR, Lead |
| `DELETE` | `/api/interviews/{id}` | Hủy lịch phỏng vấn | Admin, HR |

### 2.4. Đánh giá Ứng viên Theo Tiêu chí (`/api/evaluations`)
| Phương thức | Đường dẫn API | Chức năng | Phân quyền |
|:---:|:---|:---|:---:|
| `GET` | `/api/evaluations` | Xem lịch sử các phiếu đánh giá ứng viên | Mọi vai trò |
| `POST` | `/api/evaluations` | Nhập phiếu đánh giá 4 tiêu chí + khuyến nghị HIRE/REJECT | Admin, HR, Lead |

---

## 3. THỰC THI BẢO MẬT VÀ PHÂN QUYỀN
- Hệ thống áp dụng **JWT (JSON Web Token)** chuẩn bảo mật với thuật toán ký `HS256`.
- Mật khẩu lưu trữ trong cơ sở dữ liệu được băm bằng thuật toán **Bcrypt** an toàn, chống rò rỉ dữ liệu.
- Phân quyền theo vai trò (Role-Based Access Control - RBAC) tại tầng dependency của FastAPI đảm bảo các chức năng can thiệp dữ liệu nhạy cảm chỉ được thực thi bởi người dùng có thẩm quyền.

---
*Báo cáo được hoàn thiện làm tài liệu minh chứng cho bài kiểm tra định kỳ KT2.*
