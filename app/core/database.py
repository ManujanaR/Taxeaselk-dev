from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    pool_pre_ping=not is_sqlite,
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def _register_realtime_hooks():
    from app.services import events  # imported lazily: events -> models/schemas, never back to database

    event.listens_for(SessionLocal, "after_commit")(events.flush_after_commit)
    event.listens_for(SessionLocal, "after_rollback")(events.discard_after_rollback)


_register_realtime_hooks()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
