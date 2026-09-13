import CompanyWorkspace from "@/components/auditor/CompanyWorkspace";
import { apiServer } from "@/lib/api/server";
import type { EngagementDetail } from "@/lib/types";

// One client, one place: overview, submitted documents, requests.
export default async function CompanyPage({ params, searchParams }: { params: { id: string }; searchParams: { tab?: string } }) {
  const detail = await apiServer<EngagementDetail>(`/api/auditor/engagements/${params.id}`);
  return <CompanyWorkspace detail={detail} initialTab={searchParams.tab} />;
}
