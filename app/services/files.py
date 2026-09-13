"""Upload storage: UUID filenames under UPLOAD_DIR, extension + size allow-list, streamed to disk."""
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings

ALLOWED = {".pdf": "application/pdf", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
           ".xls": "application/vnd.ms-excel", ".csv": "text/csv", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
CHUNK = 1024 * 1024


async def save_upload(file: UploadFile) -> tuple[str, int, str]:
    """Returns (stored_name, size_bytes, content_type). Rejects bad extensions and oversize files."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(415, f"Unsupported file type {ext or '(none)'}. Allowed: {', '.join(sorted(ALLOWED))}")
    stored = f"{uuid.uuid4()}{ext}"
    path = settings.UPLOAD_DIR / stored
    size = 0
    with path.open("wb") as out:
        while chunk := await file.read(CHUNK):
            size += len(chunk)
            if size > settings.MAX_UPLOAD_BYTES:
                out.close()
                path.unlink(missing_ok=True)
                raise HTTPException(413, f"File exceeds {settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit")
            out.write(chunk)
    if size == 0:
        path.unlink(missing_ok=True)
        raise HTTPException(422, "Empty file")
    return stored, size, ALLOWED[ext]


def delete_stored(stored_name: str) -> None:
    (settings.UPLOAD_DIR / stored_name).unlink(missing_ok=True)


def serve(stored_name: str, original_name: str, content_type: str) -> FileResponse:
    path = settings.UPLOAD_DIR / stored_name
    if not path.is_file():
        raise HTTPException(404, "File missing from storage")
    return FileResponse(path, media_type=content_type, filename=original_name)
