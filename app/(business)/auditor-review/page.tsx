import Card from "@/components/ui/Card";
import SummaryCountRow from "@/components/business/SummaryCountRow";
import InviteAuditorButton from "@/components/business/InviteAuditorButton";
import AssignedAuditorCard from "@/components/business/AssignedAuditorCard";
import AuditorRequests from "@/components/business/AuditorRequests";
import T from "@/components/layout/T";
import { apiServer } from "@/lib/api/server";
import type { EngagementView, RfiRequest } from "@/lib/types";

// Assigned auditor + review summary, then the auditor's issues and RFIs to answer.
export default async function AuditorReviewPage() {
  const [view, requests] = await Promise.all([apiServer<EngagementView>("/api/engagement"), apiServer<RfiRequest[]>("/api/requests")]);
  const live = view.engagement && ["invited", "active", "under_review"].includes(view.engagement.status);

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            <T k="pages.auditorReview.title" />
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            <T k="pages.auditorReview.subtitle" />
          </p>
        </div>
        {!live && <InviteAuditorButton />}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_300px]">
        <AssignedAuditorCard view={view} />
        <Card className="p-5">
          <p className="mb-2 font-semibold text-gray-800">
            <T k="business.auditorReview.citStatus" />
          </p>
          <div className="divide-y divide-gray-50">
            <SummaryCountRow label={<T k="bizpage.auditorReview.waitingOnYou" />} count={view.openRequests} tone={view.openRequests ? "warning" : "success"} />
            <SummaryCountRow label={<T k="bizpage.auditorReview.awaitingAuditorReview" />} count={view.needsReviewCount} tone="info" />
            <SummaryCountRow label={<T k="bizpage.auditorReview.resolved" />} count={view.resolvedCount} tone="success" />
          </div>
        </Card>
      </div>

      <AuditorRequests requests={requests} />
    </div>
  );
}
