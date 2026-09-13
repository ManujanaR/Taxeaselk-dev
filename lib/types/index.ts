// Shared types. Every interface mirrors a backend Pydantic schema (camelCase, numbers, ISO dates).

export type Role = "business" | "auditor";

// --- Session (GET /api/auth/me) ---
export interface User {
  id: string;
  email: string;
  role: Role;
  fullName: string;
  createdAt: string;
}

export interface Company {
  id: string;
  companyName: string;
  tradingName: string;
  registrationNumber: string;
  tinNumber: string;
  vatNumber: string;
  isSvatRegistered: boolean;
  svatNumber: string;
  citTaxRateCategory: "standard_30" | "sme_14";
  financialYear: string;
  contactEmail: string;
  contactPhone: string;
  registeredAddress: string;
  industrySector: string;
}

export interface AuditorProfile {
  id: string;
  firmName: string;
  firmRegNo: string;
  licenseNumber: string;
  icaslMemberNo: string;
  irdPractitionerNo: string;
  phone: string;
  officeAddress: string;
}

export interface Session {
  user: User;
  company: Company | null;
  auditorProfile: AuditorProfile | null;
}

// =====================================================================
// v2 API types — mirror backend Pydantic schemas (camelCase, numbers, ISO dates)
// =====================================================================

export type EngagementStatus = "invited" | "declined" | "active" | "under_review" | "approved" | "terminated";

export interface Engagement {
  id: string;
  companyId: string;
  auditorId: string;
  taxYear: string;
  status: EngagementStatus;
  message: string;
  createdAt: string;
  acceptedAt: string | null;
  submittedAt: string | null;
  approvedAt: string | null;
}

export interface AuditorSummary {
  id: string;
  name: string;
  firm: string;
  email: string;
  averageRating: number | null;
  totalReviews: number;
}

export interface Review {
  id: string;
  rating: number;
  timeliness: number;
  communication: number;
  technical: number;
  comment: string;
  createdAt: string;
}

export interface Attachment {
  id: string;
  name: string;
  sizeBytes: number;
  contentType: string;
}

export type IssueSeverityV2 = "critical" | "warning";
export type IssueStatus = "action_required" | "pending_clarification" | "resolved";

export interface Issue {
  id: string;
  engagementId: string;
  title: string;
  comment: string;
  source: string;
  severity: IssueSeverityV2;
  status: IssueStatus;
  responseText: string;
  createdAt: string;
  resolvedAt: string | null;
  attachments: Attachment[];
}

export interface EngagementView {
  engagement: Engagement | null;
  auditor: AuditorSummary | null;
  issues: Issue[];
  approvedCount: number;
  warningsCount: number;
  criticalCount: number;
  pendingCount: number;
  review: Review | null;
}

export interface ChecklistItem {
  id: string;
  name: string;
  category: string;
  description: string;
  required: boolean;
  orderIndex: number;
  providedDocumentId: string | null;
}

export type DocStatus = "uploaded" | "verified" | "review_required";

export interface StatutoryDocument {
  id: string;
  name: string;
  docType: string;
  status: DocStatus;
  sizeBytes: number;
  contentType: string;
  checklistItemId: string | null;
  createdAt: string;
  verifiedAt: string | null;
}

export interface DocumentsView {
  uploadedCount: number;
  verifiedCount: number;
  reviewRequiredCount: number;
  missingCount: number;
  documents: StatutoryDocument[];
  checklist: { auditorName: string | null; auditorFirm: string | null; items: ChecklistItem[] };
}

export type RequestStatus = "pending" | "responded" | "resolved" | "revision_requested";
export type ResponseStatus = "unreviewed" | "resolved" | "revision_requested";

export interface RfiResponse {
  id: string;
  requestId: string;
  note: string;
  revisionNote: string;
  status: ResponseStatus;
  createdAt: string;
  attachments: Attachment[];
}

export interface RfiRequest {
  id: string;
  engagementId: string;
  referenceCode: string;
  title: string;
  description: string;
  category: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  dueDate: string | null;
  status: RequestStatus;
  createdAt: string;
  response: RfiResponse | null;
}

export interface RequestRow extends RfiRequest {
  companyName: string;
}

export interface ResponseRow extends RfiResponse {
  referenceCode: string;
  requestTitle: string;
  category: string;
  companyName: string;
  engagementId: string;
}

export interface EngagementRow extends Engagement {
  companyName: string;
  tinNumber: string;
  financialYear: string;
  criticalCount: number;
  warningsCount: number;
  openRequests: number;
  progressPercent: number;
  documentsCount: number;
  verifiedCount: number;
}

export interface EngagementDetail {
  engagement: EngagementRow;
  company: Company;
  documents: StatutoryDocument[];
  checklist: ChecklistItem[];
  issues: Issue[];
  requests: RfiRequest[];
}

export interface AuditLogEntry {
  id: string;
  companyId: string;
  companyName: string;
  actorName: string;
  actorRole: Role;
  eventType: string;
  details: string;
  tone: "success" | "warning" | "info";
  createdAt: string;
}

export interface AuditorDashboard {
  companiesAssigned: number;
  pendingReviews: number;
  criticalIssues: number;
  completedThisPeriod: number;
  priorityReviews: { engagementId: string; companyName: string; tag: "CRITICAL" | "READY" | "ATTENTION" | "ACTIVE"; detail: string; progressPercent: number; dueDate: string | null }[];
  workload: { invited: number; active: number; underReview: number; approved: number };
  recentActivity: AuditLogEntry[];
}

export interface AuditorProfileFull extends AuditorProfile {
  fullName: string;
  email: string;
}

export interface ChecklistPreset {
  id: string;
  name: string;
  items: { name: string; category: string; description: string; required: boolean }[];
}

export interface FinancialInputs {
  revenue: number;
  costOfSales: number;
  operatingExpenses: number;
  accountingDepreciation: number;
  entertainmentExpenses: number;
  taxDepreciationAllowances: number;
  sourceDocumentId: string | null;
}

export interface FinancialsView {
  inputs: (FinancialInputs & { taxYear: string; updatedAt: string }) | null;
  computed: {
    grossProfit: number;
    grossMarginPercent: number;
    accountingProfit: number;
    disallowables: number;
    allowances: number;
    taxableIncome: number;
    citRatePercent: number;
    citLiability: number;
  } | null;
  rateCategory: "standard_30" | "sme_14";
}

export interface ExtractResult {
  inputs: Partial<Record<keyof FinancialInputs, number | null>>;
  confidence: Partial<Record<keyof FinancialInputs, number>>;
  notes: string;
}

export interface DashboardView {
  progressPercent: number;
  steps: { key: string; label: string; state: "done" | "in_progress" | "pending"; progressPercent: number; ratioLabel: string; href: string }[];
  documentsUploaded: number;
  documentsRequired: number;
  accountingProfit: number | null;
  taxableIncome: number | null;
  citLiability: number | null;
  auditorStatus: EngagementStatus | "none";
  auditorName: string | null;
  auditorFirm: string | null;
  attentionItems: { id: string; severity: IssueSeverityV2; title: string; description: string; link: string }[];
}

export interface Thread {
  id: string;
  engagementId: string;
  companyName: string;
  auditorName: string;
  topic: string;
  category: string;
  status: "open" | "closed";
  lastMessage: string;
  lastMessageAt: string;
  unreadCount: number;
}

export interface ThreadMessage {
  id: string;
  senderId: string;
  senderName: string;
  senderRole: Role;
  text: string;
  createdAt: string;
}
