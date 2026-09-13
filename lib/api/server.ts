import "server-only";
import { cookies } from "next/headers";
import { ReqInit, request } from "./core";

const API_URL = process.env.API_URL || "http://localhost:8000";

// Server Components / layouts: talk to FastAPI directly, forwarding the session cookie.
export function apiServer<T = unknown>(path: string, init: ReqInit = {}): Promise<T> {
  return request<T>(`${API_URL}${path}`, init, { cookie: cookies().toString() });
}
