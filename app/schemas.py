import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: str = "hr"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Job Schemas
class JobBase(BaseModel):
    title: str
    department: str
    location: str = "Hà Nội"
    job_type: str = "Toàn thời gian"
    experience_level: str = "1 - 3 năm"
    salary_range: str = "Thỏa thuận"
    description: str
    requirements: str
    benefits: Optional[str] = None
    status: str = "Đang tuyển"
    deadline: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[str] = None

class JobResponse(JobBase):
    id: int
    created_at: datetime.datetime
    candidate_count: Optional[int] = 0
    class Config:
        from_attributes = True

# Candidate Schemas
class CandidateBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    applied_job_id: int
    source: str = "TopCV"
    skills: Optional[str] = None
    experience_years: float = 0.0
    status: str = "APPLIED"
    notes: Optional[str] = None

class CandidateCreate(CandidateBase):
    cv_raw_text: str

class CandidateUpdateStatus(BaseModel):
    status: str
    notes: Optional[str] = None

class CandidateResponse(CandidateBase):
    id: int
    cv_file_path: Optional[str] = None
    cv_raw_text: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    job_title: Optional[str] = None
    class Config:
        from_attributes = True

# Interview Schemas
class InterviewBase(BaseModel):
    candidate_id: int
    round_number: int = 1
    round_name: str = "Phỏng vấn chuyên môn"
    interviewer_id: Optional[int] = None
    scheduled_time: datetime.datetime
    location_or_link: str = "Phòng Họp 302 / Google Meet"
    notes: Optional[str] = None
    result: str = "PENDING"

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(BaseModel):
    scheduled_time: Optional[datetime.datetime] = None
    location_or_link: Optional[str] = None
    notes: Optional[str] = None
    result: Optional[str] = None
    interviewer_id: Optional[int] = None

class InterviewResponse(InterviewBase):
    id: int
    created_at: datetime.datetime
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
    interviewer_name: Optional[str] = None
    class Config:
        from_attributes = True

# Evaluation Schemas
class EvaluationBase(BaseModel):
    candidate_id: int
    interview_id: Optional[int] = None
    technical_score: float = Field(ge=1.0, le=10.0, default=7.0)
    soft_skills_score: float = Field(ge=1.0, le=10.0, default=7.0)
    attitude_score: float = Field(ge=1.0, le=10.0, default=7.0)
    language_score: float = Field(ge=1.0, le=10.0, default=7.0)
    pros: Optional[str] = None
    cons: Optional[str] = None
    recommendation: str = "HIRE"
    notes: Optional[str] = None

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationResponse(EvaluationBase):
    id: int
    evaluator_id: int
    evaluator_name: Optional[str] = None
    total_score: float
    created_at: datetime.datetime
    candidate_name: Optional[str] = None
    class Config:
        from_attributes = True

# AI Request & Response Schemas
class AISummaryRequest(BaseModel):
    candidate_id: Optional[int] = None
    job_id: Optional[int] = None
    job_description: Optional[str] = None
    cv_text: Optional[str] = None

class AISummaryResponse(BaseModel):
    candidate_id: Optional[int] = None
    matching_points: str
    questions_to_ask: str
    match_score: float
    system_prompt: str
    user_prompt: str
    bias_audit_result: str
    disclaimer: str = "⚠️ CẢNH BÁO: AI chỉ đóng vai trò hỗ trợ phân tích thông tin. Quyết định tuyển dụng cuối cùng thuộc về con người (Human-in-the-loop)."

class AIQuestionsRequest(BaseModel):
    candidate_id: Optional[int] = None
    job_id: Optional[int] = None
    skills: Optional[str] = None
    job_title: Optional[str] = None
    job_requirements: Optional[str] = None

class AIQuestionsResponse(BaseModel):
    technical_questions: List[str]
    situational_questions: List[str]
    culture_fit_questions: List[str]
    disclaimer: str = "⚠️ AI chỉ hỗ trợ gợi ý câu hỏi phỏng vấn theo kỹ năng cần đánh giá."

class AIEmailRequest(BaseModel):
    candidate_id: int
    email_type: str  # 'INVITE_INTERVIEW', 'REJECTION', 'OFFER'
    interview_time: Optional[str] = None
    interview_location: Optional[str] = None
    custom_note: Optional[str] = None

class AIEmailResponse(BaseModel):
    candidate_id: int
    email_type: str
    subject: str
    content: str
    disclaimer: str = "⚠️ Email được sinh bởi AI - Vui lòng kiểm tra và chỉnh sửa trước khi gửi cho ứng viên."

class AntiBiasTestRequest(BaseModel):
    test_cv_text: str
    attribute_to_test: str = "demographics"  # 'gender', 'age', 'marital_status', 'ethnicity_location', 'demographics'

class AntiBiasTestResponse(BaseModel):
    status: str
    attribute_detected: str
    is_biased: bool
    explanation: str
    sanitized_prompt: str
    neutral_evaluation: str
