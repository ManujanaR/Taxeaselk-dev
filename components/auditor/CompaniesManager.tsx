"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Building2, Search, Check, X, Mail } from "lucide-react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import ProgressBar from "@/components/ui/ProgressBar";
import EngagementStatusBadge from "./EngagementStatusBadge";
import { acceptEngagement, declineEngagement } from "@/lib/api/auditor";
import { date } from "@/lib/format";
import { errorMessage, toast } from "@/lib/toast";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import type { TranslationKey } from "@/lib/i18n/translations";
import type { EngagementRow } from "@/lib/types";

const TABS: { id: string; key: TranslationKey }[] = [
  { id: "all", key: "common.all" },
  { id: "invited", key: "audcomp.tabs.invitations" },
  { id: "active", key: "audcomp.tabs.waitingForPack" },
  { id: "under_review", key: "status.underReview" },
  { id: "approved", key: "status.approved" },
];

export default function CompaniesManager({ engagements, initialStatus }: { engagements: EngagementRow[]; initialStatus?: string }) {
  const router = useRouter();
  const { t } = useLanguage();
  const [tab, setTab] = useState(initialStatus && TABS.some((tb) => tb.id === initialStatus) ? initialStatus : "all");
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState<string | null>(null);

  const rows = engagements.filter((e) => (tab === "all" ? e.status !== "invited" : e.status === tab) && (e.companyName + e.tinNumber).toLowerCase().includes(query.toLowerCase()));
  const invitations = engagements.filter((e) => e.status === "invited").length;

  async function respond(id: string, accept: boolean) {
    setBusy(id);
    try {
      await (accept ? acceptEngagement(id) : declineEngagement(id));
      toast.success(accept ? t("audcomp.toast.engagementAccepted") : t("audcomp.toast.invitationDeclined"));
      router.refresh();
      if (accept) router.push(`/companies/${id}`);
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
          <h1 className="text-2xl font-bold text-gray-900">{t("audcomp.companies.title")}</h1>
          <p className="mt-1 text-sm text-gray-500">{t("audcomp.companies.subtitle")}</p>
        </div>
        {invitations > 0 && tab !== "invited" && (
          <Button variant="secondary" icon={<Mail className="h-4 w-4 text-amber-600" />} onClick={() => setTab("invited")}>
            {invitations > 1 ? t("audcomp.companies.newInvitationsPlural", { count: invitations }) : t("audcomp.companies.newInvitationSingular", { count: invitations })}
          </Button>
        )}
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-2">
        {TABS.map((tabItem) => (
          <button key={tabItem.id} onClick={() => setTab(tabItem.id)} className={`rounded-full px-3 py-1 text-xs font-semibold ${tab === tabItem.id ? "bg-brand-blue text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>
            {t(tabItem.key)}
            {tabItem.id === "invited" && invitations > 0 && <span className="ml-1 rounded-full bg-white/30 px-1.5">{invitations}</span>}
          </button>
        ))}
        <div className="relative ml-auto">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("audcomp.companies.searchPlaceholder")} className="w-64 rounded-lg border border-gray-200 py-2 pl-8 pr-3 text-sm focus:border-brand-blue focus:outline-none" />
        </div>
      </div>

      <Card className="mt-4 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <tr>
              <th className="px-4 py-3">{t("common.company")}</th>
              <th className="px-4 py-3">{t("audcomp.table.tin")}</th>
              <th className="px-4 py-3">{t("audcomp.table.taxYear")}</th>
              <th className="px-4 py-3">{t("common.status")}</th>
              <th className="px-4 py-3">{t("audcomp.table.requests")}</th>
              <th className="px-4 py-3">{t("audcomp.table.documents")}</th>
              <th className="px-4 py-3">{t("audcomp.table.progress")}</th>
              <th className="px-4 py-3 text-right">{t("common.actions")}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {rows.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-10 text-center text-gray-400">{tab === "invited" ? t("audcomp.companies.noPendingInvitations") : t("audcomp.companies.noCompaniesInView")}</td>
              </tr>
            )}
            {rows.map((e) => (
              <tr key={e.id} className="hover:bg-gray-50/60">
                <td className="px-4 py-3">
                  {e.status === "invited" ? (
                    <span className="flex items-center gap-2 font-medium text-gray-800"><Building2 className="h-4 w-4 text-gray-400" /> {e.companyName}</span>
                  ) : (
                    <Link href={`/companies/${e.id}`} className="flex items-center gap-2 font-medium text-gray-800 hover:text-brand-blue">
                      <Building2 className="h-4 w-4 text-gray-400" /> {e.companyName}
                    </Link>
                  )}
                  {e.status === "invited" && e.message && <p className="mt-0.5 max-w-xs truncate text-xs text-gray-400">“{e.message}”</p>}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-gray-600">{e.tinNumber || "—"}</td>
                <td className="px-4 py-3 text-gray-600">{e.taxYear}</td>
                <td className="px-4 py-3"><EngagementStatusBadge status={e.status} /></td>
                <td className="px-4 py-3 text-sm">{e.openRequests === 0 ? <span className="font-medium text-status-success">{t("audcomp.companies.allClear")}</span> : <span>{e.needsReview > 0 && <span className="font-medium text-brand-blue">{t("audcomp.companies.toReview", { count: e.needsReview })}</span>}{e.needsReview > 0 && e.openRequests - e.needsReview > 0 && <span className="text-gray-300"> · </span>}{e.openRequests - e.needsReview > 0 && <span className="text-status-warning">{t("audcomp.companies.waitingCount", { count: e.openRequests - e.needsReview })}</span>}{e.highPriorityOpen > 0 && <span className="ml-1 rounded bg-red-50 px-1 text-[10px] font-bold text-red-700">{t("audcomp.companies.highBadge")}</span>}</span>}</td>
                <td className="px-4 py-3 text-gray-600">{t("audcomp.companies.verifiedProgress", { verified: e.verifiedCount, total: e.documentsCount })}</td>
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
                        <Button variant="success" className="px-2.5 py-1.5 text-xs" icon={<Check className="h-3.5 w-3.5" />} disabled={busy === e.id} onClick={() => respond(e.id, true)}>{t("audcomp.actions.accept")}</Button>
                        <Button variant="secondary" className="px-2.5 py-1.5 text-xs" icon={<X className="h-3.5 w-3.5" />} disabled={busy === e.id} onClick={() => respond(e.id, false)}>{t("audcomp.actions.decline")}</Button>
                      </>
                    ) : (
                      <Link href={`/companies/${e.id}`}><Button variant="secondary" className="px-3 py-1.5 text-xs">{t("audcomp.actions.open")}</Button></Link>
                    )}
                  </div>
                  {e.status === "invited" && <p className="mt-1 text-right text-[10px] text-gray-400">{t("audcomp.companies.invitedOn", { date: date(e.createdAt) })}</p>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

    </div>
  );
}
