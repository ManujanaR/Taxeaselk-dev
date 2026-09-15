import { api } from "./client";
import type { AuditLogEntry, AuditorDashboard, AuditorProfileFull, ChecklistItem, ChecklistPreset, EngagementDetail, EngagementRow, EngagementStatus, RequestRow, StatutoryDocument } from "@/lib/types";

export const getAuditorDashboard = () => api<AuditorDashboard>("/api/auditor/dashboard");
export const getAuditorProfile = () => api<AuditorProfileFull>("/api/auditor/profile");
export const updateAuditorProfile = (payload: Omit<AuditorProfileFull, "id" | "email">) => api<AuditorProfileFull>("/api/auditor/profile", { method: "PUT", json: payload });

export const getEngagements = (status?: EngagementStatus) => api<EngagementRow[]>(`/api/auditor/engagements${status ? `?status=${status}` : ""}`);
export const getEngagementDetail = (id: string) => api<EngagementDetail>(`/api/auditor/engagements/${id}`);
export const acceptEngagement = (id: string) => api<EngagementRow>(`/api/auditor/engagements/${id}/accept`, { method: "POST" });
export const declineEngagement = (id: string) => api<EngagementRow>(`/api/auditor/engagements/${id}/decline`, { method: "POST" });
export const approveEngagement = (id: string) => api<EngagementRow>(`/api/auditor/engagements/${id}/approve`, { method: "POST" });

export const getChecklistPresets = () => api<ChecklistPreset[]>("/api/auditor/checklist-presets");
export const publishChecklist = (engagementId: string, items: ChecklistPreset["items"]) =>
  api<ChecklistItem[]>(`/api/auditor/engagements/${engagementId}/checklist`, { method: "PUT", json: { items } });
export const verifyDocument = (id: string) => api<StatutoryDocument>(`/api/auditor/documents/${id}/verify`, { method: "POST" });
export const flagDocument = (id: string) => api<StatutoryDocument>(`/api/auditor/documents/${id}/flag`, { method: "POST" });

export type NewRequest = { title: string; description: string; category: string; priority: string; dueDate: string | null };
export const getAuditorRequests = () => api<RequestRow[]>("/api/auditor/requests");
export const createRequest = (engagementId: string, payload: NewRequest) => api<RequestRow>(`/api/auditor/engagements/${engagementId}/requests`, { method: "POST", json: payload });
export const remindRequest = (id: string) => api<void>(`/api/auditor/requests/${id}/remind`, { method: "POST" });
export const resolveRequest = (id: string) => api<RequestRow>(`/api/auditor/requests/${id}/resolve`, { method: "POST" });
export const requestRevision = (id: string, note: string) => api<RequestRow>(`/api/auditor/requests/${id}/revision`, { method: "POST", json: { note } });
export const dismissRequest = (id: string) => api<RequestRow>(`/api/auditor/requests/${id}/dismiss`, { method: "POST" });

export const getAuditLog = (companyId?: string) => api<AuditLogEntry[]>(`/api/auditor/audit-log${companyId ? `?companyId=${companyId}` : ""}`);
