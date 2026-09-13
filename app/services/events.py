"""In-process event broker feeding Server-Sent Events, one queue per open browser tab.

Events are queued on the SQLAlchemy session and published only after commit, so a
client that refetches on receipt always sees the committed data.

# ponytail: in-memory broker => run one uvicorn worker. Swap publish()/subscribe() for
# Redis pub/sub or Postgres LISTEN/NOTIFY when scaling out; nothing else changes.
"""
import asyncio
import itertools
from collections import defaultdict
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.models import Notification
from app.schemas.shared import NotificationOut

loop: asyncio.AbstractEventLoop | None = None  # set in main.lifespan
_subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)
_seq = itertools.count(1)


def subscribe_queue(user_id: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers[user_id].add(q)
    return q


def unsubscribe_queue(user_id: str, q: asyncio.Queue) -> None:
    _subscribers[user_id].discard(q)
    if not _subscribers[user_id]:
        del _subscribers[user_id]


@contextmanager
def subscribe(user_id: str):
    q = subscribe_queue(user_id)
    try:
        yield q
    finally:
        unsubscribe_queue(user_id, q)


def _deliver(q: asyncio.Queue, event: dict) -> None:
    try:
        q.put_nowait(event)
    except asyncio.QueueFull:
        pass  # slow consumer; the next event (or its reconnect resync) catches it up


def publish(user_id: str, event: dict) -> None:
    """Thread-safe: routers run in the threadpool, queues live on the event loop."""
    queues = list(_subscribers.get(user_id, ()))
    if not queues:
        return
    event = {**event, "id": next(_seq)}
    for q in queues:
        if loop and loop.is_running():
            loop.call_soon_threadsafe(_deliver, q, event)
        else:
            _deliver(q, event)


# ---- session integration ----

def queue_event(db: Session, user_id: str, payload) -> None:
    db.info.setdefault("events", []).append((user_id, payload))


def touch(db: Session, user_id: str) -> None:
    """Silent 'something you are looking at changed' for the other party (no notification row)."""
    queue_event(db, user_id, {"type": "refresh"})


def flush_after_commit(session: Session) -> None:
    for user_id, payload in session.info.pop("events", []):
        if isinstance(payload, Notification):
            payload = {"type": "notification",
                       "notification": NotificationOut.model_validate(payload).model_dump(by_alias=True, mode="json")}
        publish(user_id, payload)


def discard_after_rollback(session: Session) -> None:
    session.info.pop("events", None)
