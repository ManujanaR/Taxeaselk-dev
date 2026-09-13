import FinancialsView from "@/components/business/FinancialsView";
import { apiServer } from "@/lib/api/server";
import type { DocumentsView, FinancialsView as FinancialsData } from "@/lib/types";

export default async function FinancialsPage() {
  const [data, docs] = await Promise.all([apiServer<FinancialsData>("/api/financials"), apiServer<DocumentsView>("/api/documents")]);
  return <FinancialsView data={data} documents={docs.documents} />;
}
