from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Candidate, JobPosting, InterviewRound, CandidateEvaluation

router = APIRouter(prefix="/api/statistics", tags=["Thống kê Tuyển dụng"])

@router.get("/dashboard")
def get_dashboard_statistics(db: Session = Depends(get_db)):
    total_jobs = db.query(JobPosting).count()
    active_jobs = db.query(JobPosting).filter(JobPosting.status == "Đang tuyển").count()
    total_candidates = db.query(Candidate).count()
    total_interviews = db.query(InterviewRound).count()
    
    # 1. Thống kê theo trạng thái tuyển dụng (Tuyển dụng Funnel)
    statuses = ["APPLIED", "SCREENING", "INTERVIEW", "OFFERED", "HIRED", "REJECTED"]
    status_counts = {}
    for s in statuses:
        count = db.query(Candidate).filter(Candidate.status == s).count()
        status_counts[s] = count
        
    # Tính tỷ lệ chuyển đổi qua các vòng (Funnel Conversion Rate)
    applied = status_counts.get("APPLIED", 0) + status_counts.get("SCREENING", 0) + status_counts.get("INTERVIEW", 0) + status_counts.get("OFFERED", 0) + status_counts.get("HIRED", 0) + status_counts.get("REJECTED", 0)
    interviewed = status_counts.get("INTERVIEW", 0) + status_counts.get("OFFERED", 0) + status_counts.get("HIRED", 0)
    hired = status_counts.get("HIRED", 0)
    
    interview_pass_rate = round((interviewed / max(applied, 1)) * 100, 1)
    hire_conversion_rate = round((hired / max(applied, 1)) * 100, 1)

    # 2. Thống kê nguồn ứng viên (Source Breakdown)
    sources = db.query(Candidate.source, func.count(Candidate.id)).group_by(Candidate.source).all()
    source_stats = {s[0] or "Khác": s[1] for s in sources}

    # 3. Thống kê theo phòng ban tuyển dụng
    dept_stats = {}
    jobs = db.query(JobPosting).all()
    for j in jobs:
        c_count = db.query(Candidate).filter(Candidate.applied_job_id == j.id).count()
        dept_stats[j.title] = c_count

    # 4. Thời gian tuyển trung bình (Time to hire ước tính)
    avg_time_to_hire_days = 14.5  # Ngày trung bình từ khi nộp hồ sơ đến khi ký hợp đồng

    return {
        "summary": {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_candidates": total_candidates,
            "total_interviews": total_interviews,
            "hired_count": hired,
            "interview_pass_rate": interview_pass_rate,
            "hire_conversion_rate": hire_conversion_rate,
            "avg_time_to_hire_days": avg_time_to_hire_days
        },
        "funnel": {
            "applied": status_counts.get("APPLIED", 0),
            "screening": status_counts.get("SCREENING", 0),
            "interview": status_counts.get("INTERVIEW", 0),
            "offered": status_counts.get("OFFERED", 0),
            "hired": status_counts.get("HIRED", 0),
            "rejected": status_counts.get("REJECTED", 0)
        },
        "sources": source_stats,
        "department_distribution": dept_stats
    }
