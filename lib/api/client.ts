"use client";

import { ApiError, ReqInit, request } from "./core";

export { ApiError };

// Browser-side API call. Same-origin (/api/* is rewritten to FastAPI), so the
// httpOnly cookie travels automatically. A 401 means the session is gone.
export async function api<T = unknown>(path: string, init: ReqInit = {}): Promise<T> {
  try {
    return await request<T>(path, init);
  } catch (e) {
    if (e instanceof ApiError && e.status === 401 && !path.startsWith("/api/auth/")) {
      window.location.href = "/sign-in?reset=1";
    }
    throw e;
  }
}
