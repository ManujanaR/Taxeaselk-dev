import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

const BUSINESS = ["/dashboard", "/documents", "/financials", "/auditor-review", "/discussions", "/settings"];
const AUDITOR = ["/auditor-dashboard", "/companies", "/requests", "/auditor-discussions", "/audit-log", "/auditor-settings"];
const AUTH_PAGES = ["/sign-in", "/sign-up", "/role"];
const HOME: Record<string, string> = { business: "/dashboard", auditor: "/auditor-dashboard" };

const startsWithAny = (path: string, prefixes: string[]) => prefixes.some((p) => path === p || path.startsWith(p + "/"));

// First line of defence only: redirects by cookie role. The backend re-verifies every request.
export async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;
  if (path === "/sign-in" && req.nextUrl.searchParams.get("reset") === "1") {
    // The backend rejected a well-signed cookie (e.g. the user no longer exists): drop it and show sign-in.
    const res = NextResponse.redirect(new URL("/sign-in", req.url));
    res.cookies.delete("taxease_session");
    return res;
  }
  const token = req.cookies.get("taxease_session")?.value;
  let role: string | null = null;
  if (token) {
    try {
      const { payload } = await jwtVerify(token, new TextEncoder().encode(process.env.JWT_SECRET));
      role = typeof payload.role === "string" ? payload.role : null;
    } catch {}
  }

  const wantsBusiness = startsWithAny(path, BUSINESS);
  const wantsAuditor = startsWithAny(path, AUDITOR);

  if (!role && (wantsBusiness || wantsAuditor)) {
    const res = NextResponse.redirect(new URL("/sign-in", req.url));
    if (token) res.cookies.delete("taxease_session");
    return res;
  }
  if (role && ((role === "business" && wantsAuditor) || (role === "auditor" && wantsBusiness) || startsWithAny(path, AUTH_PAGES))) {
    return NextResponse.redirect(new URL(HOME[role] ?? "/sign-in", req.url));
  }
  return NextResponse.next();
}

export const config = { matcher: ["/((?!_next|api|images|favicon.ico|logo.png).*)"] };
