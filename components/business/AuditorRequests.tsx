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
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { RfiRequest } from "@/lib/types";

const STATUS: Record<RfiRequest["status"], { label: TranslationKey; tone: BadgeTone }> = {
  pending: { label: "bizcomp.auditorRequests.statusPending", tone: "warning" },
  responded: { label: "bizcomp.auditorRequests.statusResponded", tone: "info" },
  revision_requested: { label: "bizcomp.auditorRequests.statusRevisionRequested", tone: "critical" },
  resolved: { label: "bizcomp.auditorRequests.statusResolved", tone: "success" },
  dismissed: { label: "bizcomp.auditorRequests.statusDismissed", tone: "neutral" },
};
const PRIORITY: Record<RfiRequest["priority"], BadgeTone> = { HIGH: "critical", MEDIUM: "warning", LOW: "info" };

// Everything the auditor has asked this company for, with the answer form.
export default function AuditorRequests({ requests }: { requests: RfiRequest[] }) {
  const { t } = useLanguage();
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
      toast.success(t("bizcomp.auditorRequests.answerSentToast", { code: active.referenceCode }));
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
        <p className="flex items-center gap-2 font-semibold text-gray-800"><Inbox className="h-4 w-4 text-brand-blue" /> {t("bizcomp.auditorRequests.heading")}</p>
        <span className="text-xs text-gray-400">{open ? t("bizcomp.auditorRequests.needAnswerCount", { count: open }) : t("bizcomp.auditorRequests.nothingWaiting")}</span>
      </div>

      {requests.length === 0 ? (
        <p className="py-6 text-center text-sm text-gray-400">{t("bizcomp.auditorRequests.emptyState")}</p>
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
                    <Badge tone={STATUS[r.status].tone}>{t(STATUS[r.status].label)}</Badge>
                  </div>
                  {r.description && <p className="mt-1 text-sm text-gray-600">{r.description}</p>}
                  <p className="mt-1 text-[11px] text-gray-400">
                    {r.category} · {t("bizcomp.auditorRequests.issuedLabel")} {date(r.createdAt)}
                    {r.dueDate && <span className={days !== null && days < 0 && needsAction ? " font-semibold text-red-600" : ""}> · {t("bizcomp.auditorRequests.dueLabel")} {date(r.dueDate)}{days !== null && needsAction ? (days < 0 ? ` (${t("bizcomp.auditorRequests.overdueBy", { count: -days })})` : ` (${t("bizcomp.auditorRequests.dueInDays", { count: days })})`) : ""}</span>}
                  </p>
                  {r.status === "revision_requested" && r.response?.revisionNote && (
                    <div className="mt-2 flex items-start gap-2 rounded-lg border border-red-100 bg-red-50 p-2.5 text-xs text-red-700">
                      <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      <span><span className="font-semibold">{t("bizcomp.auditorRequests.revisionAskedLabel")}</span> {r.response.revisionNote}</span>
                    </div>
                  )}
                  {r.response && (
                    <div className="mt-2 rounded-lg bg-gray-50 p-2.5 text-xs text-gray-700">
                      <span className="font-semibold">{t("bizcomp.auditorRequests.yourAnswerLabel", { date: date(r.response.createdAt) })}</span> {r.response.note}
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
                    {r.status === "revision_requested" ? t("bizcomp.auditorRequests.submitRevision") : t("bizcomp.auditorRequests.answer")}
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      )}

      {active && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="flex max-h-[90vh] w-full max-w-lg flex-col p-0">
            <div className="flex shrink-0 items-center justify-between gap-3 border-b border-gray-100 px-6 py-4">
              <div className="min-w-0">
                <h2 className="truncate text-base font-bold text-gray-900">{active.referenceCode} · {active.title}</h2>
                <p className="text-xs text-gray-500">{active.description}</p>
              </div>
              <button onClick={() => setActive(null)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
            </div>
            <form onSubmit={submit} className="flex-1 space-y-4 overflow-y-auto p-6">
              <textarea rows={4} required value={note} onChange={(e) => setNote(e.target.value)} placeholder={t("bizcomp.auditorRequests.answerPlaceholder")} className="w-full rounded-lg border border-gray-300 p-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue" />
              <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-600">
                <Paperclip className="h-4 w-4" />
                <span>{files.length ? files.map((f) => f.name).join(", ") : t("bizcomp.auditorRequests.attachEvidence")}</span>
                <input type="file" multiple className="hidden" accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg" onChange={(e) => setFiles(Array.from(e.target.files ?? []))} />
              </label>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="secondary" onClick={() => setActive(null)} disabled={busy}>{t("common.cancel")}</Button>
                <Button type="submit" disabled={busy || !note.trim()}>{busy ? t("bizcomp.auditorRequests.sending") : t("bizcomp.auditorRequests.sendAnswer")}</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </Card>
  );
}
