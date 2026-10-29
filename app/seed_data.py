import sys
import datetime
from sqlalchemy.orm import Session
from app.models import User, JobPosting, Candidate, InterviewRound, CandidateEvaluation, SystemSetting
from app.auth import hash_password

# Đảm bảo console Windows không bị lỗi Unicode
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def init_db_data(db: Session):
    # Kiểm tra xem dữ liệu đã tồn tại chưa
    if db.query(User).first():
        return

    try:
        print(">>> Khoi tao du lieu mau cho he thong tuyen dung...")
    except Exception:
        pass

    # 1. Tạo Users
    admin = User(
        username="admin",
        email="admin@ictu.edu.vn",
        hashed_password=hash_password("admin123"),
        full_name="Nguyễn Văn Quản Trị (Admin)",
        role="admin"
    )
    hr_user = User(
        username="hr_linh",
        email="linh.hr@congty.com",
        hashed_password=hash_password("hr123"),
        full_name="Phạm Phương Linh (HR Lead)",
        role="hr"
    )
    interviewer = User(
        username="tech_lead_nam",
        email="nam.tech@congty.com",
        hashed_password=hash_password("lead123"),
        full_name="Trần Hải Nam (Tech Lead)",
        role="interviewer"
    )
    db.add_all([admin, hr_user, interviewer])
    db.commit()
    db.refresh(admin)
    db.refresh(hr_user)
    db.refresh(interviewer)

    # 2. Tạo Job Postings
    job1 = JobPosting(
        title="Lập trình viên Backend Python (FastAPI / Django)",
        department="Khối Kỹ thuật & R&D",
        location="Hà Nội",
        job_type="Toàn thời gian",
        experience_level="2 - 4 năm",
        salary_range="18 - 30 triệu VNĐ",
        description="Tham gia phát triển hệ thống nền tảng dịch vụ số và microservices phục vụ hàng trăm ngàn người dùng.",
        requirements="• Thành thạo Python, FastAPI hoặc Django.\n• Nắm vững cơ sở dữ liệu PostgreSQL, MySQL, Redis.\n• Có kinh nghiệm làm việc với Docker, Git, CI/CD.\n• Tư duy lập trình tốt, khả năng tự nghiên cứu và giải quyết bài toán phức tạp.",
        benefits="• Thưởng tháng 13 + thưởng hiệu quả dự án.\n• Bảo hiểm sức khỏe PVI cao cấp.\n• Cung cấp laptop MacBook / Dell Pro cấu hình cao.\n• Du lịch hàng năm và 15 ngày phép.",
        status="Đang tuyển",
        deadline="30/11/2026"
    )
    job2 = JobPosting(
        title="Kỹ sư Frontend React (Middle / Senior)",
        department="Khối Kỹ thuật & R&D",
        location="Hà Nội / Hybrid",
        job_type="Toàn thời gian",
        experience_level="1 - 3 năm",
        salary_range="15 - 25 triệu VNĐ",
        description="Xây dựng giao diện web ứng dụng hiện đại, tối ưu trải nghiệm người dùng (UX) và hiệu năng hiển thị.",
        requirements="• Có ít nhất 1.5 năm kinh nghiệm với ReactJS, TypeScript, TailwindCSS.\n• Thành thạo quản lý State (Redux Toolkit hoặc Zustand).\n• Nắm vững kiến trúc REST API và GraphQL.\n• Kỹ năng cắt giao diện chuẩn responsive và cross-browser.",
        benefits="• Cơ chế làm việc Hybrid linh hoạt 2 ngày WFH/tuần.\n• Khóa học kỹ năng và chứng chỉ quốc tế được tài trợ 100%.\n• Team building định kỳ hàng quý.",
        status="Đang tuyển",
        deadline="15/12/2026"
    )
    job3 = JobPosting(
        title="Kỹ sư Trí tuệ Nhân tạo & Dữ liệu (AI / Data Engineer)",
        department="Khối Trí tuệ nhân tạo (AI Lab)",
        location="Hà Nội",
        job_type="Toàn thời gian",
        experience_level="2 - 5 năm",
        salary_range="25 - 45 triệu VNĐ",
        description="Nghiên cứu ứng dụng các mô hình LLM, NLP và Computer Vision vào sản phẩm cốt lõi của công ty.",
        requirements="• Nền tảng toán và giải thuật tốt. Thành thạo Python, PyTorch, Hugging Face, LangChain.\n• Kinh nghiệm triển khai API mô hình AI với FastAPI / vLLM / Triton.\n• Khả năng xử lý dữ liệu lớn với SQL, Pandas, Vector DB (Chroma, Pinecone).\n• Đọc hiểu tài liệu nghiên cứu và paper khoa học.",
        benefits="• Tiếp cận cụm máy chủ GPU đào tạo mô hình mạnh mẽ.\n• Cơ hội công bố báo cáo và tham gia hội thảo quốc tế.\n• Thưởng phát minh và bằng sáng chế công nghệ.",
        status="Đang tuyển",
        deadline="31/12/2026"
    )
    db.add_all([job1, job2, job3])
    db.commit()
    db.refresh(job1)
    db.refresh(job2)
    db.refresh(job3)

    # 3. Tạo Candidates
    c1 = Candidate(
        full_name="Nguyễn Văn An",
        email="an.nguyen@email.com",
        phone="0912345678",
        applied_job_id=job1.id,
        source="TopCV",
        skills="Python, FastAPI, PostgreSQL, Docker, Git, Redis",
        experience_years=2.5,
        status="APPLIED",
        cv_raw_text="""HỌ TÊN: NGUYỄN VĂN AN
Vị trí ứng tuyển: Backend Developer
Tốt nghiệp Đại học Bách Khoa Hà Nội - Chuyên ngành CNTT.
Kinh nghiệm: 2.5 năm lập trình Backend.
Kỹ năng chính: Python, FastAPI, Django, PostgreSQL, Docker, Redis, Unit Testing.
Dự án tiêu biểu:
1. Hệ thống sàn thương mại điện tử: Xây dựng API microservice xử lý đơn hàng bằng FastAPI, tối ưu truy vấn PostgreSQL và Redis caching.
2. Nền tảng quản lý kho vận: Thiết kế cơ sở dữ liệu và triển khai pipeline CI/CD với GitHub Actions và Docker.""",
        notes="Hồ sơ mới nộp qua TopCV, CV trình bày rõ ràng, kỹ năng rất khớp với JD."
    )

    c2 = Candidate(
        full_name="Trần Thị Mai Lan",
        email="lan.tran@email.com",
        phone="0987654321",
        applied_job_id=job2.id,
        source="LinkedIn",
        skills="React, TypeScript, TailwindCSS, Redux Toolkit, Next.js",
        experience_years=2.0,
        status="SCREENING",
        cv_raw_text="""HỌ TÊN: TRẦN THỊ MAI LAN
Chuyên môn: Frontend React Developer
Tốt nghiệp Học viện Công nghệ Bưu chính Viễn thông (PTIT).
Kinh nghiệm: 2 năm phát triển ứng dụng Web Frontend.
Kỹ năng: ReactJS, TypeScript, TailwindCSS, Redux Toolkit, Next.js, HTML5/CSS3.
Dự án:
1. Dashboard quản trị CRM: Xây dựng giao diện responsive bằng React và TailwindCSS, quản lý state phức tạp bằng Redux Toolkit.
2. Web Portal khách hàng: Tối ưu SEO và Core Web Vitals với Next.js.""",
        notes="HR đã sơ loại CV, đánh giá tốt, chuẩn bị gửi lịch phỏng vấn."
    )

    c3 = Candidate(
        full_name="Lê Hoàng Long",
        email="long.le@email.com",
        phone="0901234888",
        applied_job_id=job1.id,
        source="Giới thiệu",
        skills="Python, FastAPI, SQL, Docker, Microservices, Kubernetes",
        experience_years=3.5,
        status="INTERVIEW",
        cv_raw_text="""HỌ TÊN: LÊ HOÀNG LONG
Vị trí ứng tuyển: Senior/Middle Backend Developer
Kinh nghiệm: 3.5 năm tại các công ty Outsourcing và Product.
Kỹ năng: Python, FastAPI, MySQL, PostgreSQL, Docker, Kubernetes, CI/CD, RabbitMQ.
Dự án:
1. FinTech Payment Gateway: Phát triển API xử lý thanh toán tài chính chịu tải 10,000 req/s, đảm bảo tính nhất quán dữ liệu ACID.
2. Hệ thống Notification: Sử dụng Celery và Redis để gửi thông báo push và email tự động.""",
        notes="Đang trong vòng phỏng vấn chuyên môn với Tech Lead."
    )

    c4 = Candidate(
        full_name="Phạm Thu Hà",
        email="ha.pham@email.com",
        phone="0934567890",
        applied_job_id=job3.id,
        source="TopCV",
        skills="Python, Machine Learning, PyTorch, NLP, LangChain, SQL",
        experience_years=3.0,
        status="OFFERED",
        cv_raw_text="""HỌ TÊN: PHẠM THU HÀ
Chuyên môn: AI / Data Engineer
Tốt nghiệp Thạc sĩ Khoa học Dữ liệu - Đại học Công nghệ (ĐHQGHN).
Kinh nghiệm: 3 năm nghiên cứu và ứng dụng AI.
Kỹ năng: Python, PyTorch, Hugging Face, LangChain, RAG, Vector DB, SQL, FastAPI.
Dự án:
1. Trợ lý ảo tư vấn tài chính (RAG Chatbot): Xây dựng hệ thống tìm kiếm ngữ nghĩa với Milvus và mô hình LLM.
2. Phân loại tài liệu tự động: Triển khai mô hình BERT fine-tuning đạt độ chính xác 94%.""",
        notes="Đã hoàn thành xuất sắc 3 vòng phỏng vấn, đã gửi Offer Letter ngày hôm qua."
    )

    c5 = Candidate(
        full_name="Đặng Quốc Bảo",
        email="bao.dang@email.com",
        phone="0977889900",
        applied_job_id=job1.id,
        source="Website",
        skills="Python, FastAPI, PostgreSQL, Docker, AWS",
        experience_years=4.0,
        status="HIRED",
        cv_raw_text="""HỌ TÊN: ĐẶNG QUỐC BẢO
Vị trí: Backend Engineer
Kinh nghiệm: 4 năm phát triển hệ thống Cloud và Backend.
Kỹ năng: Python, FastAPI, Django, AWS, PostgreSQL, Docker, Kafka.
Đã hoàn tất quy trình tuyển dụng và ký hợp đồng lao động chính thức.""",
        notes="Ứng viên đã nhận việc (Onboarding) thành công."
    )

    c6 = Candidate(
        full_name="Vũ Đức Minh",
        email="minh.vu@email.com",
        phone="0966554433",
        applied_job_id=job2.id,
        source="Facebook",
        skills="PHP, WordPress, HTML, CSS",
        experience_years=1.0,
        status="REJECTED",
        cv_raw_text="""HỌ TÊN: VŨ ĐỨC MINH
Vị trí: Web Developer
Kinh nghiệm: 1 năm làm website bằng WordPress và PHP cơ bản.
Chưa có kinh nghiệm với React hoặc TypeScript theo yêu cầu công việc.""",
        notes="Không đáp ứng đủ kỹ năng công nghệ cốt lõi ReactJS. Đã gửi email cảm ơn và từ chối khéo léo."
    )

    db.add_all([c1, c2, c3, c4, c5, c6])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    db.refresh(c3)
    db.refresh(c4)
    db.refresh(c5)
    db.refresh(c6)

    # 4. Tạo Vòng Phỏng Vấn & Lịch Phỏng Vấn
    iv1 = InterviewRound(
        candidate_id=c3.id,
        round_number=2,
        round_name="Vòng 2: Phỏng vấn Chuyên môn Kỹ thuật (Technical)",
        interviewer_id=interviewer.id,
        scheduled_time=datetime.datetime.utcnow() + datetime.timedelta(days=2, hours=3),
        location_or_link="Phòng Họp Kỹ Thuật 401 & Google Meet: meet.google.com/ictu-tech-test",
        notes="Phỏng vấn sâu về thiết kế hệ thống Microservices, tối ưu truy vấn PostgreSQL và xử lý concurrency.",
        result="PENDING"
    )
    iv2 = InterviewRound(
        candidate_id=c4.id,
        round_number=3,
        round_name="Vòng 3: Phỏng vấn Văn hóa & Thỏa thuận Đãi ngộ (HR & Management)",
        interviewer_id=hr_user.id,
        scheduled_time=datetime.datetime.utcnow() - datetime.timedelta(days=3),
        location_or_link="Phòng Hội Thảo Tầng 5",
        notes="Ứng viên giao tiếp xuất sắc, tư duy phù hợp văn hóa công ty, đồng ý mức đãi ngộ.",
        result="PASSED"
    )
    db.add_all([iv1, iv2])
    db.commit()
    db.refresh(iv2)

    # 5. Tạo Đánh Giá Ứng Viên Mẫu
    eval1 = CandidateEvaluation(
        candidate_id=c4.id,
        interview_id=iv2.id,
        evaluator_id=interviewer.id,
        technical_score=9.0,
        soft_skills_score=8.5,
        attitude_score=9.0,
        language_score=8.0,
        total_score=8.6,
        pros="Nắm rất chắc kiến trúc LLM, tư duy giải thuật tốt, chủ động chia sẻ kinh nghiệm xử lý vấn đề thực tế.",
        cons="Kinh nghiệm quản lý nhóm chưa nhiều, phù hợp vai trò Chuyên gia Kỹ thuật (Individual Contributor).",
        recommendation="HIRE",
        notes="Đề xuất tuyển dụng ngay cho dự án AI Lab trọng điểm."
    )
    db.add(eval1)

    # 6. Cấu hình hệ thống ban đầu
    s1 = SystemSetting(key_name="AI_PROVIDER", key_value="auto", description="Nhà cung cấp AI Engine")
    s2 = SystemSetting(key_name="SYSTEM_NOTE", key_value="Hệ thống đã sẵn sàng phục vụ đề tài môn học AIA331.", description="Thông báo hệ thống")
    db.add_all([s1, s2])

    db.commit()
    try:
        print(">>> Du lieu mau da duoc nap thanh cong vao co so du lieu SQLite!")
    except Exception:
        pass
