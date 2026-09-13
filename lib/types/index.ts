// Shared types used across the app. Keeping these in one file makes it
// easy to see the full shape of our data model at a glance, and this is
// the file to update first once the FastAPI backend is wired up.

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

export interface DashboardStep {
  label: string;
  state: "done" | "warning" | "pending" | "in_progress";
  progressPercent: number;
  ratioLabel?: string;
  sublabel?: string;
  href?: string;
}

export interface DashboardSummary {
  progressPercent: number;
  progressUpdatedAt: string;
  steps: DashboardStep[];
  documentsUploaded: number;
  documentsTotal: number;
  accountingProfit: string;
  taxableIncome: string;
  estCitLiability: string;
  auditorStatus: string;
  attentionItems: {
    id?: string;
    issueId?: string;
    severity: "critical" | "warning";
    title: string;
    description: string;
    link?: string;
  }[];
}

// --- Documents page ---

// "processing" is a client-only transient state used right after a
// browser upload, before we know whether the file needs review — it's
// never returned by the mock/real API for existing documents.
export type DocumentStatus = "processed" | "review_required" | "missing" | "processing";

export interface DocumentRow {
  id: string;
  name: string;
  type: string; // e.g. "Financial Statements", "Trial Balance"
  status: DocumentStatus;
  aiConfidencePercent: number | null; // null when status is "missing" or "processing"
  uploadedDate: string | null; // null when status is "missing"
  sizeLabel?: string; // e.g. "2.4 MB" — only set for files uploaded client-side
}

export interface DocumentsSummary {
  uploadedCount: number;
  processedCount: number;
  reviewRequiredCount: number;
  missingCount: number;
  documents: DocumentRow[];
}

// --- Financials page ---

export type FinancialsTab =
  | "Income Statement"
  | "Balance Sheet"
  | "Trial Balance"
  | "General Ledger"
  | "Fixed Assets";

export interface FinancialLineItem {
  item: string;
  amount: string;
  source: string;
  category?: string;
  taxTreatment?: string;
  aiConfidence?: number;
  isSubtotal?: boolean;
}

export interface FinancialsSummary {
  revenue: string;
  expenses: string;
  accountingProfit: string;
  taxAdjustments: string;
  // Enriched corporate metrics
  costOfSales?: string;
  grossProfit?: string;
  grossMarginPercent?: number;
  operatingExpenses?: string;
  netPbt?: string;
  // Statutory Sri Lanka CIT computation
  disallowableAddBacks?: string;
  taxCapitalAllowances?: string;
  taxableIncome?: string;
  citRatePercent?: number;
  estCitLiability?: string;
  auditorStatus?: string;
  irdGazetteRef?: string;
  tabs: Record<FinancialsTab, FinancialLineItem[]>;
}

export interface AiFinancialReportData {
  generatedAt: string;
  taxYear: string;
  companyName: string;
  executiveSummary: string;
  profitabilityAnalysis: {
    revenue: string;
    grossProfit: string;
    grossMargin: string;
    operatingExpenses: string;
    netPbt: string;
  };
  taxReconciliation: {
    accountingProfit: string;
    disallowablesTotal: string;
    disallowablesItems: { item: string; amount: string; reason: string }[];
    capitalAllowancesTotal: string;
    taxableIncome: string;
    citRate: string;
    estimatedLiability: string;
  };
  complianceScore: number;
  keyTaxRisks: string[];
  recommendations: string[];
}

// --- Auditor Review page (business side) ---

export interface AuditorReviewIssue {
  id: string;
  status: "action_required" | "pending_clarification";
  title: string;
  comment: string;
  source: string;
  response?: string;
  correctionNote?: string;
  resolved?: boolean;
  attachedFileName?: string;
  attachedFileSize?: string;
}

export interface AuditorReviewSummary {
  auditorName: string;
  auditorFirm: string;
  auditorEmail?: string;
  reviewStatus: string; // e.g. "Waiting for Review"
  submittedDate: string;
  expectedByDate: string;
  reviewedPercent: number;
  approvedCount: number;
  warningsCount: number;
  criticalCount: number;
  pendingCount: number;
  issues: AuditorReviewIssue[];
}

// --- Settings page (business side) ---

export interface CompanySettings {
  companyName: string;
  tradingName?: string;
  registrationNumber: string;
  tinNumber: string;
  vatNumber?: string;
  isSvatRegistered?: boolean;
  svatNumber?: string;
  citTaxRateCategory?: "standard_30" | "sme_export_14" | "concessionary_15" | "other";
  financialYear: string;
  contactEmail: string;
  contactPhone: string;
  registeredAddress?: string;
  industrySector?: string;
}

