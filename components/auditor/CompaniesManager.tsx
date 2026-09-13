"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, Search, Check, X, Mail } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import ProgressBar from "@/components/ui/ProgressBar";
import EngagementStatusBadge from "./EngagementStatusBadge";
import IssueCountPair from "./IssueCountPair";
import EngagementDrawer from "./EngagementDrawer";
import { acceptEngagement, declineEngagement } from "@/lib/api/auditor";
import { date } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import type { EngagementRow } from "@/lib/types";

const TABS: { id: string; label: string }[] = [
  { id: "all", label: "All" },
  { id: "invited", label: "Invitations" },
  { id: "active", label: "Waiting for Pack" },
  { id: "under_review", label: "Under Review" },
  { id: "approved", label: "Approved" },
];

export default function CompaniesManager({ engagements, initialStatus, openEngagementId }: { engagements: EngagementRow[]; initialStatus?: string; openEngagementId?: string }) {
  const router = useRouter();
  const [tab, setTab] = useState(initialStatus && TABS.some((t) => t.id === initialStatus) ? initialStatus : "all");
  const [query, setQuery] = useState("");
  const [openId, setOpenId] = useState<string | null>(openEngagementId ?? null);
  const [busy, setBusy] = useState<string | null>(null);

  const rows = engagements.filter((e) => (tab === "all" ? e.status !== "invited" : e.status === tab) && (e.companyName + e.tinNumber).toLowerCase().includes(query.toLowerCase()));
  const invitations = engagements.filter((e) => e.status === "invited").length;

  async function respond(id: string, accept: boolean) {
    setBusy(id);
    try {
      await (accept ? acceptEngagement(id) : declineEngagement(id));
      toast.success(accept ? "Engagement accepted. Publish the document checklist next." : "Invitation declined.");
      router.refresh();
      if (accept) setOpenId(id);
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Companies</h1>
          <p className="mt-1 text-sm text-gray-500">Your client portfolio and pending engagement invitations.</p>
        </div>
        {invitations > 0 && tab !== "invited" && (
          <Button variant="secondary" icon={<Mail className="h-4 w-4 text-amber-600" />} onClick={() => setTab("invited")}>
            {invitations} New Invitation{invitations > 1 ? "s" : ""}
          </Button>
        )}
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-2">
        {TABS.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)} className={`rounded-full px-3 py-1 text-xs font-semibold ${tab === t.id ? "bg-brand-blue text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
            {t.label}
            {t.id === "invited" && invitations > 0 && <span className="ml-1 rounded-full bg-white/30 px-1.5">{invitations}</span>}
          </button>
        ))}
        <div className="relative ml-auto">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search company or TIN" className="w-64 rounded-lg border border-gray-200 py-2 pl-8 pr-3 text-sm focus:border-brand-blue focus:outline-none" />
        </div>
      </div>

      <Card className="mt-4 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th className="px-4 py-3">Company</th>
              <th className="px-4 py-3">TIN</th>
              <th className="px-4 py-3">Tax Year</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Issues</th>
              <th className="px-4 py-3">Documents</th>
              <th className="px-4 py-3">Progress</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {rows.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-10 text-center text-gray-400">{tab === "invited" ? "No pending invitations." : "No companies in this view."}</td>
              </tr>
            )}
            {rows.map((e) => (
              <tr key={e.id} className="hover:bg-gray-50/60">
                <td className="px-4 py-3">
                  <button onClick={() => e.status !== "invited" && setOpenId(e.id)} className="flex items-center gap-2 font-medium text-gray-800 hover:text-brand-blue">
                    <Building2 className="h-4 w-4 text-gray-400" /> {e.companyName}
                  </button>
                  {e.status === "invited" && e.message && <p className="mt-0.5 max-w-xs truncate text-xs text-gray-400">“{e.message}”</p>}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-gray-600">{e.tinNumber || "—"}</td>
                <td className="px-4 py-3 text-gray-600">{e.taxYear}</td>
                <td className="px-4 py-3"><EngagementStatusBadge status={e.status} /></td>
                <td className="px-4 py-3"><IssueCountPair critical={e.criticalCount} warnings={e.warningsCount} /></td>
                <td className="px-4 py-3 text-gray-600">{e.verifiedCount} / {e.documentsCount} verified</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-20"><ProgressBar value={e.progressPercent} /></div>
                    <span className="text-xs text-gray-500">{e.progressPercent}%</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-1.5">
                    {e.status === "invited" ? (
                      <>
                        <Button variant="success" className="px-2.5 py-1.5 text-xs" icon={<Check className="h-3.5 w-3.5" />} disabled={busy === e.id} onClick={() => respond(e.id, true)}>Accept</Button>
                        <Button variant="secondary" className="px-2.5 py-1.5 text-xs" icon={<X className="h-3.5 w-3.5" />} disabled={busy === e.id} onClick={() => respond(e.id, false)}>Decline</Button>
                      </>
                    ) : (
                      <Button variant="secondary" className="px-3 py-1.5 text-xs" onClick={() => setOpenId(e.id)}>Open</Button>
                    )}
                  </div>
                  {e.status === "invited" && <p className="mt-1 text-right text-[10px] text-gray-400">Invited {date(e.createdAt)}</p>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {openId && <EngagementDrawer engagementId={openId} onClose={() => { setOpenId(null); router.refresh(); }} />}
    </div>
  );
}
