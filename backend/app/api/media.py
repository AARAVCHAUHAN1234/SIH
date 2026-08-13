import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.inspection import Inspection
from app.models.media import MediaAsset

router = APIRouter(
    prefix="/api/v1/media",
    tags=["Media"],
)

MEDIA_DIR = "storage/media"

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "video/mp4",
    "video/webm",
}

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


@router.post("/upload", status_code=201)
async def upload_media(
    inspection_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Check inspection
    inspection = db.get(Inspection, uuid.UUID(inspection_id))

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported media type: {file.content_type}",
        )

    # Create storage directory
    os.makedirs(MEDIA_DIR, exist_ok=True)

    # Generate unique filename
    extension = os.path.splitext(file.filename or "")[1]
    stored_filename = f"{uuid.uuid4()}{extension}"

    storage_path = os.path.join(
        MEDIA_DIR,
        stored_filename,
    )

    # Save file
    file_size = 0

    try:
        with open(storage_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)

                if file_size > MAX_FILE_SIZE:
                    buffer.close()
                    os.remove(storage_path)

                    raise HTTPException(
                        status_code=413,
                        detail="File too large. Maximum size is 500 MB.",
                    )

                buffer.write(chunk)

    finally:
        await file.close()

    # Create database record
    media = MediaAsset(
        inspection_id=inspection.id,
        original_filename=file.filename or "unknown",
        storage_path=storage_path,
        media_type=file.content_type,
        file_size=file_size,
        processing_status="uploaded",
    )

    db.add(media)
    db.commit()
    db.refresh(media)

    return {
        "id": media.id,
        "inspection_id": media.inspection_id,
        "original_filename": media.original_filename,
        "storage_path": media.storage_path,
        "media_type": media.media_type,
        "file_size": media.file_size,
        "processing_status": media.processing_status,
    }