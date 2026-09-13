import Link from "next/link";
import Card from "@/components/ui/Card";
import AuditActionBadge from "@/components/auditor/AuditActionBadge";
import T from "@/components/layout/T";
import { apiServer } from "@/lib/api/server";
import { dateTime, titleCase } from "@/lib/format";
import type { AuditLogEntry, EngagementRow } from "@/lib/types";

export default async function AuditLogPage({ searchParams }: { searchParams: { companyId?: string } }) {
  const companyId = searchParams.companyId;
  const [entries, engagements] = await Promise.all([
    apiServer<AuditLogEntry[]>(`/api/auditor/audit-log${companyId ? `?companyId=${companyId}` : ""}`),
    apiServer<EngagementRow[]>("/api/auditor/engagements"),
  ]);
  const companies = Array.from(new Map(engagements.map((e) => [e.companyId, e.companyName])).entries());

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900"><T k="pages.auditLog.title" /></h1>
      <p className="mt-1 text-sm text-gray-500"><T k="pages.auditLog.subtitle" /></p>

      <div className="mt-5 flex flex-wrap gap-2">
        <Link href="/audit-log" className={`rounded-full px-3 py-1 text-xs font-semibold ${!companyId ? "bg-brand-blue text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>All companies</Link>
        {companies.map(([id, name]) => (
          <Link key={id} href={`/audit-log?companyId=${id}`} className={`rounded-full px-3 py-1 text-xs font-semibold ${companyId === id ? "bg-brand-blue text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>{name}</Link>
        ))}
      </div>

      <Card className="mt-4 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th className="px-4 py-3">Timestamp</th>
              <th className="px-4 py-3">Company</th>
              <th className="px-4 py-3">Actor</th>
              <th className="px-4 py-3">Event</th>
              <th className="px-4 py-3">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {entries.length === 0 && <tr><td colSpan={5} className="px-4 py-10 text-center text-gray-400">No entries yet.</td></tr>}
            {entries.map((e) => (
              <tr key={e.id}>
                <td className="whitespace-nowrap px-4 py-3 font-mono text-xs text-gray-500">{dateTime(e.createdAt)}</td>
                <td className="px-4 py-3 text-gray-800">{e.companyName}</td>
                <td className="px-4 py-3 text-gray-600">{e.actorName} <span className="text-[10px] uppercase text-gray-400">({e.actorRole})</span></td>
                <td className="px-4 py-3"><AuditActionBadge action={titleCase(e.eventType.toLowerCase())} tone={e.tone} /></td>
                <td className="px-4 py-3 text-gray-600">{e.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
