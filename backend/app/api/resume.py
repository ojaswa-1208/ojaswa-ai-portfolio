
from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    UploadFile,
    File,
)

from app.config import settings
from app.core.rate_limit import limiter
from app.services.resume_parser import (
    extract_pdf_text,
    parse_resume_with_groq,
    ResumeProcessingError,
)
from app.schemas.profile import CandidateProfile


router = APIRouter(
    prefix="/resume",
    tags=["Resume Intelligence"],
)


def check_upload_environment():
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=403,
            detail="Resume upload requires authenticated admin access.",
        )


async def read_resume(upload: UploadFile) -> bytes:
    if upload.content_type != "application/pdf":
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are accepted.",
        )

    content = await upload.read(5 * 1024 * 1024 + 1)

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Maximum PDF size is 5 MB.",
        )

    return content


@router.post("/extract")
@limiter.limit("5/minute")
async def extract_resume(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
):
    check_upload_environment()

    try:
        content = await read_resume(file)
        text = extract_pdf_text(content)

        return {
            "success": True,
            "filename": "resume.pdf",
            "character_count": len(text),
            "extracted_text": text,
        }

    except ResumeProcessingError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    finally:
        await file.close()


@router.post(
    "/parse",
    response_model=CandidateProfile,
)
@limiter.limit("3/minute")
async def parse_resume(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
):
    check_upload_environment()

    try:
        content = await read_resume(file)

        extracted_text = extract_pdf_text(content)

        profile = await parse_resume_with_groq(
            extracted_text
        )

        return profile

    except ResumeProcessingError as exc:
        status_code = (
            503
            if "API key is not configured" in str(exc)
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        )

    finally:
        await file.close()
