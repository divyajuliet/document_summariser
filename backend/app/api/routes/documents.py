from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile


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


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # 1. Check filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    # 2. Check extension
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        )

    # 3. Read file
    content = await file.read()

    # 4. Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 20 MB."
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # 5. Generate document ID
    document_id = str(uuid4())

    # 6. Create upload directory
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # 7. Create safe stored filename
    stored_filename = f"{document_id}{extension}"

    file_path = UPLOAD_DIR / stored_filename

    # 8. Save file
    file_path.write_bytes(content)

    # 9. Return metadata
    return {
        "document_id": document_id,
        "original_filename": file.filename,
        "stored_filename": stored_filename,
        "file_type": extension,
        "file_size": len(content),
        "status": "uploaded",
    }