export interface AssignedAuditorDetails {
  firmName: string;
  firmRegNo: string;
  leadAuditorName: string;
  leadAuditorEmail: string;
  leadAuditorPhone: string;
  icaslMemberNo: string;
  engagementYear: string;
  status: "Active" | "Pending_Engagement" | "Terminated";
  permissions: {
    canViewDocuments: boolean;
    canEditAdjustments: boolean;
    canSignOffReturn: boolean;
    canDirectFileIRD: boolean;
  };
  assignedDate: string;
}

export interface FinanceTeamMember {
  id: string;
  name: string;
  initials: string;
  email: string;
  role: "Owner" | "Finance Director" | "Senior Accountant" | "Tax Officer" | "Viewer";
  status: "Active" | "Invited" | "Inactive";
  lastActive: string;
  canSignReturns: boolean;
}

export interface CompanyTaxPreferences {
  accountingStandard: "SLFRS_FULL" | "SLFRS_SMES";
  currency: "LKR";
  basisOfAccounting: "accrual" | "cash";
  aiConfidenceThreshold: number; // e.g. 85 (%)
  autoNotifyAuditorOnReady: boolean;
  allowAuditorDirectModifications: boolean;
  enableAiOcrAutoExtract: boolean;
  quarterlyAdvanceTaxTracking: boolean;
}

export interface CompanyNotificationPrefs {
  auditorDocRequests: boolean;
  auditorReviewFeedback: boolean;
  citFilingClearance: boolean;
  irdDeadlinesReminders: boolean;
  advanceTaxPaymentDue: boolean;
  aiExtractionAlerts: boolean;
  emailAlerts: boolean;
  inAppNotifications: boolean;
}

export interface CompanySecuritySettings {
  twoFactorAuth: boolean;
  sessionTimeoutMinutes: number;
  ipRestriction: boolean;
  allowedIps?: string;
  dataEncryptionStandard: string;
}

export interface CompanyActivityLogEntry {
  id: string;
  action: string;
  actor: string;
  actorRole: string;
  timestamp: string;
  timeAgo: string;
  ipAddress?: string;
}

export interface CompanyFullSettings {
  profile: CompanySettings;
  auditor: AssignedAuditorDetails;
  team: FinanceTeamMember[];
  preferences: CompanyTaxPreferences;
  notifications: CompanyNotificationPrefs;
  security: CompanySecuritySettings;
  auditTrail: CompanyActivityLogEntry[];
}

// --- Auditor portal: shared ---

export type CitStatus =
  | "Draft"
  | "Under Review"
  | "Ready for Auditor"
  | "Approved"
  | "Waiting for Company";

export interface CompanyRow {
  id: string;
  name: string;
  tin: string;
  financialYear: string;
  citStatus: CitStatus;
  subStatusLabel: string; // e.g. "In Progress", "Not Started"
  criticalCount: number;
  warningsCount: number;
  progressPercent: number;
  dueDate: string;
  contactEmail?: string;
  contactPhone?: string;
  registrationNumber?: string;
  address?: string;
  businessCategory?: string;
  annualTurnover?: string;
  contactPerson?: string;
  taxOffice?: string;
}

// --- Auditor Dashboard (home) ---

export interface AuditorDashboardSummary {
  companiesAssigned: number;
  underReview?: number;
  pendingReviews: number;
  criticalIssues: number;
  completedThisPeriod: number;
  priorityReviews: {
    companyName: string;
    tag: "critical" | "attention" | "ready";
    tagLabel: string;
    detail: string;
    progressPercent: number;
    dueDate: string;
  }[];
  workload: {
    pending: number;
    inProgress: number;
    waitingForCompany: number;
    readyForApproval: number;
    completed: number;
  };
  recentActivity: { title: string; company: string; timeAgo: string }[];
}

// --- Companies page ---

export interface CompaniesSummary {
  companies: CompanyRow[];
}

// --- Review Queue page ---

export type ReviewQueueFilter =
  | "All"
  | "Pending"
  | "In Progress"
  | "Waiting for Company"
  | "Ready for Approval"
  | "Completed";

export interface ReviewQueueRow {
  id: string;
  companyName: string;
  tin: string;
  status: string;
  criticalCount: number;
  warningsCount: number;
  progressPercent: number;
  dueDate: string;
}

export interface ReviewQueueSummary {
  rows: ReviewQueueRow[];
}

// --- Issues page ---

export type IssueSeverity = "Critical" | "Warning" | "Information" | "Resolved";

export interface IssueRow {
  id: string;
  title: string;
  company: string;
  amount: string;
  severity: IssueSeverity;
  status: "Open" | "Resolved";
  source: string;
}

export interface IssuesSummary {
  criticalCount: number;
  warningsCount: number;
  informationCount: number;
  resolvedCount: number;
  issues: IssueRow[];
}

