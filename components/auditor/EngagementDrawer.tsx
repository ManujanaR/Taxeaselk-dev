"use client";

import { useCallback, useEffect, useState } from "react";
import { X, FileText, Download, CheckCircle2, Flag, ClipboardList, AlertTriangle, Inbox, ShieldCheck, Bell } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { Field, Input, Select } from "@/components/ui/Input";
import DocumentStatusBadge from "@/components/business/DocumentStatusBadge";
import EngagementStatusBadge from "./EngagementStatusBadge";
import AuditorChecklistModal from "./AuditorChecklistModal";
import { approveEngagement, createRequest, flagDocument, getEngagementDetail, raiseIssue, remindRequest, resolveIssue, verifyDocument } from "@/lib/api/auditor";
import { date, fileSize } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import type { EngagementDetail } from "@/lib/types";

type Tab = "documents" | "issues" | "requests" | "company";

// Everything the auditor does for one client, in one place.
export default function EngagementDrawer({ engagementId, onClose, initialTab = "documents" }: { engagementId: string; onClose: () => void; initialTab?: Tab }) {
  const [d, setD] = useState<EngagementDetail | null>(null);
  const [tab, setTab] = useState<Tab>(initialTab);
  const [checklistOpen, setChecklistOpen] = useState(false);
  const [issueForm, setIssueForm] = useState<{ title: string; comment: string; source: string; severity: "warning" | "critical" } | null>(null);
  const [reqForm, setReqForm] = useState<{ title: string; description: string; category: string; priority: string; dueDate: string } | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setD(await getEngagementDetail(engagementId));
    } catch (e) {
      toast.error(errorMessage(e));
      onClose();
    }
  }, [engagementId, onClose]);

  useEffect(() => {
    load();
  }, [load]);

  async function run(fn: () => Promise<unknown>, ok: string) {
    setBusy(true);
    try {
      await fn();
      toast.success(ok);
      await load();
      return true;
    } catch (e) {
      toast.error(errorMessage(e));
      return false;
    } finally {
      setBusy(false);
    }
  }

  const eng = d?.engagement;
  const canWork = eng && (eng.status === "active" || eng.status === "under_review");
  const openItems = d ? d.issues.filter((i) => i.status !== "resolved").length + d.requests.filter((r) => r.status !== "resolved").length : 0;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40">
      <div className="flex h-full w-full max-w-3xl flex-col bg-white shadow-2xl">
        <div className="flex items-start justify-between border-b border-gray-100 px-6 py-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-gray-900">{eng?.companyName ?? "Loading..."}</h2>
              {eng && <EngagementStatusBadge status={eng.status} />}
            </div>
            {eng && <p className="text-xs text-gray-500">Tax year {eng.taxYear} · TIN {eng.tinNumber || "—"} · Pack {eng.progressPercent}% · {eng.submittedAt ? `Submitted ${date(eng.submittedAt)}` : "Pack not submitted"}</p>}
          </div>
          <div className="flex items-center gap-2">
            {eng?.status === "under_review" && (
              <Button variant="success" icon={<ShieldCheck className="h-4 w-4" />} disabled={busy || openItems > 0} title={openItems ? `${openItems} open item(s) must be resolved first` : undefined}
                onClick={() => confirm(`Sign off the CIT return for ${eng.companyName} (${eng.taxYear})? This is final.`) && run(() => approveEngagement(eng.id), "Audit signed off.")}>
                Approve & Sign Off
              </Button>
            )}
            <button onClick={onClose} className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"><X className="h-5 w-5" /></button>
          </div>
        </div>

        <div className="flex gap-1 border-b border-gray-100 px-6">
          {([["documents", "Documents", d?.documents.length], ["issues", "Issues", d?.issues.filter((i) => i.status !== "resolved").length], ["requests", "RFIs", d?.requests.filter((r) => r.status !== "resolved").length], ["company", "Company", undefined]] as const).map(([id, label, n]) => (
            <button key={id} onClick={() => setTab(id)} className={`border-b-2 px-3 py-2.5 text-sm font-medium ${tab === id ? "border-brand-blue text-brand-blue" : "border-transparent text-gray-500 hover:text-gray-700"}`}>
              {label}{n ? <span className="ml-1.5 rounded-full bg-gray-100 px-1.5 text-[10px] font-bold text-gray-600">{n}</span> : null}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {!d ? <p className="text-sm text-gray-400">Loading…</p> : tab === "documents" ? (
            <>
              <div className="mb-4 flex items-center justify-between">
                <p className="flex items-center gap-2 text-sm font-semibold text-gray-800"><ClipboardList className="h-4 w-4 text-brand-blue" /> Checklist: {d.checklist.filter((c) => c.providedDocumentId).length} / {d.checklist.length} provided</p>
                {canWork && <Button variant="secondary" className="px-3 py-1.5 text-xs" onClick={() => setChecklistOpen(true)}>{d.checklist.length ? "Edit Checklist" : "Publish Checklist"}</Button>}
              </div>
              {d.checklist.length > 0 && (
                <ul className="mb-5 grid grid-cols-1 gap-1 sm:grid-cols-2">
                  {d.checklist.map((c) => (
                    <li key={c.id} className="flex items-center gap-2 text-xs text-gray-600">
                      {c.providedDocumentId ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : <span className="h-3.5 w-3.5 rounded-full border border-gray-300" />}
                      <span className={c.providedDocumentId ? "line-through" : ""}>{c.name}</span>
                    </li>
                  ))}
                </ul>
              )}
              {d.documents.length === 0 ? <p className="py-6 text-center text-sm text-gray-400">The client has not uploaded any documents yet.</p> : (
                <div className="divide-y divide-gray-50 rounded-lg border border-gray-100">
                  {d.documents.map((doc) => (
                    <div key={doc.id} className="flex items-center gap-3 px-3 py-2.5">
                      <FileText className="h-4 w-4 shrink-0 text-gray-400" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-800">{doc.name}</p>
                        <p className="text-[11px] text-gray-400">{doc.docType} · {fileSize(doc.sizeBytes)} · {date(doc.createdAt)}</p>
                      </div>
                      <DocumentStatusBadge status={doc.status} />
                      <a href={`/api/documents/${doc.id}/file`} title="Download" className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-700"><Download className="h-4 w-4" /></a>
                      {canWork && doc.status !== "verified" && <button disabled={busy} title="Verify" onClick={() => run(() => verifyDocument(doc.id), `${doc.name} verified.`)} className="rounded-lg p-1.5 text-emerald-600 hover:bg-emerald-50"><CheckCircle2 className="h-4 w-4" /></button>}
                      {canWork && doc.status !== "review_required" && <button disabled={busy} title="Flag for review" onClick={() => run(() => flagDocument(doc.id), `${doc.name} flagged.`)} className="rounded-lg p-1.5 text-amber-600 hover:bg-amber-50"><Flag className="h-4 w-4" /></button>}
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : tab === "issues" ? (
            <>
              <div className="mb-4 flex items-center justify-between">
                <p className="text-sm font-semibold text-gray-800">Issues raised during inspection</p>
                {canWork && !issueForm && <Button className="px-3 py-1.5 text-xs" icon={<AlertTriangle className="h-3.5 w-3.5" />} onClick={() => setIssueForm({ title: "", comment: "", source: "", severity: "warning" })}>Raise Issue</Button>}
              </div>
              {issueForm && (
                <Card className="mb-4 space-y-3 border-brand-blue/30 p-4">
                  <Field label="Title" required><Input value={issueForm.title} onChange={(e) => setIssueForm({ ...issueForm, title: e.target.value })} placeholder="e.g. Entertainment expenses not added back" /></Field>
                  <Field label="Auditor comment"><textarea rows={3} value={issueForm.comment} onChange={(e) => setIssueForm({ ...issueForm, comment: e.target.value })} className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none" /></Field>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Source"><Input value={issueForm.source} onChange={(e) => setIssueForm({ ...issueForm, source: e.target.value })} placeholder="Ledger account / document" /></Field>
                    <Field label="Severity"><Select value={issueForm.severity} onChange={(e) => setIssueForm({ ...issueForm, severity: e.target.value as "warning" | "critical" })}><option value="warning">Warning</option><option value="critical">Critical</option></Select></Field>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button variant="secondary" className="text-xs" onClick={() => setIssueForm(null)}>Cancel</Button>
                    <Button className="text-xs" disabled={busy || !issueForm.title.trim()} onClick={async () => (await run(() => raiseIssue(engagementId, issueForm), "Issue raised; client notified.")) && setIssueForm(null)}>Raise Issue</Button>
                  </div>
                </Card>
              )}
              {d.issues.length === 0 ? <p className="py-6 text-center text-sm text-gray-400">No issues raised.</p> : d.issues.map((i) => (
                <div key={i.id} className="border-b border-gray-50 py-3">
                  <div className="flex items-start gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-medium text-gray-800">{i.title}</p>
                        <Badge tone={i.severity === "critical" ? "critical" : "warning"}>{i.severity}</Badge>
                        <Badge tone={i.status === "resolved" ? "success" : i.status === "pending_clarification" ? "info" : "critical"}>{i.status === "pending_clarification" ? "Client responded" : i.status.replace("_", " ")}</Badge>
                      </div>
                      {i.comment && <p className="mt-1 text-sm text-gray-600">{i.comment}</p>}
                      {i.responseText && (
                        <div className="mt-2 rounded-lg bg-gray-50 p-2.5 text-xs text-gray-700">
                          <span className="font-semibold">Client:</span> {i.responseText}
                          {i.attachments.map((a) => <a key={a.id} href={`/api/attachments/${a.id}/file`} className="ml-2 text-brand-blue hover:underline">{a.name}</a>)}
                        </div>
                      )}
                    </div>
                    {canWork && i.status !== "resolved" && <Button variant="success" className="px-2.5 py-1.5 text-xs" disabled={busy} onClick={() => run(() => resolveIssue(i.id), "Issue resolved.")}>Resolve</Button>}
                  </div>
                </div>
              ))}
            </>
          ) : tab === "requests" ? (
            <>
              <div className="mb-4 flex items-center justify-between">
                <p className="text-sm font-semibold text-gray-800">Requests for Information</p>
                {canWork && !reqForm && <Button className="px-3 py-1.5 text-xs" icon={<Inbox className="h-3.5 w-3.5" />} onClick={() => setReqForm({ title: "", description: "", category: "Financial Statements", priority: "MEDIUM", dueDate: "" })}>New Request</Button>}
              </div>
              {reqForm && (
                <Card className="mb-4 space-y-3 border-brand-blue/30 p-4">
                  <Field label="Title" required><Input value={reqForm.title} onChange={(e) => setReqForm({ ...reqForm, title: e.target.value })} placeholder="e.g. Bank confirmation letters" /></Field>
                  <Field label="Instructions"><textarea rows={3} value={reqForm.description} onChange={(e) => setReqForm({ ...reqForm, description: e.target.value })} className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-brand-blue focus:outline-none" /></Field>
                  <div className="grid grid-cols-3 gap-3">
                    <Field label="Category"><Select value={reqForm.category} onChange={(e) => setReqForm({ ...reqForm, category: e.target.value })}>{["Financial Statements", "Fixed Assets", "Tax Reliefs", "Bank & Cash", "General Inquiry"].map((c) => <option key={c}>{c}</option>)}</Select></Field>
                    <Field label="Priority"><Select value={reqForm.priority} onChange={(e) => setReqForm({ ...reqForm, priority: e.target.value })}><option>HIGH</option><option>MEDIUM</option><option>LOW</option></Select></Field>
                    <Field label="Due date"><Input type="date" value={reqForm.dueDate} onChange={(e) => setReqForm({ ...reqForm, dueDate: e.target.value })} /></Field>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button variant="secondary" className="text-xs" onClick={() => setReqForm(null)}>Cancel</Button>
                    <Button className="text-xs" disabled={busy || !reqForm.title.trim()} onClick={async () => (await run(() => createRequest(engagementId, { ...reqForm, dueDate: reqForm.dueDate || null }), "Request sent; client notified.")) && setReqForm(null)}>Send Request</Button>
                  </div>
                </Card>
              )}
              {d.requests.length === 0 ? <p className="py-6 text-center text-sm text-gray-400">No requests issued.</p> : d.requests.map((r) => (
                <div key={r.id} className="flex items-start gap-3 border-b border-gray-50 py-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs text-gray-400">{r.referenceCode}</span>
                      <p className="font-medium text-gray-800">{r.title}</p>
                      <Badge tone={r.priority === "HIGH" ? "critical" : r.priority === "MEDIUM" ? "warning" : "info"}>{r.priority}</Badge>
                      <Badge tone={r.status === "resolved" ? "success" : r.status === "responded" ? "info" : r.status === "revision_requested" ? "critical" : "pending"}>{r.status.replace("_", " ")}</Badge>
                    </div>
                    <p className="mt-0.5 text-[11px] text-gray-400">{r.category}{r.dueDate ? ` · Due ${date(r.dueDate)}` : ""}</p>
                    {r.response && <p className="mt-1 text-xs text-gray-600"><span className="font-semibold">Client:</span> {r.response.note} {r.response.attachments.length > 0 && <span className="text-gray-400">· {r.response.attachments.length} file(s) — review on the Responses page</span>}</p>}
                  </div>
                  {canWork && (r.status === "pending" || r.status === "revision_requested") && <Button variant="secondary" className="px-2.5 py-1.5 text-xs" icon={<Bell className="h-3.5 w-3.5" />} disabled={busy} onClick={() => run(() => remindRequest(r.id), "Reminder sent.")}>Remind</Button>}
                </div>
              ))}
            </>
          ) : (
            <dl className="grid grid-cols-1 gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
              {([["Legal name", d.company.companyName], ["Trading name", d.company.tradingName], ["Registration no.", d.company.registrationNumber], ["TIN", d.company.tinNumber], ["VAT", d.company.vatNumber], ["SVAT", d.company.isSvatRegistered ? d.company.svatNumber || "Registered" : "Not registered"], ["CIT rate", d.company.citTaxRateCategory === "sme_14" ? "14% concessionary" : "30% standard"], ["Financial year", d.company.financialYear], ["Sector", d.company.industrySector], ["Contact", `${d.company.contactEmail} ${d.company.contactPhone}`.trim()], ["Registered address", d.company.registeredAddress]] as [string, string][]).map(([k, v]) => (
                <div key={k}><dt className="text-[11px] uppercase tracking-wider text-gray-400">{k}</dt><dd className="font-medium text-gray-800">{v || "—"}</dd></div>
              ))}
            </dl>
          )}
        </div>
      </div>

      {checklistOpen && d && <AuditorChecklistModal engagementId={engagementId} companyName={d.engagement.companyName} existing={d.checklist} onClose={() => setChecklistOpen(false)} onPublished={() => { setChecklistOpen(false); load(); }} />}
    </div>
  );
}
