# TaxEaseLK Frontend

Next.js 14 (App Router) + Tailwind. Two portals: Business (`/dashboard`, `/documents`, `/financials`, `/auditor-review`, `/discussions`, `/settings`) and Auditor (`/auditor-dashboard`, `/companies`, `/companies/[engagementId]` (overview · documents), `/requests`, `/auditor-discussions`, `/audit-log`, `/auditor-settings`).

Domain model in one line: the auditor publishes a **Checklist** (standing document list) and raises **Requests** (anything else: vouchers, clarifications, findings); the client answers a request once with a note and files; the auditor resolves it or sends it back. Evidence stays attached to the request and is listed on the company page.

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
- Mutations call `router.refresh()` so server-rendered data re-fetches.
- `lib/realtime.tsx` opens one Server-Sent Events stream (`/api/events`) per tab. Every event from the other portal re-renders the current page and bumps a `version` that client-fetched components (bell, sidebar badges, discussions, engagement drawer, rating badge) refetch on. No polling anywhere. Note: HTTP/1.1 allows 6 connections per origin and each tab holds one stream; serve over HTTP/2 in production.
- `compress: false` in `next.config.js` because Next's gzip buffers the proxied event stream; let nginx/Caddy compress.
- The only browser storage used is the language preference.

## Production (how the container runs it)

The container serves a **production build** via systemd (`taxease-frontend.service` runs `npm run start`). `./sync.sh` rebuilds it on each deploy. Dev mode (`npm run dev`) is only for local work.

## Building

```bash
npm run build && npm start   # set API_URL to the internal backend URL and JWT_SECRET in the environment
```

Serve over HTTPS: with `DEBUG=false` the backend marks the session cookie `Secure`.
