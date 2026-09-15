"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Building2, CheckCircle2, ClipboardList, Download, FileText, Flag, Paperclip, ShieldCheck } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import ProgressBar from "@/components/ui/ProgressBar";
import DocumentStatusBadge from "@/components/business/DocumentStatusBadge";
import EngagementStatusBadge from "./EngagementStatusBadge";
import AuditorChecklistModal from "./AuditorChecklistModal";
import { approveEngagement, flagDocument, verifyDocument } from "@/lib/api/auditor";
import { date, fileSize } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { EngagementDetail } from "@/lib/types";

type Tab = "overview" | "documents";
const TABS: [Tab, TranslationKey][] = [["overview", "audcomp.tabs.overview"], ["documents", "audcomp.tabs.documents"]];

export default function CompanyWorkspace({ detail: d, initialTab }: { detail: EngagementDetail; initialTab?: string }) {
  const router = useRouter();
  const { t } = useLanguage();
  const [tab, setTab] = useState<Tab>(TABS.some(([tb]) => tb === initialTab) ? (initialTab as Tab) : "overview");
  const [checklistOpen, setChecklistOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const eng = d.engagement;
  const canWork = eng.status === "active" || eng.status === "under_review";
  const openRequests = d.requests.filter((r) => r.status !== "resolved" && r.status !== "dismissed");
  const unverified = d.documents.filter((doc) => doc.status !== "verified");
  const signOffBlock = openRequests.length ? t("audcomp.workspace.openRequestsBlock", { count: openRequests.length }) : unverified.length ? t("audcomp.workspace.unverifiedBlock", { count: unverified.length }) : "";
  const provided = d.checklist.filter((c) => c.providedDocumentId).length;
  const evidence = d.requests.flatMap((r) => (r.response?.attachments ?? []).map((a) => ({ ...a, request: r })));

  async function run(fn: () => Promise<unknown>, ok: string) {
    setBusy(true);
    try {
      await fn();
      toast.success(ok);
      router.refresh();
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  function selectTab(t: Tab) {
    setTab(t);
    window.history.replaceState(null, "", `/companies/${eng.id}?tab=${t}`);
  }

  return (
    <div>
      <Link href="/companies" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"><ArrowLeft className="h-4 w-4" /> {t("audcomp.workspace.allCompaniesLink")}</Link>

      <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-brand-blue"><Building2 className="h-6 w-6" /></div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-bold text-gray-900">{eng.companyName}</h1>
              <EngagementStatusBadge status={eng.status} />
            </div>
            <p className="mt-0.5 text-sm text-gray-500">{t("audcomp.workspace.summaryLine", { year: eng.taxYear, tin: eng.tinNumber || "—", status: eng.submittedAt ? t("audcomp.workspace.packSubmitted", { date: date(eng.submittedAt) }) : t("audcomp.workspace.packNotSubmitted") })}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {eng.status === "under_review" && (
            <Button variant="success" icon={<ShieldCheck className="h-4 w-4" />} disabled={busy || signOffBlock !== ""} title={signOffBlock || undefined}
              onClick={() => confirm(t("audcomp.workspace.signOffConfirm", { company: eng.companyName, year: eng.taxYear })) && run(() => approveEngagement(eng.id), t("audcomp.workspace.auditSignedOff"))}>
              {t("audcomp.workspace.approveSignOff")}
            </Button>
          )}
        </div>
      </div>

      <div className="mt-5 flex gap-1 border-b border-gray-100">
        {TABS.map(([tb, labelKey]) => {
          const n = tb === "documents" ? d.documents.length : 0;
          return (
            <button key={tb} onClick={() => selectTab(tb)} className={`border-b-2 px-4 py-2.5 text-sm font-medium ${tab === tb ? "border-brand-blue text-brand-blue" : "border-transparent text-gray-500 hover:text-gray-700"}`}>
              {t(labelKey)}{n ? <span className="ml-1.5 rounded-full bg-gray-100 px-1.5 text-[10px] font-bold text-gray-600">{n}</span> : null}
            </button>
          );
        })}
      </div>

      <div className="mt-6">
        {tab === "overview" && (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_360px]">
            <Card className="p-6">
              <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">{t("common.company")}</p>
              <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
                {([[t("audcomp.workspace.legalName"), d.company.companyName], [t("audcomp.workspace.tradingName"), d.company.tradingName], [t("audcomp.workspace.registrationNo"), d.company.registrationNumber], [t("audcomp.table.tin"), d.company.tinNumber], [t("audcomp.workspace.vat"), d.company.vatNumber], [t("audcomp.workspace.svat"), d.company.isSvatRegistered ? d.company.svatNumber || t("audcomp.workspace.registered") : t("audcomp.workspace.notRegistered")], [t("audcomp.workspace.citRate"), d.company.citTaxRateCategory === "sme_14" ? t("audcomp.workspace.citConcessionary") : t("audcomp.workspace.citStandard")], [t("audcomp.workspace.financialYear"), d.company.financialYear], [t("audcomp.workspace.sector"), d.company.industrySector], [t("audcomp.workspace.contact"), `${d.company.contactEmail} ${d.company.contactPhone}`.trim()], [t("audcomp.workspace.registeredAddress"), d.company.registeredAddress]] as [string, string][]).map(([k, v]) => (
                  <div key={k}><dt className="text-[11px] uppercase tracking-wider text-gray-400">{k}</dt><dd className="font-medium text-gray-800">{v || "—"}</dd></div>
                ))}
              </dl>
            </Card>
            <div className="space-y-6">
              <Card className="p-5">
                <div className="mb-1 flex justify-between text-sm"><span className="font-semibold text-gray-800">{t("audcomp.workspace.auditProgress")}</span><span className="font-bold text-brand-blue">{eng.progressPercent}%</span></div>
                <ProgressBar value={eng.progressPercent} />
                <ul className="mt-4 space-y-1.5 text-sm text-gray-600">
                  <li className="flex justify-between"><span>{t("audcomp.workspace.documentsSubmitted")}</span><span className="font-medium text-gray-800">{d.documents.length}</span></li>
                  <li className="flex justify-between"><span>{t("status.verified")}</span><span className="font-medium text-gray-800">{eng.verifiedCount} / {eng.documentsCount}</span></li>
                  <li className="flex justify-between"><span>{t("audcomp.workspace.openRequestsLabel")}</span><span className={`font-medium ${openRequests.length ? "text-status-warning" : "text-gray-800"}`}>{openRequests.length}</span></li>
                  <li className="flex justify-between"><span>{t("audcomp.workspace.answersToReview")}</span><span className={`font-medium ${eng.needsReview ? "text-brand-blue" : "text-gray-800"}`}>{eng.needsReview}</span></li>
                </ul>
              </Card>
              <Card className="p-5">
                <div className="flex items-center justify-between">
                  <p className="flex items-center gap-2 font-semibold text-gray-800"><ClipboardList className="h-4 w-4 text-brand-blue" /> {t("audcomp.workspace.documentChecklist")}</p>
                  {canWork && <Button variant="secondary" className="px-3 py-1.5 text-xs" onClick={() => setChecklistOpen(true)}>{d.checklist.length ? t("common.edit") : t("audcomp.workspace.publish")}</Button>}
                </div>
                {d.checklist.length === 0 ? (
                  <p className="mt-3 text-xs text-gray-400">{t("audcomp.workspace.checklistNotPublished")}</p>
                ) : (
                  <>
                    <p className="mt-2 text-xs text-gray-500">{t("audcomp.workspace.checklistProvided", { provided, total: d.checklist.length })}</p>
                    <ul className="mt-2 space-y-1">
                      {d.checklist.map((c) => (
                        <li key={c.id} className="flex items-center gap-2 text-xs text-gray-600">
                          {c.providedDocumentId ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : <span className="h-3.5 w-3.5 rounded-full border border-gray-300" />}
                          <span className={c.providedDocumentId ? "line-through" : ""}>{c.name}</span>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </Card>
            </div>
          </div>
        )}

        {tab === "documents" && (
          <div className="space-y-6">
            <Card className="overflow-hidden">
              <div className="border-b border-gray-100 px-5 py-3">
                <p className="font-semibold text-gray-800">{t("audcomp.workspace.submittedPack")}</p>
                <p className="text-xs text-gray-500">{t("audcomp.workspace.submittedPackSub")}</p>
              </div>
              {d.documents.length === 0 ? <p className="px-5 py-8 text-center text-sm text-gray-400">{eng.status === "active" ? t("audcomp.workspace.packNotSubmittedYet") : t("audcomp.workspace.noDocuments")}</p> : (
                <div className="divide-y divide-gray-50">
                  {d.documents.map((doc) => (
                    <div key={doc.id} className="flex items-center gap-3 px-5 py-3">
                      <FileText className="h-4 w-4 shrink-0 text-gray-400" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-800">{doc.name}</p>
                        <p className="text-[11px] text-gray-400">{doc.docType} · {fileSize(doc.sizeBytes)} · {date(doc.createdAt)}</p>
                      </div>
                      <DocumentStatusBadge status={doc.status} />
                      <a href={`/api/documents/${doc.id}/file`} title={t("common.download")} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700"><Download className="h-4 w-4" /></a>
                      {canWork && doc.status !== "verified" && <button disabled={busy} title={t("audcomp.workspace.verifyTitle")} onClick={() => run(() => verifyDocument(doc.id), t("audcomp.workspace.documentVerified", { name: doc.name }))} className="rounded-lg p-1.5 text-emerald-600 hover:bg-emerald-50"><CheckCircle2 className="h-4 w-4" /></button>}
                      {canWork && doc.status !== "review_required" && <button disabled={busy} title={t("audcomp.workspace.flagTitle")} onClick={() => run(() => flagDocument(doc.id), t("audcomp.workspace.documentFlagged", { name: doc.name }))} className="rounded-lg p-1.5 text-amber-600 hover:bg-amber-50"><Flag className="h-4 w-4" /></button>}
                    </div>
                  ))}
                </div>
              )}
            </Card>
            <Card className="overflow-hidden">
              <div className="border-b border-gray-100 px-5 py-3">
                <p className="font-semibold text-gray-800">{t("audcomp.workspace.evidenceFromRequests")}</p>
                <p className="text-xs text-gray-500">{t("audcomp.workspace.evidenceSub")}</p>
              </div>
              {evidence.length === 0 ? <p className="px-5 py-8 text-center text-sm text-gray-400">{t("audcomp.workspace.noEvidenceFiles")}</p> : (
                <div className="divide-y divide-gray-50">
                  {evidence.map((a) => (
                    <div key={a.id} className="flex items-center gap-3 px-5 py-3">
                      <Paperclip className="h-4 w-4 shrink-0 text-gray-400" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-800">{a.name}</p>
                        <p className="text-[11px] text-gray-400">{fileSize(a.sizeBytes)} · {t("audcomp.workspace.answersLabel")} <span className="font-mono">{a.request.referenceCode}</span> {a.request.title}</p>
                      </div>
                      <Badge tone={a.request.status === "resolved" ? "success" : "info"}>{a.request.status === "resolved" ? t("audcomp.requestStatus.resolved") : t("audcomp.workspace.evidenceUnderReview")}</Badge>
                      <a href={`/api/attachments/${a.id}/file`} title={t("common.download")} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700"><Download className="h-4 w-4" /></a>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}
      </div>

      {checklistOpen && <AuditorChecklistModal engagementId={eng.id} companyName={eng.companyName} existing={d.checklist} onClose={() => setChecklistOpen(false)} onPublished={() => { setChecklistOpen(false); router.refresh(); }} />}
    </div>
  );
}
