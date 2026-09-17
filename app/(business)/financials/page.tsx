import FinancialsView from "@/components/business/FinancialsView";
import { apiServer } from "@/lib/api/server";
import type { Company, DocumentsView, FinancialsView as FinancialsData } from "@/lib/types";

export default async function FinancialsPage() {
  const [data, docs, company] = await Promise.all([
    apiServer<FinancialsData>("/api/financials"),
    apiServer<DocumentsView>("/api/documents"),
    apiServer<Company>("/api/company"),
  ]);
  return <FinancialsView data={data} documents={docs.documents} company={company} />;
}
