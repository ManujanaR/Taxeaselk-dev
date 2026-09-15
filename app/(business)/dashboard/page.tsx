import Link from "next/link";
import { Upload, FileBarChart, AlertTriangle, CheckCircle2, UserCheck } from "lucide-react";
import Card from "@/components/ui/Card";
import StatCard from "@/components/ui/StatCard";
import Button from "@/components/ui/Button";
import T from "@/components/layout/T";
import DashboardPipelineProgress from "@/components/business/DashboardPipelineProgress";
import { apiServer } from "@/lib/api/server";
import { getSession } from "@/lib/auth";
import { lkr } from "@/lib/format";
import type { DashboardView } from "@/lib/types";
import type { TranslationKey } from "@/lib/i18n/translations";

const AUDITOR_LABEL: Record<DashboardView["auditorStatus"], TranslationKey> = {
  none: "bizpage.dashboard.auditorNotAppointed",
  invited: "bizpage.dashboard.auditorInvitationPending",
  active: "bizpage.dashboard.auditorWaitingSubmission",
  under_review: "status.underReview",
  approved: "status.approved",
  declined: "bizpage.dashboard.auditorInvitationDeclined",
  terminated: "bizpage.dashboard.auditorNotAppointed",
};

export default async function DashboardPage() {
  const [session, data] = await Promise.all([getSession("business"), apiServer<DashboardView>("/api/dashboard")]);
  const company = session.company!;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">
        <T k="pages.dashboard.title" />
      </h1>
      <p className="mt-1 text-sm text-gray-500">
        <T k="bizpage.dashboard.subtitle" params={{ year: company.financialYear, company: company.companyName }} />
      </p>

      <DashboardPipelineProgress data={data} />

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label={<T k="business.dashboard.documents" />}
          value={`${data.documentsUploaded} / ${data.documentsRequired}`}
          hint={data.documentsUploaded >= data.documentsRequired ? <span className="font-medium text-emerald-600"><T k="bizpage.dashboard.allDocsGathered" /></span> : <T k="business.dashboard.pendingUpload" params={{ count: Math.max(0, data.documentsRequired - data.documentsUploaded) }} />}
        />
        <StatCard
          label={<T k="business.dashboard.accountingProfit" />}
          value={data.accountingProfit === null ? "—" : lkr(data.accountingProfit)}
          hint={data.accountingProfit === null ? <Link href="/financials" className="text-brand-blue hover:underline"><T k="bizpage.dashboard.enterFigures" /></Link> : <T k="bizpage.dashboard.indicativeCit" params={{ amount: lkr(data.citLiability, { compact: true }) }} />}
        />
        <StatCard
          label={<T k="business.dashboard.auditorStatus" />}
          value={<T k={AUDITOR_LABEL[data.auditorStatus]} />}
          hint={data.auditorFirm ? `${data.auditorName} · ${data.auditorFirm}` : <Link href="/auditor-review" className="text-brand-blue hover:underline"><T k="bizpage.dashboard.inviteAnAuditor" /></Link>}
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[320px_1fr]">
        <Card className="p-5">
          <p className="mb-4 font-semibold text-gray-800">
            <T k="business.dashboard.quickActions" />
          </p>
          <div className="flex flex-col gap-2.5">
            <Link href="/documents">
              <Button icon={<Upload className="h-4 w-4" />} className="w-full justify-start">
                <T k="business.dashboard.uploadDocuments" />
              </Button>
            </Link>
            <Link href="/financials">
              <Button variant="secondary" icon={<FileBarChart className="h-4 w-4" />} className="w-full justify-start">
                <T k="business.dashboard.viewFinancials" />
              </Button>
            </Link>
            <Link href="/auditor-review">
              <Button variant="secondary" icon={<UserCheck className="h-4 w-4" />} className="w-full justify-start">
                <T k="sidebar.auditorReview" />
              </Button>
            </Link>
          </div>
        </Card>

        <Card className="p-5">
          <p className="mb-4 font-semibold text-gray-800">
            <T k="business.dashboard.requiresAttention" />
          </p>
          <div className="flex flex-col gap-3">
            {data.attentionItems.length === 0 ? (
              <div className="flex items-center gap-3 rounded-lg border border-emerald-100 bg-emerald-50/60 p-4">
                <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600" />
                <div>
                  <p className="text-sm font-semibold text-emerald-900"><T k="bizpage.dashboard.allCaughtUpTitle" /></p>
                  <p className="mt-0.5 text-xs text-emerald-700/80"><T k="bizpage.dashboard.allCaughtUpSubtitle" /></p>
                </div>
              </div>
            ) : (
              data.attentionItems.map((item) => {
                const critical = item.severity === "critical";
                return (
                  <div key={item.id} className={`rounded-lg border p-3 ${critical ? "border-red-100 bg-red-50" : "border-amber-100 bg-amber-50"}`}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-2">
                        <AlertTriangle className={`mt-0.5 h-4 w-4 shrink-0 ${critical ? "text-status-critical" : "text-status-warning"}`} />
                        <div>
                          <p className={`text-sm font-semibold ${critical ? "text-status-critical" : "text-status-warning"}`}>{item.title}</p>
                          <p className="mt-0.5 text-xs text-gray-500">{item.description}</p>
                        </div>
                      </div>
                      <Link href={item.link} className="shrink-0 whitespace-nowrap text-xs font-medium text-brand-blue hover:underline">
                        <T k="business.dashboard.reviewLink" />
                      </Link>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
