# TaxEaseLK Backend

FastAPI + SQLAlchemy API for the TaxEaseLK Corporate Income Tax audit-prep platform (Sri Lanka Inland Revenue Act No. 24 of 2017).

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # set SECRET_KEY (openssl rand -hex 32); SQLite is the default
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Tables are created on first boot. Swagger UI is at `/docs` when `DEBUG=true`.

## Tests

```bash
.venv/bin/pytest -q      # walks the full business <-> auditor flow on a scratch SQLite DB
.venv/bin/python app/services/tax_engine.py   # CIT waterfall self-check
```

## Production (Supabase Postgres)

1. In the Supabase dashboard: reset the database password, then copy the **Session pooler** connection string (IPv4-safe).
2. If the old prototype ever ran against this project, run `scripts/drop_legacy_tables.sql` in the SQL editor once.
3. `.env`:
   ```
   DEBUG=false
   CORS_ORIGINS=["https://app.yourdomain.lk"]
   DATABASE_URL=postgresql+psycopg2://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require
   SECRET_KEY=<64 hex chars, same value as JWT_SECRET in the frontend>
   GEMINI_API_KEY=<optional; enables /api/financials/extract>
   UPLOAD_DIR=/var/lib/taxease/uploads      # or, to keep files in Supabase Storage (private bucket, created on boot):
   SUPABASE_URL=https://<ref>.supabase.co
   SUPABASE_SERVICE_KEY=<service_role key>
   SUPABASE_BUCKET=taxease-files
   ```
4. `uvicorn app.main:app --host 127.0.0.1 --port 8000` (single worker, see Realtime) behind the Next.js app (it proxies `/api/*`). `DEBUG=false` makes the session cookie `Secure`, so the frontend must be served over HTTPS.

## Layout

```
app/
  main.py            app factory, CORS, lifespan create_all
  core/              config (pydantic-settings), database, security (bcrypt + PyJWT), deps (auth/role guards)
  models.py          all tables, FK-by-id; an invitation is an engagement with status 'invited'
  schemas/           Pydantic models (camelCase JSON in/out)
  routers/           auth, business, auditor, documents, financials, issues, discussions, notifications
  services/          tax_engine (pure CIT waterfall), pipeline (5-stage progress), files (uploads),
                     extract (Gemini), notify (notifications + audit log)
tests/test_flows.py  end-to-end flow test
```

Realtime: `GET /api/events` is a Server-Sent Events stream per signed-in tab. `notify()`/`touch()` queue events on the
SQLAlchemy session and `services/events.py` publishes them after commit. The broker is in-process, so run **one**
uvicorn worker; swap `publish()`/`subscribe()` for Redis pub/sub or Postgres LISTEN/NOTIFY to scale out.

Auth: `POST /api/auth/login` sets an httpOnly `taxease_session` JWT cookie; every other route requires it and checks the role. Company/auditor identity always comes from the cookie, never from request parameters.
