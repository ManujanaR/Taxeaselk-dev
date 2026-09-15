import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, ReqInit, request } from "./core";

const API_URL = process.env.API_URL || "http://localhost:8000";

// Server Components / layouts: talk to FastAPI directly, forwarding the session cookie.
// A 15s timeout keeps a stalled backend from hanging the render forever under the
// loading splash — the abort throws, which the caller (e.g. getSession) treats like any
// other failure and redirects to sign-in. Callers may pass their own signal to override.
export async function apiServer<T = unknown>(path: string, init: ReqInit = {}): Promise<T> {
  try {
    return await request<T>(`${API_URL}${path}`, { signal: AbortSignal.timeout(15000), ...init }, { cookie: cookies().toString() });
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) redirect("/sign-in?reset=1"); // session invalid on the backend
    throw e;
  }
}
