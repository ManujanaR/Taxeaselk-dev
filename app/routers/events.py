"""GET /api/events — Server-Sent Events stream for the signed-in user (one per browser tab)."""
import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.database import SessionLocal
from app.core.deps import COOKIE_NAME
from app.core.security import decode_access_token
from app.models import User
from app.services import events

router = APIRouter(prefix="/api", tags=["events"])


def stream_user_id(request: Request) -> str:
    """Authenticate the SSE client in a DB session that closes IMMEDIATELY.

    A normal `Depends(get_db)` session stays open for the whole response; for an SSE stream that
    lives for hours, that pins one pooled connection per open browser tab. Over a day the tabs
    accumulate and exhaust the Supabase pooler, after which every new connection hangs. The stream
    itself only reads the in-memory event queue, so it needs no DB session at all.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth = request.headers.get("authorization", "")
        token = auth[7:] if auth.lower().startswith("bearer ") else None
    payload = decode_access_token(token) if token else None
    if not payload:
        raise HTTPException(401, "Not authenticated")
    with SessionLocal() as db:
        user = db.get(User, payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(401, "Not authenticated")
        return user.id

PING_SECONDS = 15
PADDING = ":" + " " * 2048 + "\n\n"  # defeats proxy buffering so the first real event isn't held back


async def _stream(user_id: str):
    q = events.subscribe_queue(user_id)
    try:
        yield "retry: 2000\n" + PADDING
        while True:
            try:
                ev = await asyncio.wait_for(q.get(), PING_SECONDS)
                yield f"id: {ev['id']}\nevent: {ev['type']}\ndata: {json.dumps(ev)}\n\n"
            except asyncio.TimeoutError:
                yield ": ping\n\n"
    finally:
        events.unsubscribe_queue(user_id, q)


@router.get("/events")
async def event_stream(user_id: str = Depends(stream_user_id)):
    return StreamingResponse(
        _stream(user_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )
