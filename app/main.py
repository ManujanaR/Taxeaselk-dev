import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal

# Routers
from app.routers.auth import router as auth_router
from app.routers.business_dashboard import router as business_dashboard_router
from app.routers.documents import router as documents_router
from app.routers.financials import router as financials_router
from app.routers.auditor_review import router as auditor_review_router
from app.routers.checklists import router as checklists_router
from app.routers.auditor_dashboard import router as auditor_dashboard_router
from app.routers.companies import router as companies_router
from app.routers.requests_responses import router as requests_responses_router
from app.routers.discussions import router as discussions_router
from app.routers.settings import router as settings_router
from app.routers.notifications import router as notifications_router
from app.routers.audit_log import router as audit_log_router

def init_database():
    Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    init_database()
    yield
    print(f"Shutting down {settings.PROJECT_NAME}...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend for TaxEaseLK Next.js Application",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for document downloads and uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include all API Routers
app.include_router(auth_router)
app.include_router(business_dashboard_router)
app.include_router(documents_router)
app.include_router(financials_router)
app.include_router(auditor_review_router)
app.include_router(checklists_router)
app.include_router(auditor_dashboard_router)
app.include_router(companies_router)
app.include_router(requests_responses_router)
app.include_router(discussions_router)
app.include_router(settings_router)
app.include_router(notifications_router)
app.include_router(audit_log_router)

@app.get("/", tags=["Health"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "service": "TaxEaseLK Compliance & CIT Engine"
    }
