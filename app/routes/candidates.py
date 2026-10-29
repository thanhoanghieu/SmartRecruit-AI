import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pypdf import PdfReader
from docx import Document

from app.database import get_db
from app.models import Candidate, JobPosting, User
from app.schemas import CandidateCreate, CandidateResponse, CandidateUpdateStatus
from app.auth import get_current_user, require_roles
from app.config import settings

router = APIRouter(prefix="/api/candidates", tags=["Hồ sơ Ứng viên"])

def extract_text_from_file(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    try:
        if ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        elif ext in [".docx", ".doc"]:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
    except Exception as e:
        text = f"Không thể trích xuất văn bản từ file ({str(e)}). Vui lòng dán nội dung thủ công."
    return text.strip()

@router.get("", response_model=List[CandidateResponse])
def get_candidates(
    job_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skill: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Candidate)
    
    if job_id:
        query = query.filter(Candidate.applied_job_id == job_id)
    if status_filter:
        query = query.filter(Candidate.status == status_filter)
    if skill:
        query = query.filter(Candidate.skills.ilike(f"%{skill}%"))
    if search:
        query = query.filter(
            (Candidate.full_name.ilike(f"%{search}%")) |
            (Candidate.email.ilike(f"%{search}%")) |
            (Candidate.skills.ilike(f"%{search}%"))
        )
        
    candidates = query.order_by(Candidate.id.desc()).all()
    results = []
    for c in candidates:
        res = CandidateResponse.model_validate(c)
        if c.job:
            res.job_title = c.job.title
        results.append(res)
    return results

@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy ứng viên này")
    res = CandidateResponse.model_validate(c)
    if c.job:
        res.job_title = c.job.title
    return res

@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate_in: CandidateCreate,
    current_user: User = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    job = db.query(JobPosting).filter(JobPosting.id == candidate_in.applied_job_id).first()
    if not job:
        raise HTTPException(status_code=400, detail="Vị trí tuyển dụng không hợp lệ")
        
    c = Candidate(**candidate_in.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    
    res = CandidateResponse.model_validate(c)
    res.job_title = job.title
    return res

@router.post("/upload", response_model=CandidateResponse)
async def upload_candidate_cv(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    applied_job_id: int = Form(...),
    source: str = Form("TopCV"),
    skills: Optional[str] = Form(None),
    experience_years: float = Form(0.0),
    file: Optional[UploadFile] = File(None),
    cv_raw_text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    job = db.query(JobPosting).filter(JobPosting.id == applied_job_id).first()
    if not job:
        raise HTTPException(status_code=400, detail="Vị trí tuyển dụng không tồn tại")

    saved_file_path = None
    extracted_text = cv_raw_text or ""
    
    if file and file.filename:
        filename = f"{email}_{file.filename}"
        dest_path = settings.UPLOAD_DIR / filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_file_path = str(dest_path)
        
        extracted = extract_text_from_file(saved_file_path, file.filename)
        if extracted:
            extracted_text = extracted

    if not extracted_text:
        extracted_text = f"Ứng viên {full_name} ứng tuyển vị trí {job.title}. Kỹ năng khai báo: {skills}."

    c = Candidate(
        full_name=full_name,
        email=email,
        phone=phone,
        applied_job_id=applied_job_id,
        source=source,
        skills=skills,
        experience_years=experience_years,
        cv_file_path=saved_file_path,
        cv_raw_text=extracted_text,
        status="APPLIED"
    )
    db.add(c)
    db.commit()
    db.refresh(c)

    res = CandidateResponse.model_validate(c)
    res.job_title = job.title
    return res

@router.patch("/{candidate_id}/status", response_model=CandidateResponse)
def update_candidate_status(
    candidate_id: int,
    status_update: CandidateUpdateStatus,
    current_user: User = Depends(require_roles(["admin", "hr", "interviewer"])),
    db: Session = Depends(get_db)
):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy ứng viên này")
        
    c.status = status_update.status
    if status_update.notes:
        c.notes = status_update.notes
    db.commit()
    db.refresh(c)
    
    res = CandidateResponse.model_validate(c)
    if c.job:
        res.job_title = c.job.title
    return res

@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    candidate_id: int,
    current_user: User = Depends(require_roles(["admin", "hr"])),
    db: Session = Depends(get_db)
):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy ứng viên này")
    db.delete(c)
    db.commit()
    return None
