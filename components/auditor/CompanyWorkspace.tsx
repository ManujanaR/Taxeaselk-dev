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
import type { EngagementDetail } from "@/lib/types";

type Tab = "overview" | "documents";
const TABS: [Tab, string][] = [["overview", "Overview"], ["documents", "Documents"]];

export default function CompanyWorkspace({ detail: d, initialTab }: { detail: EngagementDetail; initialTab?: string }) {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>(TABS.some(([t]) => t === initialTab) ? (initialTab as Tab) : "overview");
  const [checklistOpen, setChecklistOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const eng = d.engagement;
  const canWork = eng.status === "active" || eng.status === "under_review";
  const openRequests = d.requests.filter((r) => r.status !== "resolved");
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
      <Link href="/companies" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"><ArrowLeft className="h-4 w-4" /> All companies</Link>

      <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-brand-blue"><Building2 className="h-6 w-6" /></div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-bold text-gray-900">{eng.companyName}</h1>
              <EngagementStatusBadge status={eng.status} />
            </div>
            <p className="mt-0.5 text-sm text-gray-500">Tax year {eng.taxYear} · TIN {eng.tinNumber || "—"} · {eng.submittedAt ? `Pack submitted ${date(eng.submittedAt)}` : "Pack not submitted yet"}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {eng.status === "under_review" && (
            <Button variant="success" icon={<ShieldCheck className="h-4 w-4" />} disabled={busy || openRequests.length > 0} title={openRequests.length ? `${openRequests.length} open request(s) must be resolved first` : undefined}
              onClick={() => confirm(`Sign off the CIT return for ${eng.companyName} (${eng.taxYear})? This is final.`) && run(() => approveEngagement(eng.id), "Audit signed off.")}>
              Approve &amp; Sign Off
            </Button>
          )}
        </div>
      </div>

      <div className="mt-5 flex gap-1 border-b border-gray-100">
        {TABS.map(([t, label]) => {
          const n = t === "documents" ? d.documents.length : 0;
          return (
            <button key={t} onClick={() => selectTab(t)} className={`border-b-2 px-4 py-2.5 text-sm font-medium ${tab === t ? "border-brand-blue text-brand-blue" : "border-transparent text-gray-500 hover:text-gray-700"}`}>
              {label}{n ? <span className="ml-1.5 rounded-full bg-gray-100 px-1.5 text-[10px] font-bold text-gray-600">{n}</span> : null}
            </button>
          );
        })}
      </div>

      <div className="mt-6">
        {tab === "overview" && (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_360px]">
            <Card className="p-6">
              <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Company</p>
              <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
                {([["Legal name", d.company.companyName], ["Trading name", d.company.tradingName], ["Registration no.", d.company.registrationNumber], ["TIN", d.company.tinNumber], ["VAT", d.company.vatNumber], ["SVAT", d.company.isSvatRegistered ? d.company.svatNumber || "Registered" : "Not registered"], ["CIT rate", d.company.citTaxRateCategory === "sme_14" ? "14% concessionary" : "30% standard"], ["Financial year", d.company.financialYear], ["Sector", d.company.industrySector], ["Contact", `${d.company.contactEmail} ${d.company.contactPhone}`.trim()], ["Registered address", d.company.registeredAddress]] as [string, string][]).map(([k, v]) => (
                  <div key={k}><dt className="text-[11px] uppercase tracking-wider text-gray-400">{k}</dt><dd className="font-medium text-gray-800">{v || "—"}</dd></div>
                ))}
              </dl>
            </Card>
            <div className="space-y-6">
              <Card className="p-5">
                <div className="mb-1 flex justify-between text-sm"><span className="font-semibold text-gray-800">Audit progress</span><span className="font-bold text-brand-blue">{eng.progressPercent}%</span></div>
                <ProgressBar value={eng.progressPercent} />
                <ul className="mt-4 space-y-1.5 text-sm text-gray-600">
                  <li className="flex justify-between"><span>Documents submitted</span><span className="font-medium text-gray-800">{d.documents.length}</span></li>
                  <li className="flex justify-between"><span>Verified</span><span className="font-medium text-gray-800">{eng.verifiedCount} / {eng.documentsCount}</span></li>
                  <li className="flex justify-between"><span>Open requests</span><span className={`font-medium ${openRequests.length ? "text-status-warning" : "text-gray-800"}`}>{openRequests.length}</span></li>
                  <li className="flex justify-between"><span>Answers to review</span><span className={`font-medium ${eng.needsReview ? "text-brand-blue" : "text-gray-800"}`}>{eng.needsReview}</span></li>
                </ul>
              </Card>
              <Card className="p-5">
                <div className="flex items-center justify-between">
                  <p className="flex items-center gap-2 font-semibold text-gray-800"><ClipboardList className="h-4 w-4 text-brand-blue" /> Document checklist</p>
                  {canWork && <Button variant="secondary" className="px-3 py-1.5 text-xs" onClick={() => setChecklistOpen(true)}>{d.checklist.length ? "Edit" : "Publish"}</Button>}
                </div>
                {d.checklist.length === 0 ? (
                  <p className="mt-3 text-xs text-gray-400">Not published yet. The client sees this list on their Documents page.</p>
                ) : (
                  <>
                    <p className="mt-2 text-xs text-gray-500">{provided} / {d.checklist.length} provided</p>
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
                <p className="font-semibold text-gray-800">Submitted pack</p>
                <p className="text-xs text-gray-500">Documents the client sent with the handover. Verify each one or flag it for the client to re-check.</p>
              </div>
              {d.documents.length === 0 ? <p className="px-5 py-8 text-center text-sm text-gray-400">{eng.status === "active" ? "The client has not submitted their pack yet." : "No documents."}</p> : (
                <div className="divide-y divide-gray-50">
                  {d.documents.map((doc) => (
                    <div key={doc.id} className="flex items-center gap-3 px-5 py-3">
                      <FileText className="h-4 w-4 shrink-0 text-gray-400" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-800">{doc.name}</p>
                        <p className="text-[11px] text-gray-400">{doc.docType} · {fileSize(doc.sizeBytes)} · {date(doc.createdAt)}</p>
                      </div>
                      <DocumentStatusBadge status={doc.status} />
                      <a href={`/api/documents/${doc.id}/file`} title="Download" className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700"><Download className="h-4 w-4" /></a>
                      {canWork && doc.status !== "verified" && <button disabled={busy} title="Verify" onClick={() => run(() => verifyDocument(doc.id), `${doc.name} verified.`)} className="rounded-lg p-1.5 text-emerald-600 hover:bg-emerald-50"><CheckCircle2 className="h-4 w-4" /></button>}
                      {canWork && doc.status !== "review_required" && <button disabled={busy} title="Flag for the client to re-check" onClick={() => run(() => flagDocument(doc.id), `${doc.name} flagged.`)} className="rounded-lg p-1.5 text-amber-600 hover:bg-amber-50"><Flag className="h-4 w-4" /></button>}
                    </div>
                  ))}
                </div>
              )}
            </Card>
            <Card className="overflow-hidden">
              <div className="border-b border-gray-100 px-5 py-3">
                <p className="font-semibold text-gray-800">Evidence from requests</p>
                <p className="text-xs text-gray-500">Files the client attached when answering your requests. They stay here after the request is resolved.</p>
              </div>
              {evidence.length === 0 ? <p className="px-5 py-8 text-center text-sm text-gray-400">No evidence files yet.</p> : (
                <div className="divide-y divide-gray-50">
                  {evidence.map((a) => (
                    <div key={a.id} className="flex items-center gap-3 px-5 py-3">
                      <Paperclip className="h-4 w-4 shrink-0 text-gray-400" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-800">{a.name}</p>
                        <p className="text-[11px] text-gray-400">{fileSize(a.sizeBytes)} · answers <span className="font-mono">{a.request.referenceCode}</span> {a.request.title}</p>
                      </div>
                      <Badge tone={a.request.status === "resolved" ? "success" : "info"}>{a.request.status === "resolved" ? "Resolved" : "Under review"}</Badge>
                      <a href={`/api/attachments/${a.id}/file`} title="Download" className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700"><Download className="h-4 w-4" /></a>
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
