import AuditorResponsesManager from "@/components/auditor/AuditorResponsesManager";
import { apiServer } from "@/lib/api/server";
import type { ResponseRow } from "@/lib/types";

export default async function ResponsesPage() {
  const responses = await apiServer<ResponseRow[]>("/api/auditor/responses");
  return <AuditorResponsesManager responses={responses} />;
}
