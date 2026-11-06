import json
import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)

from sqlalchemy.orm import Session

from app.config import settings

from app.db.database import get_db

from app.models.candidate import Candidate
from app.models.job import Job

from app.services.document_parser import (
    parse_document
)

from app.agents.profile_agent import (
    extract_candidate_profile,
    extract_job_profile
)

from app.services.alignment_engine import (
    calculate_alignment
)


router = APIRouter()


os.makedirs(
    settings.UPLOAD_DIR,
    exist_ok=True
)


@router.post(
    "/screen"
)
async def screen_candidate(
    resume: UploadFile = File(...),
    jd: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required."
        )

    if not jd.filename:
        raise HTTPException(
            status_code=400,
            detail="Job description file is required."
        )

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".md"
    }

    resume_ext = os.path.splitext(
        resume.filename
    )[1].lower()

    jd_ext = os.path.splitext(
        jd.filename
    )[1].lower()

    if resume_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported resume format."
        )

    if jd_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported JD format."
        )

    file_id = str(
        uuid.uuid4()
    )

    resume_path = os.path.join(
        settings.UPLOAD_DIR,
        f"{file_id}_resume{resume_ext}"
    )

    jd_path = os.path.join(
        settings.UPLOAD_DIR,
        f"{file_id}_jd{jd_ext}"
    )

    with open(
        resume_path,
        "wb"
    ) as file:

        file.write(
            await resume.read()
        )

    with open(
        jd_path,
        "wb"
    ) as file:

        file.write(
            await jd.read()
        )

    try:

        resume_text = parse_document(
            resume_path
        )

        jd_text = parse_document(
            jd_path
        )

        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract resume text."
            )

        if not jd_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract JD text."
            )

        candidate_profile = (
            extract_candidate_profile(
                resume_text
            )
        )

        job_profile = (
            extract_job_profile(
                jd_text
            )
        )

        alignment = calculate_alignment(
            candidate_profile,
            job_profile
        )

        eligible = (
            alignment[
                "weighted_alignment"
            ]
            >= settings.ALIGNMENT_THRESHOLD
            and not alignment[
                "critical_skills_missing"
            ]
        )

        candidate = Candidate(
            name=candidate_profile.name,
            resume_filename=resume.filename,
            resume_text=resume_text,
            profile_json=json.dumps(
                candidate_profile.model_dump()
            )
        )

        db.add(candidate)

        db.flush()

        job = Job(
            title=job_profile.title,
            jd_filename=jd.filename,
            jd_text=jd_text,
            profile_json=json.dumps(
                job_profile.model_dump()
            )
        )

        db.add(job)

        db.commit()

        db.refresh(candidate)
        db.refresh(job)

        return {

            "candidate_id": candidate.id,

            "job_id": job.id,

            "candidate_profile":
                candidate_profile.model_dump(),

            "job_profile":
                job_profile.model_dump(),

            "alignment":
                alignment,

            "alignment_threshold":
                settings.ALIGNMENT_THRESHOLD,

            "eligible_for_interview":
                eligible,

            "message": (
                "Candidate is eligible "
                "for interview."
                if eligible
                else
                "Candidate does not meet "
                "the interview eligibility "
                "criteria."
            )
        }

    except HTTPException:
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )