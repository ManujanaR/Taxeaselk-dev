import { api } from "./client";
import type { Company, DocumentsView, EngagementView, ExtractResult, FinancialInputs, FinancialsView, Review, RfiRequest, RfiResponse, StatutoryDocument, Engagement } from "@/lib/types";

export const getCompany = () => api<Company>("/api/company");
export const updateCompany = (payload: Omit<Company, "id">) => api<Company>("/api/company", { method: "PUT", json: payload });

export const getEngagement = () => api<EngagementView>("/api/engagement");
export const inviteAuditor = (payload: { auditorEmail: string; taxYear: string; message?: string }) =>
  api<Engagement>("/api/engagement/invite", { method: "POST", json: payload });
export const cancelEngagement = () => api<void>("/api/engagement/cancel", { method: "POST" });
export const rateAuditor = (payload: Omit<Review, "id" | "createdAt">) => api<Review>("/api/engagement/review", { method: "POST", json: payload });

export const getDocuments = () => api<DocumentsView>("/api/documents");
export const uploadDocument = (file: File, docType: string, checklistItemId?: string) => {
  const body = new FormData();
  body.append("file", file);
  body.append("docType", docType);
  if (checklistItemId) body.append("checklistItemId", checklistItemId);
  return api<StatutoryDocument>("/api/documents", { method: "POST", body });
};
export const deleteDocument = (id: string) => api<void>(`/api/documents/${id}`, { method: "DELETE" });

export const getFinancials = () => api<FinancialsView>("/api/financials");
export const saveFinancials = (payload: FinancialInputs) => api<FinancialsView>("/api/financials", { method: "PUT", json: payload });
export const extractFinancials = (documentId: string) => api<ExtractResult>("/api/financials/extract", { method: "POST", json: { documentId } });
export const submitHandover = () => api<void>("/api/handover", { method: "POST" });

export const getRequests = () => api<RfiRequest[]>("/api/requests");
export const respondToRequest = (id: string, note: string, files: File[]) => {
  const body = new FormData();
  body.append("note", note);
  files.forEach((f) => body.append("attachments", f));
  return api<RfiResponse>(`/api/requests/${id}/respond`, { method: "POST", body });
};
