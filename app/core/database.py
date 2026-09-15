from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")
# Postgres via the Supabase pooler: idle connections get dropped (NAT/pooler timeout) after a while.
# pool_pre_ping alone can still HANG on a half-open socket, so we also give libpq a connect timeout and
# TCP keepalives that fail a dead connection fast, and recycle connections before the pooler's idle cutoff.
# Without this the whole app "loads forever" the morning after a quiet night. (See frontend apiServer timeout.)
pg_connect_args = {"connect_timeout": 10, "keepalives": 1, "keepalives_idle": 30,
                   "keepalives_interval": 10, "keepalives_count": 3}
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else pg_connect_args,
    pool_pre_ping=not is_sqlite,
    pool_recycle=-1 if is_sqlite else 1800,
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
