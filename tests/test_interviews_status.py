import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import JobPosting, Candidate, InterviewRound, CandidateEvaluation, User
from app.auth import hash_password

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()

    user = User(username="lead", email="lead@ictu.edu.vn", hashed_password=hash_password("123"), full_name="Tech Lead", role="interviewer")
    job = JobPosting(title="Backend Dev", department="Tech", description="JD", requirements="Req")
    session.add_all([user, job])
    session.commit()

    candidate = Candidate(full_name="Lê Văn Phỏng Vấn", email="pv@test.com", phone="09", applied_job_id=job.id, cv_raw_text="CV", status="APPLIED")
    session.add(candidate)
    session.commit()

    yield session
    session.close()

def test_interview_schedule_and_candidate_status_transition(db):
    candidate = db.query(Candidate).first()
    user = db.query(User).first()

    # Tạo lịch phỏng vấn vòng 1
    round1 = InterviewRound(
        candidate_id=candidate.id,
        round_number=1,
        round_name="Vòng 1: Lọc hồ sơ",
        interviewer_id=user.id,
        scheduled_time=datetime.datetime.now(datetime.UTC),
        result="PASSED"
    )
    db.add(round1)
    # Chuyển trạng thái sang INTERVIEW
    candidate.status = "INTERVIEW"
    db.commit()

    assert round1.id is not None
    assert candidate.status == "INTERVIEW"

    # Tạo đánh giá sau phỏng vấn với khuyến nghị HIRE
    eval_record = CandidateEvaluation(
        candidate_id=candidate.id,
        interview_id=round1.id,
        evaluator_id=user.id,
        technical_score=9.0,
        soft_skills_score=8.5,
        attitude_score=9.0,
        language_score=8.0,
        total_score=8.7,
        recommendation="HIRE"
    )
    db.add(eval_record)
    candidate.status = "OFFERED"
    db.commit()

    assert eval_record.total_score == 8.7
    assert candidate.status == "OFFERED"
