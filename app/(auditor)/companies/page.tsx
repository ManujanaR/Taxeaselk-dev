import CompaniesManager from "@/components/auditor/CompaniesManager";
import { apiServer } from "@/lib/api/server";
import type { EngagementRow } from "@/lib/types";

export default async function CompaniesPage({ searchParams }: { searchParams: { status?: string; engagementId?: string } }) {
  const engagements = await apiServer<EngagementRow[]>("/api/auditor/engagements");
  const invitations = await apiServer<EngagementRow[]>("/api/auditor/engagements?status=invited");
  const all = [...invitations.filter((i) => !engagements.some((e) => e.id === i.id)), ...engagements];
  return <CompaniesManager engagements={all} initialStatus={searchParams.status} openEngagementId={searchParams.engagementId} />;
}
