from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InterviewRound, Candidate, User
from app.schemas import InterviewCreate, InterviewUpdate, InterviewResponse
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/interviews", tags=["Lịch Phỏng Vấn & Vòng Tuyển Dụng"])

@router.get("", response_model=List[InterviewResponse])
def get_interviews(
    candidate_id: Optional[int] = None,
    result_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(InterviewRound)
    if candidate_id:
        query = query.filter(InterviewRound.candidate_id == candidate_id)
    if result_filter:
        query = query.filter(InterviewRound.result == result_filter)
        
    rounds = query.order_by(InterviewRound.scheduled_time.desc()).all()
    results = []
    for r in rounds:
        item = InterviewResponse.model_validate(r)
        if r.candidate:
            item.candidate_name = r.candidate.full_name
            if r.candidate.job:
                item.job_title = r.candidate.job.title
        if r.interviewer:
            item.interviewer_name = r.interviewer.full_name
        results.append(item)
    return results

@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview(
    interview_in: InterviewCreate,
    current_user: User = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == interview_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Không tìm thấy ứng viên tương ứng")
        
    iv = InterviewRound(**interview_in.model_dump())
    db.add(iv)
    
    # Cập nhật trạng thái ứng viên sang INTERVIEW nếu đang ở APPLIED hoặc SCREENING
    if candidate.status in ["APPLIED", "SCREENING"]:
        candidate.status = "INTERVIEW"
        
    db.commit()
    db.refresh(iv)
    
    item = InterviewResponse.model_validate(iv)
    item.candidate_name = candidate.full_name
    if candidate.job:
        item.job_title = candidate.job.title
    if iv.interviewer:
        item.interviewer_name = iv.interviewer.full_name
    return item

@router.put("/{interview_id}", response_model=InterviewResponse)
def update_interview(
    interview_id: int,
    interview_update: InterviewUpdate,
    current_user: User = Depends(require_roles(["admin", "hr", "interviewer"])),
    db: Session = Depends(get_db)
):
    iv = db.query(InterviewRound).filter(InterviewRound.id == interview_id).first()
    if not iv:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch phỏng vấn này")
        
    update_data = interview_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(iv, key, value)
        
    db.commit()
    db.refresh(iv)
    
    item = InterviewResponse.model_validate(iv)
    if iv.candidate:
        item.candidate_name = iv.candidate.full_name
        if iv.candidate.job:
            item.job_title = iv.candidate.job.title
    if iv.interviewer:
        item.interviewer_name = iv.interviewer.full_name
    return item

@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(
    interview_id: int,
    current_user: User = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    iv = db.query(InterviewRound).filter(InterviewRound.id == interview_id).first()
    if not iv:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch phỏng vấn này")
    db.delete(iv)
    db.commit()
    return None
