"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Inbox, Paperclip, X, AlertCircle } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge, { BadgeTone } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { respondToRequest } from "@/lib/api/business";
import { date, daysUntil, fileSize } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import type { RfiRequest } from "@/lib/types";

const STATUS: Record<RfiRequest["status"], { label: string; tone: BadgeTone }> = {
  pending: { label: "Needs your answer", tone: "warning" },
  responded: { label: "Awaiting auditor review", tone: "info" },
  revision_requested: { label: "Revision requested", tone: "critical" },
  resolved: { label: "Resolved", tone: "success" },
};
const PRIORITY: Record<RfiRequest["priority"], BadgeTone> = { HIGH: "critical", MEDIUM: "warning", LOW: "info" };

// Everything the auditor has asked this company for, with the answer form.
export default function AuditorRequests({ requests }: { requests: RfiRequest[] }) {
  const router = useRouter();
  const highlight = useSearchParams().get("request");
  const [active, setActive] = useState<RfiRequest | null>(null);
  const [note, setNote] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const rowRefs = useRef<Record<string, HTMLDivElement | null>>({});

  useEffect(() => {
    if (highlight) rowRefs.current[highlight]?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [highlight]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!active) return;
    setBusy(true);
    try {
      await respondToRequest(active.id, note, files);
      toast.success(`Answer to ${active.referenceCode} sent to your auditor.`);
      setActive(null);
      setNote("");
      setFiles([]);
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const open = requests.filter((r) => r.status === "pending" || r.status === "revision_requested").length;

  return (
    <Card className="mt-6 p-5">
      <div className="mb-3 flex items-center justify-between">
        <p className="flex items-center gap-2 font-semibold text-gray-800"><Inbox className="h-4 w-4 text-brand-blue" /> Requests from your auditor</p>
        <span className="text-xs text-gray-400">{open ? `${open} need your answer` : "Nothing waiting on you"}</span>
      </div>

      {requests.length === 0 ? (
        <p className="py-6 text-center text-sm text-gray-400">Your auditor has not requested anything yet.</p>
      ) : (
        <div className="divide-y divide-gray-50">
          {requests.map((r) => {
            const days = daysUntil(r.dueDate);
            const needsAction = r.status === "pending" || r.status === "revision_requested";
            return (
              <div key={r.id} ref={(el) => { rowRefs.current[r.id] = el; }} className={`flex items-start gap-3 py-4 ${highlight === r.id ? "-mx-3 rounded-lg bg-blue-50/60 px-3" : ""}`}>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs text-gray-400">{r.referenceCode}</span>
                    <p className="font-medium text-gray-800">{r.title}</p>
                    <Badge tone={PRIORITY[r.priority]}>{r.priority}</Badge>
                    <Badge tone={STATUS[r.status].tone}>{STATUS[r.status].label}</Badge>
                  </div>
                  {r.description && <p className="mt-1 text-sm text-gray-600">{r.description}</p>}
                  <p className="mt-1 text-[11px] text-gray-400">
                    {r.category} · Issued {date(r.createdAt)}
                    {r.dueDate && <span className={days !== null && days < 0 && needsAction ? " font-semibold text-red-600" : ""}> · Due {date(r.dueDate)}{days !== null && needsAction ? days < 0 ? ` (${-days}d overdue)` : ` (in ${days}d)` : ""}</span>}
                  </p>
                  {r.status === "revision_requested" && r.response?.revisionNote && (
                    <div className="mt-2 flex items-start gap-2 rounded-lg border border-red-100 bg-red-50 p-2.5 text-xs text-red-700">
                      <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      <span><span className="font-semibold">Your auditor asked for a revision:</span> {r.response.revisionNote}</span>
                    </div>
                  )}
                  {r.response && (
                    <div className="mt-2 rounded-lg bg-gray-50 p-2.5 text-xs text-gray-700">
                      <span className="font-semibold">Your answer ({date(r.response.createdAt)}):</span> {r.response.note}
                      <div className="mt-1 flex flex-wrap gap-2">
                        {r.response.attachments.map((a) => (
                          <a key={a.id} href={`/api/attachments/${a.id}/file`} className="inline-flex items-center gap-1 text-brand-blue hover:underline">
                            <Paperclip className="h-3 w-3" /> {a.name} ({fileSize(a.sizeBytes)})
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {needsAction && (
                  <Button variant={r.status === "revision_requested" ? "primary" : "secondary"} className="px-3 py-1.5 text-xs" onClick={() => { setActive(r); setNote(r.response?.note ?? ""); }}>
                    {r.status === "revision_requested" ? "Submit revision" : "Answer"}
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      )}

      {active && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-lg p-0">
            <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
              <div>
                <h2 className="text-base font-bold text-gray-900">{active.referenceCode} · {active.title}</h2>
                <p className="text-xs text-gray-500">{active.description}</p>
              </div>
              <button onClick={() => setActive(null)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
            </div>
            <form onSubmit={submit} className="space-y-4 p-6">
              <textarea rows={4} required value={note} onChange={(e) => setNote(e.target.value)} placeholder="Your explanation for the auditor. Reference the ledger account, voucher or schedule where relevant." className="w-full rounded-lg border border-gray-300 p-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue" />
              <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-600">
                <Paperclip className="h-4 w-4" />
                <span>{files.length ? files.map((f) => f.name).join(", ") : "Attach evidence (invoices, vouchers, confirmations — PDF, XLSX, CSV, images)"}</span>
                <input type="file" multiple className="hidden" accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg" onChange={(e) => setFiles(Array.from(e.target.files ?? []))} />
              </label>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="secondary" onClick={() => setActive(null)} disabled={busy}>Cancel</Button>
                <Button type="submit" disabled={busy || !note.trim()}>{busy ? "Sending..." : "Send answer"}</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </Card>
  );
}
