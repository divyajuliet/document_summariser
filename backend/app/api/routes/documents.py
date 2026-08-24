from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Document
from backend.app.extraction.router import ExtractionRouter


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = Path("uploads")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# Extraction service
extraction_router = ExtractionRouter()


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    # 2. Validate file extension
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Allowed types: "
                f"{', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        )

    # 3. Read file
    content = await file.read()

    # 4. Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 20 MB."
        )

    # 5. Validate empty file
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # 6. Generate unique document ID
    document_id = str(uuid4())

    # 7. Create upload directory
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # 8. Generate stored filename
    stored_filename = f"{document_id}{extension}"

    file_path = UPLOAD_DIR / stored_filename

    # 9. Save physical file
    file_path.write_bytes(content)

    # 10. Create database record
    document = Document(
        document_id=document_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_type=extension,
        mime_type=file.content_type,
        file_size=len(content),
        status="UPLOADED",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # 11. Return document metadata
    return {
        "document_id": document.document_id,
        "original_filename": document.original_filename,
        "stored_filename": document.stored_filename,
        "file_type": document.file_type,
        "mime_type": document.mime_type,
        "file_size": document.file_size,
        "status": document.status,
        "created_at": document.created_at,
    }


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

@router.get("/")
def get_documents(
    db: Session = Depends(get_db)
):

    documents = db.query(Document).all()

    return documents


# ============================================================
# EXTRACT DOCUMENT
# ============================================================

@router.get("/{document_id}/extract")
def extract_document(
    document_id: str,
    db: Session = Depends(get_db)
):

    # 1. Find document in database
    document = (
        db.query(Document)
        .filter(
            Document.document_id == document_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # 2. Find physical file
    file_path = (
        UPLOAD_DIR /
        document.stored_filename
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Stored document file not found."
        )

    # 3. Run extraction pipeline
    try:

        result = extraction_router.extract(
            file_path=file_path,
            document_id=document.document_id,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(exc)}"
        )

    # ========================================================
    # EXTRACT RESULTS
    # ========================================================

    extracted = result["document"]
    attempts = result["attempts"]
    validation = result["validation"]

    # ========================================================
    # BUILD ATTEMPT RESPONSE
    # ========================================================

    attempt_results = []

    for attempt in attempts:

        attempt_results.append(
            {
                "attempt_number": attempt.attempt_number,
                "method": attempt.method,
                "quality_score": attempt.quality_score,
                "status": attempt.status,
                "reason": attempt.reason,
                "error": attempt.error,
            }
        )

    # ========================================================
    # BUILD VALIDATION RESPONSE
    # ========================================================

    validation_result = None

    if validation is not None:

        validation_result = {
            "overall_score": validation.overall_score,
            "decision": validation.decision,
            "questions": [
                {
                    "question": question.question,
                    "passed": question.passed,
                    "score": question.score,
                    "explanation": question.explanation,
                }
                for question in validation.questions
            ],
        }

    # ========================================================
    # RETURN COMPLETE EXTRACTION RESULT
    # ========================================================

    return {
        "document_id": extracted.document_id,

        "extraction": {
            "method": extracted.extraction_method,
            "total_pages": extracted.total_pages,
            "total_characters": extracted.total_characters,
            "pages": [
                {
                    "page_number": page.page_number,
                    "text": page.text,
                    "char_count": page.char_count,
                }
                for page in extracted.pages
            ],
        },

        "qext": {
            "selected_method": extracted.extraction_method,
            "attempts": attempt_results,
        },

        "validation": validation_result,
    }