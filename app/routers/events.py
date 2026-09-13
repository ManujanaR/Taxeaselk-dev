"""GET /api/events — Server-Sent Events stream for the signed-in user (one per browser tab)."""
import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user
from app.models import User
from app.services import events

router = APIRouter(prefix="/api", tags=["events"])

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
async def event_stream(user: User = Depends(get_current_user)):
    return StreamingResponse(
        _stream(user.id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )
