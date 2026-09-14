import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ApiError, ReqInit, request } from "./core";

const API_URL = process.env.API_URL || "http://localhost:8000";

// Server Components / layouts: talk to FastAPI directly, forwarding the session cookie.
export async function apiServer<T = unknown>(path: string, init: ReqInit = {}): Promise<T> {
  try {
    return await request<T>(`${API_URL}${path}`, init, { cookie: cookies().toString() });
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) redirect("/sign-in?reset=1"); // session invalid on the backend
    throw e;
  }
}
