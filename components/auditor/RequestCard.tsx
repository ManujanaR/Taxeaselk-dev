"use client";

import { useState } from "react";
import Link from "next/link";
import { Bell, Building2, CheckCircle2, Download, RotateCcw, Trash2, X } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge, { BadgeTone } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { dismissRequest, remindRequest, requestRevision, resolveRequest } from "@/lib/api/auditor";
import { date, dateTime, daysUntil, fileSize } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { RfiRequest } from "@/lib/types";

export const REQUEST_STATUS: Record<RfiRequest["status"], { key: TranslationKey; tone: BadgeTone }> = {
  pending: { key: "audcomp.requestStatus.pending", tone: "warning" },
  responded: { key: "audcomp.requestStatus.responded", tone: "info" },
  revision_requested: { key: "audcomp.requestStatus.revisionRequested", tone: "critical" },
  resolved: { key: "audcomp.requestStatus.resolved", tone: "success" },
  dismissed: { key: "audcomp.requestStatus.dismissed", tone: "neutral" },
};
export const PRIORITY_TONE: Record<RfiRequest["priority"], BadgeTone> = { HIGH: "critical", MEDIUM: "warning", LOW: "info" };

// One request as the auditor sees it: the ask, the client's answer + evidence, and the actions. Used by the
// cross-company queue and by the company page.
export default function RequestCard({ request: r, companyName, companyHref, onChanged }: { request: RfiRequest; companyName?: string; companyHref?: string; onChanged: () => void }) {
  const { t } = useLanguage();
  const [revising, setRevising] = useState(false);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const days = daysUntil(r.dueDate);
  const waiting = r.status === "pending" || r.status === "revision_requested";
  const open = r.status !== "resolved" && r.status !== "dismissed";

  async function act(fn: () => Promise<unknown>, ok: string) {
    setBusy(true);
    try {
      await fn();
      toast.success(ok);
      setRevising(false);
      setNote("");
      onChanged();
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card className="p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-xs text-gray-400">{r.referenceCode}</span>
            <p className="font-semibold text-gray-800">{r.title}</p>
            <Badge tone={PRIORITY_TONE[r.priority]}>{r.priority}</Badge>
            <Badge tone={REQUEST_STATUS[r.status].tone}>{t(REQUEST_STATUS[r.status].key)}</Badge>
          </div>
          <p className="mt-0.5 flex flex-wrap items-center gap-1 text-xs text-gray-500">
            {companyName && (
              <>
                <Building2 className="h-3 w-3" />
                {companyHref ? <Link href={companyHref} className="hover:text-brand-blue hover:underline">{companyName}</Link> : companyName}
                <span>·</span>
              </>
            )}
            {r.category} · {t("audcomp.requestCard.issuedOn", { date: date(r.createdAt) })}
            {r.dueDate && <span className={waiting && days !== null && days < 0 ? "font-semibold text-red-600" : ""}> · {t("audcomp.requestCard.dueOn", { date: date(r.dueDate) })}{waiting && days !== null && days < 0 ? ` ${t("audcomp.requestCard.overdueDays", { days: -days })}` : ""}</span>}
          </p>
          {r.description && <p className="mt-2 text-sm text-gray-600">{r.description}</p>}
        </div>
        <div className="flex shrink-0 gap-2">
          {r.status === "responded" && (
            <>
              <Button variant="success" className="px-3 py-1.5 text-xs" icon={<CheckCircle2 className="h-3.5 w-3.5" />} disabled={busy} onClick={() => act(() => resolveRequest(r.id), t("audcomp.toast.requestResolved", { ref: r.referenceCode }))}>{t("audcomp.actions.resolve")}</Button>
              <Button variant="secondary" className="px-3 py-1.5 text-xs" icon={<RotateCcw className="h-3.5 w-3.5" />} disabled={busy} onClick={() => setRevising(true)}>{t("audcomp.actions.sendBack")}</Button>
            </>
          )}
          {waiting && <Button variant="secondary" className="px-3 py-1.5 text-xs" icon={<Bell className="h-3.5 w-3.5" />} disabled={busy} onClick={() => act(() => remindRequest(r.id), t("audcomp.toast.reminderSent"))}>{t("audcomp.actions.remind")}</Button>}
          {open && <Button variant="secondary" className="px-3 py-1.5 text-xs text-gray-500" icon={<Trash2 className="h-3.5 w-3.5" />} disabled={busy} onClick={() => confirm(t("audcomp.requestCard.dismissConfirm", { ref: r.referenceCode })) && act(() => dismissRequest(r.id), t("audcomp.toast.requestDismissed", { ref: r.referenceCode }))}>{t("audcomp.actions.dismiss")}</Button>}
        </div>
      </div>

      {r.response && (
        <div className="mt-3 rounded-lg border border-gray-100 bg-gray-50 p-3">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-400">{t("audcomp.requestCard.clientAnswer", { date: dateTime(r.response.createdAt) })}</p>
          <p className="mt-1 whitespace-pre-wrap text-sm text-gray-700">{r.response.note}</p>
          {r.response.attachments.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {r.response.attachments.map((a) => (
                <a key={a.id} href={`/api/attachments/${a.id}/file`} className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 hover:border-brand-blue hover:text-brand-blue">
                  <Download className="h-3.5 w-3.5" /> {a.name} <span className="text-gray-400">({fileSize(a.sizeBytes)})</span>
                </a>
              ))}
            </div>
          )}
          {r.status === "revision_requested" && r.response.revisionNote && <p className="mt-2 text-xs text-red-700"><span className="font-semibold">{t("audcomp.requestCard.youAskedFor")}</span> {r.response.revisionNote}</p>}
        </div>
      )}

      {revising && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-lg p-0">
            <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
              <h2 className="text-base font-bold text-gray-900">{t("audcomp.requestCard.sendBackTitle", { ref: r.referenceCode })}</h2>
              <button onClick={() => setRevising(false)} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4 p-6">
              <textarea rows={4} value={note} onChange={(e) => setNote(e.target.value)} placeholder={t("audcomp.requestCard.sendBackPlaceholder")} className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none focus:ring-1 focus:ring-brand-blue" />
              <div className="flex justify-end gap-2">
                <Button variant="secondary" onClick={() => setRevising(false)} disabled={busy}>{t("common.cancel")}</Button>
                <Button disabled={busy || !note.trim()} onClick={() => act(() => requestRevision(r.id, note), t("audcomp.toast.sentBackToClient"))}>{t("audcomp.actions.sendBack")}</Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </Card>
  );
}
