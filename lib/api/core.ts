export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export type ReqInit = Omit<RequestInit, "body"> & { json?: unknown; body?: BodyInit };

// Shared by the browser client and the server helper. Throws ApiError on any non-2xx.
export async function request<T>(url: string, init: ReqInit = {}, extraHeaders: Record<string, string> = {}): Promise<T> {
  const { json, headers, ...rest } = init;
  const res = await fetch(url, {
    ...rest,
    cache: "no-store",
    headers: { ...(json !== undefined ? { "Content-Type": "application/json" } : {}), ...extraHeaders, ...(headers as Record<string, string>) },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail ?? data);
    } catch {}
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
