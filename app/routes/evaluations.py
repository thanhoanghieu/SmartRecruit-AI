from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CandidateEvaluation, Candidate, User, InterviewRound
from app.schemas import EvaluationCreate, EvaluationResponse
from app.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/evaluations", tags=["Đánh giá Phỏng vấn"])

@router.get("", response_model=List[EvaluationResponse])
def get_evaluations(
    candidate_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CandidateEvaluation)
    if candidate_id:
        query = query.filter(CandidateEvaluation.candidate_id == candidate_id)
        
    evals = query.order_by(CandidateEvaluation.created_at.desc()).all()
    results = []
    for e in evals:
        item = EvaluationResponse.model_validate(e)
        if e.candidate:
            item.candidate_name = e.candidate.full_name
        if e.evaluator:
            item.evaluator_name = e.evaluator.full_name
        results.append(item)
    return results

@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    eval_in: EvaluationCreate,
    current_user: User = Depends(require_roles(["admin", "hr", "interviewer"])),
    db: Session = Depends(get_db)
):
    candidate = db.query(Candidate).filter(Candidate.id == eval_in.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Không tìm thấy ứng viên tương ứng")
        
    # Tính điểm trung bình cộng có trọng số
    total = round(
        (eval_in.technical_score * 0.4) +
        (eval_in.soft_skills_score * 0.25) +
        (eval_in.attitude_score * 0.25) +
        (eval_in.language_score * 0.1),
        2
    )
    
    evaluation = CandidateEvaluation(
        candidate_id=eval_in.candidate_id,
        interview_id=eval_in.interview_id,
        evaluator_id=current_user.id,
        technical_score=eval_in.technical_score,
        soft_skills_score=eval_in.soft_skills_score,
        attitude_score=eval_in.attitude_score,
        language_score=eval_in.language_score,
        total_score=total,
        pros=eval_in.pros,
        cons=eval_in.cons,
        recommendation=eval_in.recommendation,
        notes=eval_in.notes
    )
    db.add(evaluation)
    
    # Cập nhật kết quả phỏng vấn tương ứng nếu có
    if eval_in.interview_id:
        iv = db.query(InterviewRound).filter(InterviewRound.id == eval_in.interview_id).first()
        if iv:
            iv.result = "PASSED" if eval_in.recommendation == "HIRE" else ("FAILED" if eval_in.recommendation == "REJECT" else "COMPLETED")
            
    # Hỗ trợ cập nhật trạng thái ứng viên
    if eval_in.recommendation == "HIRE" and candidate.status == "INTERVIEW":
        candidate.status = "OFFERED"
    elif eval_in.recommendation == "REJECT" and candidate.status == "INTERVIEW":
        candidate.status = "REJECTED"
        
    db.commit()
    db.refresh(evaluation)
    
    item = EvaluationResponse.model_validate(evaluation)
    item.candidate_name = candidate.full_name
    item.evaluator_name = current_user.full_name
    return item
