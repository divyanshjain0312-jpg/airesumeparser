"""Upload router — accepts a PDF and returns a session id."""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import Settings, get_settings
from app.models.schemas import UploadResponse

router = APIRouter(prefix="/api", tags=["upload"])

MAX_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {MAX_SIZE_BYTES // (1024 * 1024)} MB limit.",
        )

    session_id = uuid.uuid4().hex[:16]
    upload_dir: Path = settings.upload_path
    dest = upload_dir / f"{session_id}.pdf"
    dest.write_bytes(contents)

    return UploadResponse(
        session_id=session_id,
        filename=file.filename,
        size_bytes=len(contents),
        message="File uploaded successfully.",
    )