// --- Audit Log page ---

export interface AuditLogRow {
  id: string;
  timestamp: string;
  company: string;
  user: string;
  action: string;
  actionTone: "success" | "warning" | "info" | "pending";
  details: string;
}

export interface AuditLogSummary {
  entries: AuditLogRow[];
}

// --- Auditor Settings page ---

export interface AuditorProfileSettings {
  fullName: string;
  email: string;
  phone: string;
  licenseNumber: string;
  organization: string;
  designation: string;
  caSriLankaNo?: string;
  irdPractitionerNo?: string;
  firmRegNo?: string;
  firmAddress?: string;
  signatureStampUrl?: string;
}

export interface AuditorTeamMember {
  id: string;
  name: string;
  initials: string;
  email: string;
  role: "Audit Partner" | "Senior Auditor" | "Audit Assistant" | "Tax Specialist";
  assignedCompaniesCount: number;
  status: "Active" | "Invited";
}

export interface AuditPreferences {
  defaultTaxYear: string;
  accountingStandard: "SLFRS / LKAS for SMEs" | "Full SLFRS" | "Tax Basis of Accounting";
  materialityThresholdPercent: number;
  autoRemindDaysBeforeDeadline: number[];
  autoRequestStandardPackOnConnect: boolean;
  strictVatReconciliation: boolean;
}

export interface AuditorNotificationPrefs {
  clientDocumentUploaded: boolean;
  clientResponseReceived: boolean;
  discussionMessageReceived: boolean;
  deadlineApproaching: boolean;
  clientInvitationReceived: boolean;
  digestFrequency: "instant" | "daily_digest" | "weekly";
}

export interface AuditorSecuritySettings {
  twoFactorEnabled: boolean;
  sessionTimeoutMinutes: number;
  ipWhitelistEnabled: boolean;
  immutableAuditTrail: boolean;
  activeSessions: {
    id: string;
    device: string;
    browser: string;
    ipAddress: string;
    lastActive: string;
    isCurrent: boolean;
  }[];
}

export interface AuditorFullSettings {
  profile: AuditorProfileSettings;
  team: AuditorTeamMember[];
  preferences: AuditPreferences;
  notifications: AuditorNotificationPrefs;
  security: AuditorSecuritySettings;
}

// --- Auditor Documents page ---

export interface AuditorDocumentRow {
  id: string;
  companyName: string;
  documentName: string;
  documentType: string;
  status: "processed" | "review_required" | "verified";
  aiConfidencePercent: number;
  uploadedDate: string;
  sizeLabel: string;
}

export interface AuditorDocumentsSummary {
  totalDocuments: number;
  pendingReviewCount: number;
  verifiedCount: number;
  documents: AuditorDocumentRow[];
}

// --- Auditor Requests page ---

export interface AuditorRequestRow {
  id: string;
  requestId: string;
  companyName: string;
  title: string;
  description: string;
  category: string;
  status: "pending" | "responded" | "resolved";
  priority: "high" | "medium" | "low";
  requestedDate: string;
  dueDate: string;
}

export interface AuditorRequestsSummary {
  totalRequests: number;
  pendingCount: number;
  respondedCount: number;
  resolvedCount: number;
  requests: AuditorRequestRow[];
}

// --- Auditor Responses page ---

export interface AttachedResponseFile {
  id: string;
  name: string;
  size: string;
  type: string;
  uploadedAt: string;
  downloadUrl?: string;
}

export interface ClientResponseItem {
  id: string;
  requestId: string;
  requestTitle: string;
  companyName: string;
  category: string;
  clientResponseNote: string;
  submittedBy: string;
  submittedAt: string;
  status: "unreviewed" | "resolved" | "revision_requested";
  attachedFiles: AttachedResponseFile[];
  revisionNote?: string;
}

export interface AuditorResponsesSummary {
  totalResponses: number;
  unreviewedCount: number;
  resolvedCount: number;
  revisionCount: number;
  responses: ClientResponseItem[];
}

// --- Auditor Discussions page ---

export interface DiscussionMessage {
  id: string;
  sender: string;
  senderRole: "Auditor" | "Company";
  text: string;
  timestamp: string;
}

export interface DiscussionThread {
  id: string;
  companyName: string;
  auditorName?: string;
  topic: string;
  category?: string;
  lastMessage: string;
  lastUpdated: string;
  unreadCount: number;
  status: "Open" | "Closed";
  messages: DiscussionMessage[];
}

export interface BusinessDiscussionSummary {
  assignedAuditor: {
    name: string;
    firm: string;
  };
  threads: DiscussionThread[];
}

export interface AuditorDiscussionsSummary {
  threads: DiscussionThread[];
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
