import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.database import engine
from app.models import Base
from app.routers import ROUTERS
from app.services import events, files


@asynccontextmanager
async def lifespan(_: FastAPI):
    events.loop = asyncio.get_running_loop()
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # DB may be briefly unreachable (pooler blip). Boot anyway so the app serves clear per-request
    # errors instead of crash-looping — a restart loop just hammers the pooler and delays recovery.
    try:
        Base.metadata.create_all(bind=engine)
        _add_missing_columns()
    except OperationalError as e:
        logging.getLogger("uvicorn.error").error("DB init skipped, backend up but degraded: %s", str(e).splitlines()[0])
    files.ensure_bucket()
    yield


def _add_missing_columns():
    """create_all never alters existing tables; add new nullable columns in place. # ponytail: Alembic when this grows."""
    insp = inspect(engine)
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            existing = {c["name"] for c in insp.get_columns(table.name)}
            for col in table.columns:
                if col.name not in existing and col.nullable:
                    conn.execute(text(f'ALTER TABLE {table.name} ADD COLUMN {col.name} {col.type.compile(engine.dialect)}'))


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan,
              docs_url="/docs" if settings.DEBUG else None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in ROUTERS:
    app.include_router(r)


@app.get("/health", tags=["health"])
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "version": settings.VERSION}
