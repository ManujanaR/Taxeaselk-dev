import RequestsManager from "@/components/auditor/RequestsManager";
import { apiServer } from "@/lib/api/server";
import type { EngagementRow, RequestRow } from "@/lib/types";

export default async function RequestsPage({ searchParams }: { searchParams: { status?: string; company?: string } }) {
  const [requests, engagements] = await Promise.all([apiServer<RequestRow[]>("/api/auditor/requests"), apiServer<EngagementRow[]>("/api/auditor/engagements")]);
  return <RequestsManager requests={requests} engagements={engagements.filter((e) => e.status === "active" || e.status === "under_review")} initialStatus={searchParams.status} companyFilter={searchParams.company} />;
}
