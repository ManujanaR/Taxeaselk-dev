import DocumentsManager from "@/components/business/DocumentsManager";
import SubmitToAuditorButton from "@/components/business/SubmitToAuditorButton";
import T from "@/components/layout/T";
import { apiServer } from "@/lib/api/server";
import type { DashboardView, DocumentsView } from "@/lib/types";

export default async function DocumentsPage() {
  const [data, dash] = await Promise.all([apiServer<DocumentsView>("/api/documents"), apiServer<DashboardView>("/api/dashboard")]);

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            <T k="pages.documents.title" />
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            <T k="pages.documents.subtitle" />
          </p>
        </div>
        <SubmitToAuditorButton auditorStatus={dash.auditorStatus} hasFigures={dash.accountingProfit !== null} missingCount={data.missingCount} />
      </div>
      <DocumentsManager data={data} />
    </div>
  );
}
