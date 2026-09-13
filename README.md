# TaxEaseLK Frontend

Next.js 14 (App Router) + Tailwind. Two portals: Business (`/dashboard`, `/documents`, `/financials`, `/auditor-review`, `/discussions`, `/settings`) and Auditor (`/auditor-dashboard`, `/companies`, `/auditor-documents`, `/responses`, `/requests`, `/auditor-discussions`, `/audit-log`, `/auditor-settings`).

## Run locally

```bash
npm install
cp .env.local.example .env.local   # API_URL=http://localhost:8000, JWT_SECRET = backend SECRET_KEY
npm run dev
```

The backend must be running (see `../backend/README.md`).

## How it talks to the backend

- `next.config.js` rewrites `/api/*` to `API_URL`, so the browser is same-origin and the httpOnly session cookie just works.
- `middleware.ts` verifies the cookie with `jose` and redirects: no session → `/sign-in`; wrong portal → own dashboard.
- Server Components fetch with `lib/api/server.ts` (forwards the cookie); client components use `lib/api/client.ts`. Both throw `ApiError` on non-2xx; a client 401 sends the user to sign-in.
- Typed wrappers live in `lib/api/business.ts`, `lib/api/auditor.ts`, `lib/api/notifications.ts`; types in `lib/types/index.ts` mirror the backend schemas.
- Mutations call `router.refresh()` so server-rendered data re-fetches. The notification bell, sidebar badges and open discussion thread poll every 30 s.
- The only browser storage used is the language preference.

## Production

```bash
npm run build && npm start   # set API_URL to the internal backend URL and JWT_SECRET in the environment
```

Serve over HTTPS: with `DEBUG=false` the backend marks the session cookie `Secure`.
