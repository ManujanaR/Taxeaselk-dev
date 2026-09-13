"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Building2, Download, CheckCircle2, RotateCcw, X } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge, { BadgeTone } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { requestRevision, resolveResponse } from "@/lib/api/auditor";
import { dateTime, fileSize } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import type { ResponseRow } from "@/lib/types";

const STATUS: Record<ResponseRow["status"], { label: string; tone: BadgeTone }> = {
  unreviewed: { label: "Unreviewed", tone: "warning" },
  resolved: { label: "Resolved", tone: "success" },
  revision_requested: { label: "Revision Requested", tone: "critical" },
};
const FILTERS = ["all", "unreviewed", "resolved", "revision_requested"] as const;

export default function AuditorResponsesManager({ responses }: { responses: ResponseRow[] }) {
  const router = useRouter();
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("all");
  const [query, setQuery] = useState("");
  const [revising, setRevising] = useState<ResponseRow | null>(null);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);

  const rows = responses.filter((r) => (filter === "all" || r.status === filter) && (r.companyName + r.requestTitle + r.referenceCode).toLowerCase().includes(query.toLowerCase()));

  async function act(fn: () => Promise<unknown>, ok: string) {
    setBusy(true);
    try {
      await fn();
      toast.success(ok);
      setRevising(null);
      setNote("");
      router.refresh();
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Client Responses</h1>
          <p className="mt-1 text-sm text-gray-500">Evidence and explanations submitted against your requests for information.</p>
        </div>
        <Link href="/requests"><Button variant="secondary">View Sent Requests</Button></Link>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-2">
        {FILTERS.map((f) => {
          const n = f === "all" ? responses.length : responses.filter((r) => r.status === f).length;
          return (
            <button key={f} onClick={() => setFilter(f)} className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${filter === f ? "bg-brand-blue text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
              {f.replace("_", " ")} <span className="opacity-70">({n})</span>
            </button>
          );
        })}
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search..." className="ml-auto w-56 rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand-blue focus:outline-none" />
      </div>

      <div className="mt-4 space-y-3">
        {rows.length === 0 && <Card className="p-10 text-center text-sm text-gray-400">No responses in this view.</Card>}
        {rows.map((r) => (
          <Card key={r.id} className="p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs text-gray-400">{r.referenceCode}</span>
                  <p className="font-semibold text-gray-800">{r.requestTitle}</p>
                  <Badge tone={STATUS[r.status].tone}>{STATUS[r.status].label}</Badge>
                </div>
                <p className="mt-0.5 flex items-center gap-1 text-xs text-gray-500"><Building2 className="h-3 w-3" /> {r.companyName} · {r.category} · {dateTime(r.createdAt)}</p>
              </div>
              {r.status !== "resolved" && (
                <div className="flex gap-2">
                  <Button variant="success" className="px-3 py-1.5 text-xs" icon={<CheckCircle2 className="h-3.5 w-3.5" />} disabled={busy} onClick={() => act(() => resolveResponse(r.id), `${r.referenceCode} resolved.`)}>Mark Resolved</Button>
                  <Button variant="secondary" className="px-3 py-1.5 text-xs" icon={<RotateCcw className="h-3.5 w-3.5" />} disabled={busy} onClick={() => setRevising(r)}>Request Revision</Button>
                </div>
              )}
            </div>
            <p className="mt-3 rounded-lg bg-gray-50 p-3 text-sm text-gray-700">{r.note}</p>
            {r.revisionNote && <p className="mt-2 text-xs text-red-700"><span className="font-semibold">Your revision note:</span> {r.revisionNote}</p>}
            {r.attachments.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {r.attachments.map((a) => (
                  <a key={a.id} href={`/api/attachments/${a.id}/file`} className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs font-medium text-gray-700 hover:border-brand-blue hover:text-brand-blue">
                    <Download className="h-3.5 w-3.5" /> {a.name} <span className="text-gray-400">({fileSize(a.sizeBytes)})</span>
                  </a>
                ))}
              </div>
            )}
          </Card>
        ))}
      </div>

      {revising && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-lg p-0">
            <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
              <h2 className="text-base font-bold text-gray-900">Request revision — {revising.referenceCode}</h2>
              <button onClick={() => setRevising(null)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4 p-6">
              <textarea rows={4} value={note} onChange={(e) => setNote(e.target.value)} placeholder="Explain what is missing, e.g. 'Please provide the official tax invoice showing the VAT registration number.'" className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue" />
              <div className="flex justify-end gap-2">
                <Button variant="secondary" onClick={() => setRevising(null)} disabled={busy}>Cancel</Button>
                <Button disabled={busy || !note.trim()} onClick={() => act(() => requestRevision(revising.id, note), "Revision request sent to client.")}>Send Revision Request</Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
