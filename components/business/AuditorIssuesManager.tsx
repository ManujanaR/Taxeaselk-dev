"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AlertTriangle, CheckCircle2, Clock, Paperclip, X } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { respondToIssue } from "@/lib/api/business";
import { date, fileSize } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import type { Issue } from "@/lib/types";

const STATUS = {
  action_required: { label: "Action Required", tone: "critical", icon: AlertTriangle },
  pending_clarification: { label: "Awaiting Auditor", tone: "warning", icon: Clock },
  resolved: { label: "Resolved", tone: "success", icon: CheckCircle2 },
} as const;

export default function AuditorIssuesManager({ issues }: { issues: Issue[] }) {
  const router = useRouter();
  const params = useSearchParams();
  const highlight = params.get("issue");
  const [active, setActive] = useState<Issue | null>(null);
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
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
      await respondToIssue(active.id, text, file);
      toast.success("Response sent to your auditor.");
      setActive(null);
      setText("");
      setFile(null);
      router.refresh();
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card className="mt-6 p-5">
      <div className="mb-3 flex items-center justify-between">
        <p className="font-semibold text-gray-800">Auditor Inquiries & Exceptions</p>
        <span className="text-xs text-gray-400">{issues.filter((i) => i.status !== "resolved").length} open</span>
      </div>

      {issues.length === 0 ? (
        <p className="py-6 text-center text-sm text-gray-400">No issues raised by your auditor.</p>
      ) : (
        <div className="divide-y divide-gray-50">
          {issues.map((issue) => {
            const s = STATUS[issue.status];
            const Icon = s.icon;
            return (
              <div
                key={issue.id}
                ref={(el) => {
                  rowRefs.current[issue.id] = el;
                }}
                className={`flex items-start gap-3 py-4 ${highlight === issue.id ? "-mx-3 rounded-lg bg-blue-50/60 px-3" : ""}`}
              >
                <span className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${issue.severity === "critical" ? "bg-red-50 text-red-600" : "bg-amber-50 text-amber-600"}`}>
                  <Icon className="h-4 w-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-medium text-gray-800">{issue.title}</p>
                    <Badge tone={issue.severity === "critical" ? "critical" : "warning"}>{issue.severity}</Badge>
                    <Badge tone={s.tone}>{s.label}</Badge>
                  </div>
                  <p className="mt-1 text-sm text-gray-600">{issue.comment}</p>
                  {issue.source && <p className="mt-1 text-xs text-gray-400">Source: {issue.source}</p>}
                  {issue.responseText && (
                    <div className="mt-2 rounded-lg bg-gray-50 p-2.5 text-xs text-gray-700">
                      <span className="font-semibold">Your response:</span> {issue.responseText}
                      {issue.attachments.map((a) => (
                        <a key={a.id} href={`/api/attachments/${a.id}/file`} className="ml-2 inline-flex items-center gap-1 text-brand-blue hover:underline">
                          <Paperclip className="h-3 w-3" /> {a.name} ({fileSize(a.sizeBytes)})
                        </a>
                      ))}
                    </div>
                  )}
                  <p className="mt-1 text-[11px] text-gray-400">Raised {date(issue.createdAt)}{issue.resolvedAt ? ` · Resolved ${date(issue.resolvedAt)}` : ""}</p>
                </div>
                {issue.status !== "resolved" && (
                  <Button variant="secondary" className="px-3 py-1.5 text-xs" onClick={() => { setActive(issue); setText(issue.responseText); }}>
                    {issue.status === "pending_clarification" ? "Update Response" : "Respond"}
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
                <h2 className="text-base font-bold text-gray-900">{active.title}</h2>
                <p className="text-xs text-gray-500">{active.comment}</p>
              </div>
              <button onClick={() => setActive(null)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100">
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={submit} className="space-y-4 p-6">
              <textarea
                rows={5}
                required
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Explain the treatment, reference the ledger account or voucher, and attach evidence if requested..."
                className="w-full rounded-lg border border-gray-300 p-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue"
              />
              <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-600">
                <Paperclip className="h-4 w-4" />
                <span>{file ? `${file.name} (${fileSize(file.size)})` : "Attach evidence (PDF, XLSX, CSV, image — max 10 MB)"}</span>
                <input type="file" className="hidden" accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
              </label>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="secondary" onClick={() => setActive(null)} disabled={busy}>
                  Cancel
                </Button>
                <Button type="submit" disabled={busy || !text.trim()}>
                  {busy ? "Sending..." : "Submit Explanation"}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </Card>
  );
}
