import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import JobPosting, Candidate

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Tạo Job mẫu
    job = JobPosting(
        title="Python Backend Developer",
        department="Engineering",
        description="Lập trình FastAPI",
        requirements="Python, FastAPI, SQL"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    yield db
    db.close()

def test_create_candidate(db_session):
    job = db_session.query(JobPosting).first()
    candidate = Candidate(
        full_name="Nguyễn Văn Test",
        email="test@ictu.edu.vn",
        phone="0912345678",
        applied_job_id=job.id,
        skills="Python, FastAPI, Docker",
        experience_years=2.0,
        cv_raw_text="2 năm kinh nghiệm lập trình Python và FastAPI.",
        status="APPLIED"
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)

    assert candidate.id is not None
    assert candidate.full_name == "Nguyễn Văn Test"
    assert candidate.status == "APPLIED"

def test_query_and_filter_candidates(db_session):
    job = db_session.query(JobPosting).first()
    c1 = Candidate(full_name="Ứng viên A", email="a@test.com", phone="01", applied_job_id=job.id, skills="Python", cv_raw_text="CV A", status="APPLIED")
    c2 = Candidate(full_name="Ứng viên B", email="b@test.com", phone="02", applied_job_id=job.id, skills="React", cv_raw_text="CV B", status="SCREENING")
    db_session.add_all([c1, c2])
    db_session.commit()

    python_candidates = db_session.query(Candidate).filter(Candidate.skills.contains("Python")).all()
    assert len(python_candidates) == 1
    assert python_candidates[0].full_name == "Ứng viên A"

    screening_candidates = db_session.query(Candidate).filter(Candidate.status == "SCREENING").all()
    assert len(screening_candidates) == 1
    assert screening_candidates[0].full_name == "Ứng viên B"
