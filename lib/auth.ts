import "server-only";
import { redirect } from "next/navigation";
import { apiServer } from "@/lib/api/server";
import type { Session } from "@/lib/types";

export function initials(name: string): string {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]!.toUpperCase()).join("") || "?";
}

export function formattedUserId(session: Session): string {
  return `${session.user.role === "auditor" ? "AUD" : "BIZ"}-${session.user.id.replace(/-/g, "").slice(0, 8).toUpperCase()}`;
}

// Used by the portal layouts. Redirects to sign-in when the cookie is missing/invalid
// or the user is in the wrong portal.
export async function getSession(role: "business" | "auditor"): Promise<Session> {
  let session: Session;
  try {
    session = await apiServer<Session>("/api/auth/me");
  } catch {
    redirect("/sign-in?reset=1");
  }
  if (session.user.role !== role) redirect(session.user.role === "auditor" ? "/auditor-dashboard" : "/dashboard");
  return session;
}
