import asyncio
import pytest
from app.ai_service import AIService

def test_ai_cv_summary_rubric_format():
    jd = "Cần tuyển Lập trình viên Python FastAPI, kinh nghiệm Docker, PostgreSQL."
    cv = "Họ tên: Nguyễn Văn An. 3 năm kinh nghiệm lập trình backend với Python, FastAPI, Docker và cơ sở dữ liệu PostgreSQL."

    result = asyncio.run(AIService.summarize_cv(job_description=jd, cv_text=cv, provider="auto"))

    # Kiểm tra các trường đầu ra bắt buộc theo đề bài
    assert "matching_points" in result
    assert "questions_to_ask" in result
    assert "match_score" in result
    assert result["match_score"] >= 50.0

    # Kiểm tra tuân thủ đúng prompt mẫu
    assert "Bạn là trợ lý tuyển dụng" in result["system_prompt"]
    assert "không suy diễn thông tin cá nhân" in result["system_prompt"]
    assert "Mô tả vị trí:" in result["user_prompt"]
    assert "CV ứng viên:" in result["user_prompt"]

    # Kiểm tra disclaimer bắt buộc
    assert "Human-in-the-loop" in result["disclaimer"]

def test_ai_generate_interview_questions():
    questions = AIService.generate_interview_questions(
        job_title="Backend Developer",
        job_requirements="Python, FastAPI, SQL",
        candidate_skills="Python, FastAPI, Docker"
    )

    assert "technical_questions" in questions
    assert "situational_questions" in questions
    assert "culture_fit_questions" in questions
    assert len(questions["technical_questions"]) > 0
    assert len(questions["situational_questions"]) > 0
    assert len(questions["culture_fit_questions"]) > 0

def test_ai_generate_email():
    invite_email = AIService.generate_email(
        email_type="INVITE_INTERVIEW",
        candidate_name="Nguyễn Văn An",
        candidate_email="an@email.com",
        job_title="Backend Developer",
        interview_time="09:00 AM Thứ Hai",
        interview_location="Google Meet"
    )
    assert "Thư Mời Tham Dự Phỏng Vấn" in invite_email["subject"]
    assert "Nguyễn Văn An" in invite_email["content"]
    assert "Google Meet" in invite_email["content"]

    rejection_email = AIService.generate_email(
        email_type="REJECTION",
        candidate_name="Trần Thị B",
        candidate_email="b@email.com",
        job_title="Frontend Developer"
    )
    assert "Thông Báo Kết Quả" in rejection_email["subject"]
    assert "Trần Thị B" in rejection_email["content"]

    offer_email = AIService.generate_email(
        email_type="OFFER",
        candidate_name="Lê Văn C",
        candidate_email="c@email.com",
        job_title="AI Engineer"
    )
    assert "JOB OFFER" in offer_email["subject"]
    assert "Lê Văn C" in offer_email["content"]
