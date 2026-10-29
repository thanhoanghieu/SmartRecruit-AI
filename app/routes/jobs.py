from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import JobPosting, Candidate, User
from app.schemas import JobCreate, JobUpdate, JobResponse
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/jobs", tags=["Vị trí Tuyển dụng"])

@router.get("", response_model=List[JobResponse])
def get_jobs(
    department: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(JobPosting)
    if department:
        query = query.filter(JobPosting.department == department)
    if status_filter:
        query = query.filter(JobPosting.status == status_filter)
        
    jobs = query.order_by(JobPosting.id.desc()).all()
    results = []
    for job in jobs:
        c_count = db.query(Candidate).filter(Candidate.applied_job_id == job.id).count()
        job_data = JobResponse.model_validate(job)
        job_data.candidate_count = c_count
        results.append(job_data)
    return results

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy vị trí tuyển dụng này")
    c_count = db.query(Candidate).filter(Candidate.applied_job_id == job.id).count()
    job_data = JobResponse.model_validate(job)
    job_data.candidate_count = c_count
    return job_data

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    job = JobPosting(**job_in.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    job_data = JobResponse.model_validate(job)
    job_data.candidate_count = 0
    return job_data

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: User = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy vị trí tuyển dụng này")
    
    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)
        
    db.commit()
    db.refresh(job)
    c_count = db.query(Candidate).filter(Candidate.applied_job_id == job.id).count()
    job_data = JobResponse.model_validate(job)
    job_data.candidate_count = c_count
    return job_data

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy vị trí tuyển dụng này")
    db.delete(job)
    db.commit()
    return None
