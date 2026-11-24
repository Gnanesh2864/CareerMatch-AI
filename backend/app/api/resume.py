import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.schemas.candidate import CandidateProfileSchema, ResumeParseResponse
from app.resume.parser import extract_text_from_file
from app.resume.extractor import CandidateExtractor
from app.embeddings.embedder import embedding_service
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/resume", tags=["Resume & Candidate Intelligence"])

@router.post("/upload", response_model=ResumeParseResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    raw_text = extract_text_from_file(contents, file.filename or "resume.pdf")

    # Extract structured candidate schema
    structured_profile = CandidateExtractor.extract_profile(raw_text)

    # Compute dense vector embedding for matching
    skills_str = ", ".join([s.name for s in structured_profile.skills])
    embed_repr = (
        f"{structured_profile.full_name}. {structured_profile.experience_level} engineer. "
        f"Skills: {skills_str}. Summary: {structured_profile.summary}."
    )
    vector_embed = embedding_service.embed_text(embed_repr)

    # Persist or update CandidateProfile row
    prof = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not prof:
        prof = CandidateProfile(
            user_id=current_user.id,
            raw_resume_text=raw_text,
            resume_filename=file.filename,
            structured_data_json=structured_profile.model_dump_json(),
            embedding_json=json.dumps(vector_embed),
        )
        db.add(prof)
    else:
        prof.raw_resume_text = raw_text
        prof.resume_filename = file.filename
        prof.structured_data_json = structured_profile.model_dump_json()
        prof.embedding_json = json.dumps(vector_embed)

    db.commit()

    return ResumeParseResponse(
        success=True,
        structured_profile=structured_profile,
        raw_text_preview=raw_text[:500] + "...",
        message="Resume successfully processed and extracted."
    )

@router.get("/profile", response_model=CandidateProfileSchema)
def get_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prof = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not prof or not prof.structured_data_json:
        # Return empty default profile
        return CandidateProfileSchema(full_name=current_user.full_name, email=current_user.email)
    return CandidateProfileSchema.model_validate_json(prof.structured_data_json)

@router.put("/profile", response_model=CandidateProfileSchema)
def update_candidate_profile(
    updated: CandidateProfileSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skills_str = ", ".join([s.name for s in updated.skills])
    embed_repr = (
        f"{updated.full_name}. {updated.experience_level} engineer. "
        f"Skills: {skills_str}. Summary: {updated.summary}."
    )
    vector_embed = embedding_service.embed_text(embed_repr)

    prof = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not prof:
        prof = CandidateProfile(
            user_id=current_user.id,
            raw_resume_text="",
            resume_filename="manual_entry",
            structured_data_json=updated.model_dump_json(),
            embedding_json=json.dumps(vector_embed),
        )
        db.add(prof)
    else:
        prof.structured_data_json = updated.model_dump_json()
        prof.embedding_json = json.dumps(vector_embed)

    db.commit()
    return updated
