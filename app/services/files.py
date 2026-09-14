"""Upload storage. UUID object names, extension + size allow-list.

Backend is Supabase Storage (private bucket, service-role key) when SUPABASE_URL and
SUPABASE_SERVICE_KEY are set; otherwise files live under UPLOAD_DIR on local disk.
"""
import uuid
from pathlib import Path

import httpx
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse, Response

from app.core.config import settings

ALLOWED = {".pdf": "application/pdf", ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
           ".xls": "application/vnd.ms-excel", ".csv": "text/csv", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
CHUNK = 1024 * 1024


def _supabase() -> bool:
    return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}", "apikey": settings.SUPABASE_SERVICE_KEY}


def _object_url(stored_name: str) -> str:
    return f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{stored_name}"


def ensure_bucket() -> None:
    """Create the private bucket on startup if it doesn't exist (idempotent)."""
    if not _supabase():
        return
    if httpx.get(f"{settings.SUPABASE_URL}/storage/v1/bucket/{settings.SUPABASE_BUCKET}", headers=_headers(), timeout=20).status_code == 200:
        return
    r = httpx.post(f"{settings.SUPABASE_URL}/storage/v1/bucket", headers=_headers(),
                   json={"id": settings.SUPABASE_BUCKET, "name": settings.SUPABASE_BUCKET, "public": False,
                         "file_size_limit": settings.MAX_UPLOAD_BYTES}, timeout=20)
    if r.status_code not in (200, 201) and "BucketAlreadyExists" not in r.text:
        raise RuntimeError(f"Supabase Storage bucket check failed: {r.status_code} {r.text[:200]}")


async def _read_limited(file: UploadFile) -> bytes:
    buf = bytearray()
    while chunk := await file.read(CHUNK):
        buf.extend(chunk)
        if len(buf) > settings.MAX_UPLOAD_BYTES:
            raise HTTPException(413, f"File exceeds {settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit")
    if not buf:
        raise HTTPException(422, "Empty file")
    return bytes(buf)


async def save_upload(file: UploadFile) -> tuple[str, int, str]:
    """Returns (stored_name, size_bytes, content_type)."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(415, f"Unsupported file type {ext or '(none)'}. Allowed: {', '.join(sorted(ALLOWED))}")
    stored, ctype = f"{uuid.uuid4()}{ext}", ALLOWED[ext]
    data = await _read_limited(file)
    if _supabase():
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(_object_url(stored), headers={**_headers(), "Content-Type": ctype, "x-upsert": "false"}, content=data)
        if r.status_code not in (200, 201):
            raise HTTPException(502, f"File storage failed: {r.text[:200]}")
    else:
        (settings.UPLOAD_DIR / stored).write_bytes(data)
    return stored, len(data), ctype


def read_bytes(stored_name: str) -> bytes:
    if _supabase():
        r = httpx.get(_object_url(stored_name), headers=_headers(), timeout=60)
        if r.status_code != 200:
            raise HTTPException(404, "File missing from storage")
        return r.content
    path = settings.UPLOAD_DIR / stored_name
    if not path.is_file():
        raise HTTPException(404, "File missing from storage")
    return path.read_bytes()


def delete_stored(stored_name: str) -> None:
    if _supabase():
        httpx.delete(_object_url(stored_name), headers=_headers(), timeout=30)  # best effort; a missing object is fine
    else:
        (settings.UPLOAD_DIR / stored_name).unlink(missing_ok=True)


def serve(stored_name: str, original_name: str, content_type: str):
    if _supabase():
        return Response(read_bytes(stored_name), media_type=content_type,
                        headers={"Content-Disposition": f'attachment; filename="{original_name}"'})
    path = settings.UPLOAD_DIR / stored_name
    if not path.is_file():
        raise HTTPException(404, "File missing from storage")
    return FileResponse(path, media_type=content_type, filename=original_name)
