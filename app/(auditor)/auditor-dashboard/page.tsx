import Link from "next/link";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import AuditorPriorityReviews from "@/components/auditor/AuditorPriorityReviews";
import AuditorRecentActivityCard from "@/components/auditor/AuditorRecentActivityCard";
import T from "@/components/layout/T";
import { apiServer } from "@/lib/api/server";
import type { AuditorDashboard } from "@/lib/types";

export default async function AuditorDashboardPage() {
  const data = await apiServer<AuditorDashboard>("/api/auditor/dashboard");
  const w = data.workload;

  return (
    <div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Tile title={<T k="auditor.dashboard.activeClients" />} sub={<T k="audpage.dashboard.activeClientsSub" />} value={data.companiesAssigned} href="/companies" cta={<T k="sidebar.companies" />} />
        <Tile title={<T k="auditor.dashboard.pendingReviewCount" />} sub={<T k="audpage.dashboard.pendingReviewSub" />} value={data.pendingReviews} valueClass="text-brand-blue" href="/companies?status=under_review" cta={<T k="audpage.dashboard.openCompanies" />} />
        <Tile title={<T k="common.completed" />} sub={<T k="audpage.dashboard.completedSub" />} value={data.completedThisPeriod} valueClass="text-status-success" href="/companies?status=approved" cta={<T k="common.viewAll" />} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
        <AuditorPriorityReviews reviews={data.priorityReviews} />
        <div className="flex flex-col gap-6">
          <Card className="p-5">
            <p className="mb-3 font-semibold text-gray-800">
              <T k="auditor.reviewQueue.queueTitle" />
            </p>
            <div className="space-y-2 text-sm">
              <Row label={<T k="audpage.dashboard.invitations" />} value={w.invited} href="/companies?status=invited" />
              <Row label={<T k="audpage.dashboard.waitingForPack" />} value={w.active} href="/companies?status=active" />
              <Row label={<T k="status.underReview" />} value={w.underReview} href="/companies?status=under_review" />
              <Row label={<T k="common.completed" />} value={w.approved} href="/companies?status=approved" />
              <Row label={<T k="audpage.dashboard.highPriorityOpen" />} value={data.highPriorityOpen} href="/requests" danger />
            </div>
          </Card>
          <AuditorRecentActivityCard activity={data.recentActivity} />
        </div>
      </div>
    </div>
  );
}

function Tile({ title, sub, value, valueClass = "text-gray-900", href, cta }: { title: React.ReactNode; sub: React.ReactNode; value: number; valueClass?: string; href: string; cta: React.ReactNode }) {
  return (
    <Card className="p-5">
      <p className="font-semibold text-gray-800">{title}</p>
      <p className="mt-1 text-sm text-gray-400">{sub}</p>
      <p className={`mt-3 text-3xl font-bold ${valueClass}`}>{value}</p>
      <Link href={href}>
        <Button variant="secondary" className="mt-4 w-full">{cta}</Button>
      </Link>
    </Card>
  );
}

function Row({ label, value, href, danger }: { label: React.ReactNode; value: number; href: string; danger?: boolean }) {
  return (
    <Link href={href} className="flex items-center justify-between rounded-md px-1 py-0.5 hover:bg-gray-50">
      <span className="text-gray-600">{label}</span>
      <span className={`font-semibold ${danger && value ? "text-status-critical" : "text-gray-800"}`}>{value}</span>
    </Link>
  );
}
