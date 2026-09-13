ï»¿# TaxEaseLK - FastAPI Backend & CIT Engine

A production-ready, fully functional Python FastAPI backend designed specifically for the **TaxEaseLK** Corporate Income Tax (CIT) & Statutory Audit Preparation platform.

Built directly against the updated specification documents:
- `TaxEaseLK_Backend_Architecture_and_API_Specification_Final.docx`
- `TaxEaseLK_Frontend_Functional_Specification_Final.docx`

---

## Architecture Overview

```
backend/
??? app/
?   ??? core/                  # Configuration, database engine & security
?   ?   ??? config.py          # Pydantic Settings & environment variables
?   ?   ??? database.py        # SQLAlchemy session & declarative base
?   ?   ??? security.py        # Password hashing & JWT token management
?   ??? models/                # 16 SQLAlchemy relational database models
?   ?   ??? user.py, company.py, auditor.py, engagement.py, document.py
?   ?   ??? financial.py, checklist.py, issue.py, request_response.py
?   ?   ??? discussion.py, notification.py, audit_log.py, auditor_settings.py
?   ?   ??? __init__.py
?   ??? schemas/               # Pydantic v2 schemas matching Next.js TypeScript types
?   ?   ??? auth.py, dashboard.py, document.py, financial.py, checklist.py
?   ?   ??? auditor_review.py, auditor_dashboard.py, company.py, request_response.py
?   ?   ??? discussion.py, notification.py, settings.py
?   ?   ??? __init__.py
?   ??? services/              # Core business calculation logic
?   ?   ??? tax_engine.py      # Sri Lanka Inland Revenue Act No. 24 of 2017 calculation engine
?   ?   ??? ocr_service.py     # Document OCR & extraction simulation
?   ?   ??? seed_data.py       # Automatic database seeder for out-of-the-box operation
?   ??? routers/               # API route endpoints
?   ?   ??? auth.py            # /api/auth/login, /api/auth/register
?   ?   ??? business_dashboard.py # /api/dashboard (5-stage pipeline & P&L metrics)
?   ?   ??? documents.py       # /api/documents, /api/documents/upload, /api/documents/{id}
?   ?   ??? financials.py      # /api/financials (5 schedule tabs), /api/financials/generate-report
?   ?   ??? auditor_review.py  # /api/auditor-review, /api/auditors/rate, /api/auditors/{email}/reviews
?   ?   ??? checklists.py      # /api/checklists/presets, /api/checklists/{company_name}, /api/auditor/checklists
?   ?   ??? auditor_dashboard.py # /api/auditor/dashboard, /api/auditor/review-queue, /api/nav/badge-counts
?   ?   ??? companies.py       # /api/auditor/companies, /api/auditor/invitations/*
?   ?   ??? requests_responses.py # /api/auditor/requests/*, /api/auditor/responses/*
?   ?   ??? discussions.py     # /api/business/discussions/*, /api/auditor/discussions/*
?   ?   ??? settings.py        # /api/settings, /api/business/settings, /api/auditor/settings
?   ?   ??? notifications.py   # /api/notifications/* (cross-portal auditor & business bells)
?   ?   ??? audit_log.py       # /api/auditor/audit-log, /api/audit-log
?   ??? main.py                # FastAPI app, CORS, lifespan seeder & static mount
??? tests/
?   ??? __init__.py
?   ??? test_api_endpoints.py  # Automated pytest test suite
??? uploads/                   # Document and voucher storage directory
??? requirements.txt           # Python dependency requirements
??? run_server.py              # Single-command server runner
??? .env                       # Local environment configuration
```

---

## Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python run_server.py
```
Or directly with Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

The server will automatically:
1. Create all 16 database tables in `taxease.db` (SQLite).
2. Seed initial compliance data for `ABC (Pvt) Ltd` and `K.L. Perera, FCA` (`BDO Partners`).
3. Launch on `http://localhost:8000`.
4. Expose interactive Swagger documentation at: `http://localhost:8000/docs`.

---

## Frontend Integration

In your Next.js frontend (`c:\Users\M S I\OneDrive\Desktop\frontend`):
Ensure `.env.local` points to this backend:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
Then visit:
- **API Health & Regression Test**: `http://localhost:3000/api-test`
- **Business Dashboard**: `http://localhost:3000/dashboard`
- **Auditor Dashboard**: `http://localhost:3000/auditor-dashboard`
- **Auditor Document Checklist Manager**: `http://localhost:3000/companies`
- **Client Responses Review Queue**: `http://localhost:3000/responses`

---

## Switching to Supabase / PostgreSQL (Production)

To connect directly to a remote Supabase or PostgreSQL database, update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```
The SQLAlchemy models will automatically initialize on startup.
