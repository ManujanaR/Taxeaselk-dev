import AuditorDocumentsManager from "@/components/auditor/AuditorDocumentsManager";
import { apiServer } from "@/lib/api/server";
import type { EngagementRow } from "@/lib/types";

export default async function AuditorDocumentsPage({ searchParams }: { searchParams: { engagementId?: string } }) {
  const engagements = await apiServer<EngagementRow[]>("/api/auditor/engagements");
  return <AuditorDocumentsManager engagements={engagements.filter((e) => e.status !== "invited")} openEngagementId={searchParams.engagementId} />;
}
