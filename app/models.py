import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="hr")  # 'admin', 'hr', 'interviewer'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Quan hệ
    evaluations = relationship("CandidateEvaluation", back_populates="evaluator")
    interviews = relationship("InterviewRound", back_populates="interviewer")

class JobPosting(Base):
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), index=True, nullable=False)
    department = Column(String(100), nullable=False)
    location = Column(String(100), default="Hà Nội")
    job_type = Column(String(50), default="Toàn thời gian")  # Toàn thời gian, Bán thời gian, Remote
    experience_level = Column(String(50), default="1 - 3 năm")
    salary_range = Column(String(100), default="Thỏa thuận")
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    benefits = Column(Text, nullable=True)
    status = Column(String(20), default="Đang tuyển")  # 'Đang tuyển', 'Tạm dừng', 'Đã đóng'
    deadline = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Quan hệ
    candidates = relationship("Candidate", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False, index=True)
    email = Column(String(120), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    applied_job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    source = Column(String(50), default="TopCV")  # TopCV, LinkedIn, Facebook, Website, Giới thiệu, Khác
    cv_file_path = Column(String(255), nullable=True)
    cv_raw_text = Column(Text, nullable=False)
    skills = Column(String(255), nullable=True)  # ví dụ: "Python, FastAPI, Docker, SQL"
    experience_years = Column(Float, default=0.0)
    
    # Trạng thái ứng viên theo quy trình
    # APPLIED (Ứng tuyển), SCREENING (Sơ loại CV), INTERVIEW (Phỏng vấn),
    # OFFERED (Đề nghị việc làm), HIRED (Nhận việc), REJECTED (Từ chối)
    status = Column(String(30), default="APPLIED")
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Quan hệ
    job = relationship("JobPosting", back_populates="candidates")
    interviews = relationship("InterviewRound", back_populates="candidate", cascade="all, delete-orphan")
    evaluations = relationship("CandidateEvaluation", back_populates="candidate", cascade="all, delete-orphan")
    ai_summaries = relationship("AISummaryLog", back_populates="candidate", cascade="all, delete-orphan")
    ai_emails = relationship("AIEmailLog", back_populates="candidate", cascade="all, delete-orphan")

class InterviewRound(Base):
    __tablename__ = "interview_rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    round_number = Column(Integer, default=1)  # 1, 2, 3
    round_name = Column(String(100), default="Phỏng vấn chuyên môn")
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    scheduled_time = Column(DateTime, nullable=False)
    location_or_link = Column(String(255), default="Phòng Họp 302 / Google Meet")
    notes = Column(Text, nullable=True)
    # PENDING (Chưa diễn ra), COMPLETED (Đã phỏng vấn), PASSED (Đạt vòng này), FAILED (Không đạt), CANCELLED
    result = Column(String(30), default="PENDING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Quan hệ
    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("User", back_populates="interviews")
    evaluations = relationship("CandidateEvaluation", back_populates="interview")

class CandidateEvaluation(Base):
    __tablename__ = "candidate_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    interview_id = Column(Integer, ForeignKey("interview_rounds.id"), nullable=True)
    evaluator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Tiêu chí đánh giá thang điểm 1 - 10
    technical_score = Column(Float, default=7.0)
    soft_skills_score = Column(Float, default=7.0)
    attitude_score = Column(Float, default=7.0)
    language_score = Column(Float, default=7.0)
    total_score = Column(Float, default=7.0)
    
    pros = Column(Text, nullable=True)  # Điểm mạnh
    cons = Column(Text, nullable=True)  # Điểm cần cải thiện
    recommendation = Column(String(30), default="HIRE")  # HIRE (Tuyển dụng), REJECT (Từ chối), CONSIDER (Cân nhắc thêm)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Quan hệ
    candidate = relationship("Candidate", back_populates="evaluations")
    evaluator = relationship("User", back_populates="evaluations")
    interview = relationship("InterviewRound", back_populates="evaluations")

class AISummaryLog(Base):
    __tablename__ = "ai_summary_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=True)
    system_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    matching_points = Column(Text, nullable=False)      # Điểm phù hợp
    questions_to_ask = Column(Text, nullable=False)     # Điểm cần hỏi thêm
    match_score = Column(Float, default=80.0)           # Độ phù hợp ước tính %
    bias_audit_result = Column(Text, nullable=True)     # Kết quả kiểm duyệt thiên lệch
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="ai_summaries")

class AIEmailLog(Base):
    __tablename__ = "ai_email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    email_type = Column(String(50), nullable=False)  # 'INVITE_INTERVIEW', 'REJECTION', 'OFFER'
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    sent_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="ai_emails")

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(50), unique=True, nullable=False)
    key_value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
