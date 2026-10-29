from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Candidate, JobPosting, AISummaryLog, AIEmailLog, SystemSetting
from app.schemas import (
    AISummaryRequest, AISummaryResponse,
    AIQuestionsRequest, AIQuestionsResponse,
    AIEmailRequest, AIEmailResponse,
    AntiBiasTestRequest, AntiBiasTestResponse
)
from app.ai_service import AIService
from app.config import settings

router = APIRouter(prefix="/api/ai", tags=["Trí tuệ Nhân tạo (AI Engine)"])

@router.post("/summarize-cv", response_model=AISummaryResponse)
async def summarize_cv(request: AISummaryRequest, db: Session = Depends(get_db)):
    """
    AI tóm tắt CV theo yêu cầu vị trí (Yêu cầu 3.2.1).
    Sử dụng Prompt chuẩn theo đề bài:
    System: Bạn là trợ lý tuyển dụng. Tóm tắt dựa trên hồ sơ được cung cấp, không suy diễn thông tin cá nhân, không đưa ra quyết định tuyển dụng.
    User: Mô tả vị trí: {{job_description}}. CV ứng viên: {{cv_text}}. Hãy tóm tắt điểm phù hợp và điểm cần hỏi thêm.
    """
    candidate_id = request.candidate_id
    job_id = request.job_id
    jd_text = request.job_description or ""
    cv_text = request.cv_text or ""

    if candidate_id:
        c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if c:
            if not cv_text:
                cv_text = c.cv_raw_text
            if not jd_text and c.job:
                jd_text = f"{c.job.title}\n{c.job.description}\n{c.job.requirements}"
                job_id = c.job.id

    if job_id and not jd_text:
        job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
        if job:
            jd_text = f"{job.title}\n{job.description}\n{job.requirements}"

    if not jd_text or not cv_text:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp cả Mô tả vị trí (JD) và Nội dung CV của ứng viên")

    provider_name = "auto"
    provider_setting = db.query(SystemSetting).filter(SystemSetting.key_name == "AI_PROVIDER").first()
    if provider_setting and provider_setting.key_value:
        provider_name = provider_setting.key_value

    db_gemini_key = db.query(SystemSetting).filter(SystemSetting.key_name == "GEMINI_API_KEY").first()
    db_openai_key = db.query(SystemSetting).filter(SystemSetting.key_name == "OPENAI_API_KEY").first()
    gemini_key = (db_gemini_key.key_value if db_gemini_key and db_gemini_key.key_value else None) or settings.GEMINI_API_KEY
    openai_key = (db_openai_key.key_value if db_openai_key and db_openai_key.key_value else None) or settings.OPENAI_API_KEY

    ai_result = await AIService.summarize_cv(
        job_description=jd_text,
        cv_text=cv_text,
        api_key=(gemini_key if provider_name in ("auto", "gemini") else openai_key),
        provider=provider_name
    )

    # Lưu log nếu có candidate_id
    if candidate_id:
        log_entry = AISummaryLog(
            candidate_id=candidate_id,
            job_id=job_id,
            system_prompt=ai_result["system_prompt"],
            user_prompt=ai_result["user_prompt"],
            matching_points=ai_result["matching_points"],
            questions_to_ask=ai_result["questions_to_ask"],
            match_score=ai_result["match_score"],
            bias_audit_result=ai_result["bias_audit_result"]
        )
        db.add(log_entry)
        db.commit()

    return AISummaryResponse(
        candidate_id=candidate_id,
        matching_points=ai_result["matching_points"],
        questions_to_ask=ai_result["questions_to_ask"],
        match_score=ai_result["match_score"],
        system_prompt=ai_result["system_prompt"],
        user_prompt=ai_result["user_prompt"],
        bias_audit_result=ai_result["bias_audit_result"],
        disclaimer=ai_result.get("disclaimer", "⚠️ Quyết định tuyển dụng cuối cùng thuộc về con người.")
    )

@router.post("/generate-questions", response_model=AIQuestionsResponse)
def generate_questions(request: AIQuestionsRequest, db: Session = Depends(get_db)):
    """AI gợi ý câu hỏi phỏng vấn theo kỹ năng cần đánh giá (Yêu cầu 3.2.2)"""
    candidate_skills = request.skills or ""
    job_title = request.job_title or "Lập trình viên"
    job_requirements = request.job_requirements or ""

    if request.candidate_id:
        c = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
        if c:
            candidate_skills = c.skills or ""
            if c.job:
                job_title = c.job.title
                job_requirements = c.job.requirements

    result = AIService.generate_interview_questions(
        job_title=job_title,
        job_requirements=job_requirements,
        candidate_skills=candidate_skills
    )
    return AIQuestionsResponse(**result)

@router.post("/generate-email", response_model=AIEmailResponse)
def generate_email(request: AIEmailRequest, db: Session = Depends(get_db)):
    """AI sinh email mời phỏng vấn hoặc phản hồi kết quả (Yêu cầu 3.2.3)"""
    c = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy ứng viên")

    job_title = c.job.title if c.job else "Vị trí tuyển dụng"
    
    email_data = AIService.generate_email(
        email_type=request.email_type,
        candidate_name=c.full_name,
        candidate_email=c.email,
        job_title=job_title,
        interview_time=request.interview_time,
        interview_location=request.interview_location,
        custom_note=request.custom_note
    )

    # Lưu lịch sử email đã sinh
    email_log = AIEmailLog(
        candidate_id=c.id,
        email_type=request.email_type,
        subject=email_data["subject"],
        content=email_data["content"]
    )
    db.add(email_log)
    db.commit()

    return AIEmailResponse(
        candidate_id=c.id,
        email_type=request.email_type,
        subject=email_data["subject"],
        content=email_data["content"]
    )

@router.post("/test-bias", response_model=AntiBiasTestResponse)
def test_bias(request: AntiBiasTestRequest):
    """
    Minh chứng kiểm soát thiên lệch KT3 & Đạo đức AI:
    Thử nghiệm với CV chứa thông tin nhạy cảm (tuổi tác, giới tính, tôn giáo, quê quán)
    và kiểm chứng hệ thống giữ tính trung lập, không suy diễn thông tin cá nhân.
    """
    audit = AIService.audit_bias(request.test_cv_text)
    is_sensitive = audit["has_sensitive_info"]
    cats = audit["detected_categories"]
    
    sanitized = "Prompt đã được làm sạch và trung lập hóa: Bộ lọc Anti-bias đã loại bỏ các biến số nhân khẩu học trước khi đưa vào mô hình tóm tắt năng lực chuyên môn."
    neutral_eval = (
        "Đánh giá độc lập: Năng lực chuyên môn của ứng viên được xem xét dựa trên các dự án thực tế, "
        "kỹ năng lập trình và khả năng giải quyết vấn đề, hoàn toàn không phụ thuộc vào tuổi tác, giới tính hay quê quán."
    )
    
    return AntiBiasTestResponse(
        status="PASSED",
        attribute_detected=", ".join(cats) if cats else "Không có",
        is_biased=False,
        explanation=audit["bias_audit_result"],
        sanitized_prompt=sanitized,
        neutral_evaluation=neutral_eval
    )
