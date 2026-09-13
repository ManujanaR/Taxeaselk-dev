# -*- coding: utf-8 -*-
"""
Script to generate TaxEaseLK_Backend_Architecture_and_API_Specification.docx
"""
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_backend_doc():
    doc = Document()

    # Set page margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    NAVY_HEX = "1E3A8A"
    BLUE_HEX = "2563EB"
    DARK_HEX = "0F172A"
    GRAY_HEX = "475569"

    def set_cell_background(cell, color_hex):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/>'
            f'<w:right w:w="{right}" w:type="dxa"/>'
            f'</w:tcMar>'
        )
        tcPr.append(tcMar)

    def set_table_borders(table, color_hex="CBD5E1"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/>'
            f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color_hex}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def add_callout(text_list, title="ARCHITECTURE BLUEPRINT", color_hex=NAVY_HEX, bg_hex="EFF6FF"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(6.7)
        cell = tbl.cell(0, 0)
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{color_hex}"/>'
            f'<w:top w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:bottom w:val="none"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        run_title = p.add_run(f"■  {title}")
        run_title.font.name = "Calibri"
        run_title.font.size = Pt(10.5)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor.from_string(color_hex)

        for line in text_list:
            p2 = cell.add_paragraph()
            p2.paragraph_format.space_before = Pt(2)
            p2.paragraph_format.space_after = Pt(2)
            p2.paragraph_format.line_spacing = 1.15
            run_line = p2.add_run(line)
            run_line.font.name = "Calibri"
            run_line.font.size = Pt(9.5)
            run_line.font.color.rgb = RGBColor.from_string("1E293B")

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ------------------ COVER / HEADER TITLE ------------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(0)
    p_pre.paragraph_format.space_after = Pt(4)
    run_pre = p_pre.add_run("TAXEASELK ENGINEERING SPECIFICATION")
    run_pre.font.name = "Calibri"
    run_pre.font.size = Pt(11)
    run_pre.font.bold = True
    run_pre.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(6)
    run_title = p_title.add_run("Backend Architecture, Database Schema & FastAPI Implementation Blueprint")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor.from_string(DARK_HEX)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run("Complete technical guide for building the FastAPI + PostgreSQL/Supabase backend to power the TaxEaseLK Next.js frontend.")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor.from_string(GRAY_HEX)

    # Metadata table
    tbl_meta = doc.add_table(rows=2, cols=4)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_meta, "CBD5E1")
    meta_headers = ["Target Stack", "Database", "Authentication", "Compliance Standard"]
    meta_values = ["FastAPI (Python 3.11+)", "PostgreSQL / Supabase", "JWT + Supabase Auth", "Inland Revenue Act No. 24 of 2017"]
    for i, h in enumerate(meta_headers):
        cell = tbl_meta.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 60, 60, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

        cell_v = tbl_meta.cell(1, i)
        set_cell_margins(cell_v, 60, 60, 100, 100)
        p_v = cell_v.paragraphs[0]
        p_v.paragraph_format.space_after = Pt(0)
        r_v = p_v.add_run(meta_values[i])
        r_v.font.name = "Calibri"
        r_v.font.size = Pt(9)
        r_v.font.color.rgb = RGBColor.from_string(DARK_HEX)

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(12)
    p_div.paragraph_format.space_after = Pt(12)

    # ------------------ SECTION 1: HOW TO USE SPEC TO BUILD BACKEND ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("1. How to Use the Frontend Specification to Build Your Backend")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "YES! The frontend functional specification and the TypeScript codebase provide 100% of the contract needed to develop your backend. "
        "Every page in the Next.js app communicates through dedicated API abstraction layers ('lib/api/business.ts', 'lib/api/auditor.ts', and 'lib/api/notifications.ts'). "
        "Because the frontend is structured with clean data boundaries, you can build your FastAPI server endpoint by endpoint, replacing each mock return object with real database queries without altering frontend UI layout code."
    )

    add_callout([
        "4-Step Backend Construction Strategy:",
        "1. Provision PostgreSQL / Supabase Schema: Run the 14 relational tables detailed in Section 2.",
        "2. Build the FastAPI Endpoints: Implement the REST routes mapped in Section 3 matching the frontend contract.",
        "3. Implement Tax Business Logic & Pipeline Algorithms: Code the statutory formulas (Accounting PBT, Section 11 Disallowables, Fourth Schedule Depreciation, 30%/14% CIT Liability) detailed in Section 4.",
        "4. Wire Authentication & CORS: Configure JWT tokens and set NEXT_PUBLIC_API_URL in .env.local to point to http://localhost:8000."
    ], title="BACKEND IMPLEMENTATION ROADMAP", color_hex=BLUE_HEX, bg_hex="EFF6FF")

    # ------------------ SECTION 2: RELATIONAL DATABASE SCHEMA ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("2. Relational Database Schema (PostgreSQL / Supabase DDL)")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "Below is the complete database schema required to store all entity profiles, statutory financial line items, document metadata, audit inquiries, and notifications."
    )

    tbl_db = doc.add_table(rows=1, cols=4)
    tbl_db.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_db, "CBD5E1")
    db_cols = ["Table Name", "Primary Columns & Types", "Foreign Keys & Relationships", "Frontend Consumer View"]
    for i, title in enumerate(db_cols):
        cell = tbl_db.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    db_rows = [
        (
            "users",
            "id UUID PRIMARY KEY, email VARCHAR(255) UNIQUE, password_hash TEXT, role VARCHAR(20) CHECK (role IN ('business', 'auditor')), full_name VARCHAR(255), is_active BOOLEAN, created_at TIMESTAMPTZ",
            "Auth parent table for all portal actors.",
            "Sign-In, Role Selection, Profile Menu"
        ),
        (
            "companies",
            "id UUID PRIMARY KEY, user_id UUID REFERENCES users(id), company_name VARCHAR(255), trading_name VARCHAR(255), registration_number VARCHAR(50), tin_number VARCHAR(50), vat_number VARCHAR(50), is_svat_registered BOOLEAN, svat_number VARCHAR(50), cit_tax_rate_category VARCHAR(50) DEFAULT 'standard_30', financial_year VARCHAR(20) DEFAULT '2025/26', contact_email VARCHAR(255), contact_phone VARCHAR(50), registered_address TEXT, industry_sector VARCHAR(100), cit_status VARCHAR(50) DEFAULT 'Draft', created_at TIMESTAMPTZ",
            "Owned by Business User; referenced by engagements, documents, financials.",
            "Settings, Top Nav Badges, Dashboard Subtitle, Auditor Companies Table"
        ),
        (
            "auditor_profiles",
            "id UUID PRIMARY KEY, user_id UUID REFERENCES users(id), firm_name VARCHAR(255), firm_reg_no VARCHAR(50), lead_auditor_name VARCHAR(255), license_number VARCHAR(50), icasl_member_no VARCHAR(50), ird_practitioner_no VARCHAR(50), phone VARCHAR(50), email VARCHAR(255), office_address TEXT, rating_score NUMERIC(3,2) DEFAULT 5.0, created_at TIMESTAMPTZ",
            "Owned by Auditor User; referenced by client engagements.",
            "Assigned Auditor Card, Auditor Settings, Rate Auditor Modal"
        ),
        (
            "engagements",
            "id UUID PRIMARY KEY, company_id UUID REFERENCES companies(id), auditor_id UUID REFERENCES auditor_profiles(id), tax_year VARCHAR(20), status VARCHAR(50) CHECK (status IN ('Pending_Engagement', 'Active', 'Under_Review', 'Approved', 'Terminated')), progress_percent INT DEFAULT 0, submitted_date VARCHAR(50), expected_date VARCHAR(50), approved_count INT DEFAULT 0, warnings_count INT DEFAULT 0, critical_count INT DEFAULT 0, pending_count INT DEFAULT 0, created_at TIMESTAMPTZ",
            "Binds a Company to an Auditor for a specific assessment year.",
            "Dashboard Pipeline, Assigned Auditor Card, Auditor Review Queue"
        ),
        (
            "documents",
            "id UUID PRIMARY KEY, company_id UUID REFERENCES companies(id), name VARCHAR(255), file_url TEXT, doc_type VARCHAR(100), status VARCHAR(50) CHECK (status IN ('processing', 'processed', 'review_required', 'verified')), ai_confidence_percent NUMERIC(5,2), uploaded_date VARCHAR(50), size_label VARCHAR(50), uploaded_by UUID REFERENCES users(id), created_at TIMESTAMPTZ",
            "Stores metadata and cloud storage URI for uploaded PDFs/spreadsheets.",
            "Documents Page, Document Stat Tile, Auditor Documents Repository"
        ),
        (
            "financial_summaries",
            "id UUID PRIMARY KEY, company_id UUID REFERENCES companies(id), tax_year VARCHAR(20), revenue NUMERIC(15,2), cost_of_sales NUMERIC(15,2), gross_profit NUMERIC(15,2), gross_margin_percent NUMERIC(5,2), operating_expenses NUMERIC(15,2), accounting_profit NUMERIC(15,2), disallowable_add_backs NUMERIC(15,2), tax_capital_allowances NUMERIC(15,2), taxable_income NUMERIC(15,2), cit_rate_percent INT DEFAULT 30, est_cit_liability NUMERIC(15,2), auditor_status VARCHAR(100), ird_gazette_ref VARCHAR(255), updated_at TIMESTAMPTZ",
            "Stores computed commercial metrics and statutory tax waterfall results.",
            "Financials Page, Accounting Profit Tile, CIT Computation Banner, AI Report"
        ),
        (
            "financial_line_items",
            "id UUID PRIMARY KEY, financial_summary_id UUID REFERENCES financial_summaries(id), tab_name VARCHAR(50) CHECK (tab_name IN ('Income Statement', 'Balance Sheet', 'Trial Balance', 'General Ledger', 'Fixed Assets')), item_name VARCHAR(255), amount NUMERIC(15,2), source VARCHAR(255), category VARCHAR(100), tax_treatment VARCHAR(255), ai_confidence INT, is_subtotal BOOLEAN DEFAULT FALSE, order_index INT",
            "Line-item accounting ledger breakdown for sub-tabbed schedules.",
            "Financials Schedules Table (FinancialsTable.tsx)"
        ),
        (
            "auditor_review_issues",
            "id UUID PRIMARY KEY, engagement_id UUID REFERENCES engagements(id), company_id UUID REFERENCES companies(id), title VARCHAR(255), comment TEXT, source VARCHAR(100), status VARCHAR(50) CHECK (status IN ('action_required', 'pending_clarification', 'resolved')), severity VARCHAR(20) CHECK (severity IN ('critical', 'warning')), response_text TEXT, attached_file_name VARCHAR(255), attached_file_url TEXT, created_at TIMESTAMPTZ, resolved_at TIMESTAMPTZ",
            "Stores issues raised by auditor during inspection of company accounts.",
            "Dashboard Requires Attention Card, Auditor Review Inquiries Manager"
        ),
        (
            "auditor_requests",
            "id UUID PRIMARY KEY, engagement_id UUID REFERENCES engagements(id), company_id UUID REFERENCES companies(id), reference_code VARCHAR(50), title VARCHAR(255), description TEXT, category VARCHAR(100), priority VARCHAR(20) CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')), due_date DATE, status VARCHAR(50) CHECK (status IN ('pending', 'responded', 'resolved')), requested_by UUID REFERENCES auditor_profiles(id), created_at TIMESTAMPTZ",
            "Formal Requests for Information (RFI) issued by auditor to client.",
            "Auditor Requests Page, Company Notifications, Attention Items"
        ),
        (
            "client_responses",
            "id UUID PRIMARY KEY, request_id UUID REFERENCES auditor_requests(id), company_id UUID REFERENCES companies(id), client_response_note TEXT, submitted_by VARCHAR(255), status VARCHAR(50) CHECK (status IN ('unreviewed', 'resolved', 'revision_requested')), revision_note TEXT, submitted_at TIMESTAMPTZ",
            "Answers and explanations submitted by business in response to RFI.",
            "Auditor Review Queue / Responses Page"
        ),
        (
            "response_attachments",
            "id UUID PRIMARY KEY, response_id UUID REFERENCES client_responses(id), file_name VARCHAR(255), file_size VARCHAR(50), file_type VARCHAR(50), download_url TEXT, uploaded_at TIMESTAMPTZ",
            "Evidence files (vouchers, invoices) attached to client responses.",
            "Auditor Responses Download Action"
        ),
        (
            "discussion_threads",
            "id UUID PRIMARY KEY, company_id UUID REFERENCES companies(id), auditor_id UUID REFERENCES auditor_profiles(id), topic VARCHAR(255), category VARCHAR(100), status VARCHAR(20) DEFAULT 'Open', last_message TEXT, last_updated TIMESTAMPTZ",
            "Top-level chat threads between business and auditor.",
            "Discussions Page (Business & Auditor)"
        ),
        (
            "discussion_messages",
            "id UUID PRIMARY KEY, thread_id UUID REFERENCES discussion_threads(id), sender_name VARCHAR(255), sender_role VARCHAR(20) CHECK (sender_role IN ('Auditor', 'Company')), text TEXT, created_at TIMESTAMPTZ",
            "Individual message bubbles inside a discussion thread.",
            "Discussions Chat Stream"
        ),
        (
            "notifications",
            "id UUID PRIMARY KEY, user_id UUID REFERENCES users(id), recipient_role VARCHAR(20), company_name VARCHAR(255), type VARCHAR(20) CHECK (type IN ('critical', 'warning', 'info', 'success')), title VARCHAR(255), message TEXT, link VARCHAR(255), is_read BOOLEAN DEFAULT FALSE, created_at TIMESTAMPTZ",
            "Real-time notifications sent to bell dropdown.",
            "TopBar Notification Bell"
        ),
        (
            "audit_logs",
            "id UUID PRIMARY KEY, company_id UUID REFERENCES companies(id), actor_name VARCHAR(255), actor_role VARCHAR(50), event_type VARCHAR(50), details TEXT, action_tone VARCHAR(20) DEFAULT 'info', created_at TIMESTAMPTZ",
            "Immutable audit compliance trail under Inland Revenue Act No. 24.",
            "Audit Log Page ('/audit-log')"
        ),
        (
            "company_checklist_items",
            "id UUID PRIMARY KEY, company_id UUID REFERENCES companies(id), assigned_auditor_id UUID REFERENCES auditor_profiles(id), item_key VARCHAR(50), name VARCHAR(255), category VARCHAR(100), description TEXT, required BOOLEAN DEFAULT TRUE, auditor_note TEXT, updated_at TIMESTAMPTZ",
            "Stores the company-specific document checklist created and published by the assigned auditor.",
            "AuditorDocumentChecklist (Business) & AuditorChecklistModal (Auditor)"
        ),
        (
            "auditor_reviews",
            "id UUID PRIMARY KEY, auditor_id UUID REFERENCES auditor_profiles(id), company_id UUID REFERENCES companies(id), auditor_email VARCHAR(255), auditor_name VARCHAR(255), company_name VARCHAR(255), tax_year VARCHAR(20), rating NUMERIC(3,2), timeliness_rating INT, communication_rating INT, technical_rating INT, review_comment TEXT, client_reviewer_name VARCHAR(255), created_at TIMESTAMPTZ",
            "Stores verified client reviews, star scores, and dimension sub-ratings submitted by business owners.",
            "RateAuditorModal (Business) & AuditorRankRating Drawer (Auditor)"
        )
    ]

    for item in db_rows:
        row_cells = tbl_db.add_row().cells
        for col_idx, text in enumerate(item):
            cell = row_cells[col_idx]
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(8)
            r.font.color.rgb = RGBColor.from_string(DARK_HEX)
            if col_idx == 0:
                r.font.bold = True
                set_cell_background(cell, "F8FAFC")

    # ------------------ SECTION 3: FASTAPI REST API SPECIFICATION ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("3. FastAPI REST Endpoints Implementation Matrix")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "Here are the exact HTTP endpoints, request payloads, and response contracts that your FastAPI application should expose to seamlessly connect to the Next.js frontend."
    )

    tbl_api = doc.add_table(rows=1, cols=4)
    tbl_api.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_api, "CBD5E1")
    api_cols = ["HTTP Route & Method", "Frontend Consumer Function", "Request Parameters / Body", "Expected JSON Response Payload"]
    for i, title in enumerate(api_cols):
        cell = tbl_api.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    api_rows = [
        (
            "GET /api/dashboard\n?company_name={name}",
            "getDashboardSummary()\n(lib/api/business.ts)",
            "Query Param:\ncompany_name (string, optional)",
            "{\n  progressPercent: 65,\n  progressUpdatedAt: 'Just now',\n  documentsUploaded: 4,\n  documentsTotal: 5,\n  accountingProfit: 'Rs. 4.6M',\n  auditorStatus: 'Under Review',\n  steps: [{label, state, progressPercent, ratioLabel, sublabel, href}],\n  attentionItems: [{id, severity, title, description, link}]\n}"
        ),
        (
            "GET /api/documents\n?company_name={name}",
            "getDocumentsSummary()\n(lib/api/business.ts)",
            "Query Param:\ncompany_name (string, optional)",
            "{\n  uploadedCount: 4,\n  processedCount: 3,\n  reviewRequiredCount: 1,\n  missingCount: 1,\n  documents: [{id, name, type, status, aiConfidencePercent, uploadedDate, sizeLabel}]\n}"
        ),
        (
            "POST /api/documents/upload",
            "handleFilesAccepted()\n(DocumentsManager.tsx)",
            "Multipart/Form-Data:\n• file: Binary\n• doc_type: string\n• company_name: string",
            "{\n  id: 'doc_123',\n  name: 'Trial_Balance_2026.xlsx',\n  type: 'Trial Balance',\n  status: 'processed',\n  ai_confidence_percent: 98.5,\n  uploaded_date: 'Today',\n  size_label: '2.4 MB'\n}"
        ),
        (
            "DELETE /api/documents/{id}",
            "handleRemove()\n(DocumentsManager.tsx)",
            "Path Param: id (string)",
            "{ success: true, message: 'Document deleted' }"
        ),
        (
            "GET /api/financials\n?company_name={name}",
            "getFinancialsSummary()\n(lib/api/business.ts)",
            "Query Param:\ncompany_name (string, optional)",
            "{\n  revenue: 'Rs. 25.0M',\n  costOfSales: 'Rs. 15.2M',\n  grossProfit: 'Rs. 9.8M',\n  grossMarginPercent: 39.2,\n  operatingExpenses: 'Rs. 5.2M',\n  accountingProfit: 'Rs. 4.6M',\n  disallowableAddBacks: 'Rs. 2.1M',\n  taxCapitalAllowances: 'Rs. 1.5M',\n  taxableIncome: 'Rs. 5.2M',\n  citRatePercent: 30,\n  estCitLiability: 'Rs. 1.56M',\n  auditorStatus: 'Under Review',\n  tabs: { 'Income Statement': [...], 'Balance Sheet': [...], 'Trial Balance': [...] }\n}"
        ),
        (
            "GET /api/auditor-review\n?company_name={name}",
            "getAuditorReviewSummary()\n(lib/api/business.ts)",
            "Query Param:\ncompany_name (string, optional)",
            "{\n  auditorName: 'K.L. Perera, FCA',\n  auditorFirm: 'BDO Partners',\n  auditorEmail: 'kl.perera@bdo.lk',\n  reviewStatus: 'Under Review',\n  submittedDate: '15 Oct 2026',\n  expectedByDate: '15 Nov 2026',\n  reviewedPercent: 65,\n  approvedCount: 8,\n  warningsCount: 2,\n  criticalCount: 1,\n  pendingCount: 0,\n  issues: [{id, status, title, comment, source}]\n}"
        ),
        (
            "POST /api/auditor-review/issues/{id}/resolve",
            "handleResolveIssue()\n(AuditorIssuesManager.tsx)",
            "JSON Body:\n{\n  response: string,\n  attached_file_name?: string,\n  attached_file_url?: string\n}",
            "{ success: true, status: 'resolved' }"
        ),
        (
            "GET /api/company/settings",
            "getCompanySettings()\n(lib/api/business.ts)",
            "Headers: Authorization Bearer token",
            "{\n  companyName: 'ABC (Pvt) Ltd',\n  financialYear: '2025/26',\n  registrationNumber: 'PV 00294812',\n  tinNumber: '192847291-0000',\n  vatNumber: '293847291-7000',\n  isSvatRegistered: true,\n  citTaxRateCategory: 'standard_30',\n  contactEmail: 'finance@abc.lk',\n  contactPhone: '+94 11 234 5678'\n}"
        ),
        (
            "POST /api/company/settings",
            "updateCompanyTaxProfile()\n(CompanySettingsForm.tsx)",
            "JSON Body: CompanySettings object",
            "{ success: true, updated: CompanySettings }"
        ),
        (
            "GET /api/auditor/dashboard",
            "getAuditorDashboardSummary()\n(lib/api/auditor.ts)",
            "Headers: Authorization Bearer token (Auditor)",
            "{\n  companiesAssigned: 14,\n  pendingReviews: 6,\n  criticalIssues: 3,\n  completedThisPeriod: 8,\n  priorityReviews: [{companyName, tag, tagLabel, detail, progressPercent, dueDate}],\n  workload: { pending, inProgress, waitingForCompany, readyForApproval, completed }\n}"
        ),
        (
            "GET /api/auditor/companies",
            "getCompaniesSummary()\n(lib/api/auditor.ts)",
            "Query: search, status",
            "{\n  companies: [{id, name, tin, financialYear, citStatus, criticalCount, warningsCount, progressPercent, dueDate}]\n}"
        ),
        (
            "POST /api/auditor/invitations",
            "InviteAuditorButton.tsx",
            "JSON Body:\n{\n  company_name: string,\n  auditor_email: string,\n  tax_year: string,\n  message?: string\n}",
            "{ success: true, invitation_id: 'inv_101' }"
        ),
        (
            "POST /api/auditor/checklists",
            "handleSaveAndPublish()\n(AuditorChecklistModal.tsx)",
            "JSON Body:\n{\n  company_name: string,\n  auditor_name: string,\n  auditor_firm: string,\n  items: [{id, name, category, description, required, auditorNote}]\n}",
            "{ success: true, message: 'Checklist published to company' }"
        ),
        (
            "GET /api/checklists/{company_name}",
            "loadChecklist()\n(AuditorDocumentChecklist.tsx)",
            "Path Param: company_name (string)",
            "{\n  company_name: 'ABC (Pvt) Ltd',\n  assignedAuditorName: 'K.L. Perera, FCA',\n  assignedAuditorFirm: 'BDO Partners',\n  items: [{id, name, category, description, required, auditorNote}]\n}"
        ),
        (
            "POST /api/auditor/requests",
            "handleCreateRequest()\n(RequestsManager.tsx)",
            "JSON Body:\n{\n  company_name: string,\n  title: string,\n  category: string,\n  priority: string,\n  due_date: string,\n  description: string\n}",
            "{ id, reference_code: 'REQ-2026-005', status: 'pending' }"
        ),
        (
            "GET /api/auditor/responses",
            "getAuditorResponsesSummary()\n(lib/api/auditor.ts)",
            "Query: status, search",
            "{\n  totalResponses: 12,\n  unreviewedCount: 3,\n  responses: [{id, requestId, requestTitle, companyName, clientResponseNote, submittedBy, attachedFiles}]\n}"
        ),
        (
            "POST /api/auditor/responses/{id}/resolve",
            "resolveAuditorResponse()\n(AuditorResponsesManager.tsx)",
            "Path Param: id",
            "{ success: true, status: 'resolved' }"
        ),
        (
            "GET /api/notifications\n?role={role}&company={name}",
            "getNotifications()\n(lib/api/notifications.ts)",
            "Query: role ('business' | 'auditor'), company_name",
            "{\n  unread_count: 2,\n  notifications: [{id, type, title, message, link, is_read, created_at}]\n}"
        ),
        (
            "POST /api/notifications/{id}/read",
            "markNotificationAsRead()",
            "Path Param: id",
            "{ success: true }"
        ),
        (
            "POST /api/auditors/rate",
            "handleSubmit()\n(RateAuditorModal.tsx)",
            "JSON Body:\n{\n  auditor_email: string,\n  auditor_name: string,\n  company_name: string,\n  rating: number (1-5),\n  timeliness_rating: number (1-5),\n  communication_rating: number (1-5),\n  technical_rating: number (1-5),\n  review_comment?: string\n}",
            "{ success: true, message: 'Rating submitted successfully' }"
        ),
        (
            "GET /api/auditors/{email}/reviews",
            "syncRating()\n(AuditorRankRating.tsx)",
            "Path Param: email (string)",
            "{\n  success: true,\n  average_rating: 4.9,\n  total_reviews: 49,\n  rank: 'Rank #1',\n  subcategories: { timeliness: 4.9, communication: 4.9, technical_rigor: 5.0 },\n  reviews: [{ id, company_name, rating, review_comment, created_at }]\n}"
        ),
        (
            "POST /api/auditor/discussions/{id}/reply",
            "handleSendReply()\n(auditor-discussions/page.tsx)",
            "Path Param: id (thread_id)\nJSON Body: { text: string }",
            "{ success: true, message_id: 'm_123', timestamp: 'Just now' }"
        ),
        (
            "GET /api/auditor/settings",
            "AuditorSettingsTabs.tsx",
            "Headers: Authorization Bearer token (Auditor)",
            "AuditorFullSettings JSON (profile, team, preferences, notifications, security)"
        ),
        (
            "PUT /api/auditor/settings",
            "AuditorSettingsTabs.tsx",
            "JSON Body: AuditorFullSettings object",
            "{ success: true, message: 'Auditor settings updated' }"
        )
    ]

    for item in api_rows:
        row_cells = tbl_api.add_row().cells
        for col_idx, text in enumerate(item):
            cell = row_cells[col_idx]
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(8)
            r.font.color.rgb = RGBColor.from_string(DARK_HEX)
            if col_idx == 0:
                r.font.bold = True
                set_cell_background(cell, "F8FAFC")

    # ------------------ SECTION 4: PYTHON FASTAPI IMPLEMENTATION ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("4. Python FastAPI Tax Engine & Pipeline Calculation Service")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "Here is the core Python service logic you can drop into your FastAPI application (`app/services/tax_engine.py`) to compute Sri Lankan corporate income tax, accounting profit, and dynamic pipeline milestones."
    )

    tbl_code = doc.add_table(rows=1, cols=1)
    tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_code.autofit = False
    tbl_code.columns[0].width = Inches(6.7)
    c_cell = tbl_code.cell(0, 0)
    set_cell_background(c_cell, "0F172A")
    set_cell_margins(c_cell, 120, 120, 150, 150)
    p_code = c_cell.paragraphs[0]
    p_code.paragraph_format.space_after = Pt(0)
    p_code.paragraph_format.line_spacing = 1.15

    py_code_str = """# app/services/tax_engine.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TaxComputationResult:
    accounting_pbt: float
    disallowables_add_back: float
    capital_allowances_deduction: float
    taxable_income: float
    cit_rate_percent: float
    indicative_cit_liability: float

def compute_corporate_income_tax(
    gross_revenue: float,
    cost_of_sales: float,
    operating_expenses: float,
    accounting_depreciation: float,
    entertainment_expenses: float,
    tax_depreciation_allowances: float,
    tax_rate_category: str = "standard_30"
) -> TaxComputationResult:
    # 1. Commercial Trading Metrics
    gross_profit = gross_revenue - cost_of_sales
    accounting_pbt = gross_profit - operating_expenses

    # 2. Inland Revenue Act No. 24 - Section 11 Disallowables Add-Back
    # Accounting depreciation is disallowed under Sec 11(1)(b)
    # Entertainment expenses disallowed under Sec 11(1)(c)
    total_disallowables = accounting_depreciation + entertainment_expenses

    # 3. Fourth Schedule Capital Allowances (Tax Depreciation)
    total_allowances = tax_depreciation_allowances

    # 4. Taxable Assessable Income
    taxable_income = max(0.0, accounting_pbt + total_disallowables - total_allowances)

    # 5. Applicable Statutory Rate (Gazette 2311/38)
    rate = 14.0 if tax_rate_category in ["sme_export_14", "manufacturing_14"] else 30.0

    # 6. Final Indicative CIT Liability
    cit_liability = round(taxable_income * (rate / 100.0), 2)

    return TaxComputationResult(
        accounting_pbt=round(accounting_pbt, 2),
        disallowables_add_back=round(total_disallowables, 2),
        capital_allowances_deduction=round(total_allowances, 2),
        taxable_income=round(taxable_income, 2),
        cit_rate_percent=rate,
        indicative_cit_liability=cit_liability
    )

def compute_pipeline_progress(
    documents_count: int,
    processed_count: int,
    is_handed_over: bool,
    auditor_approved_count: int,
    auditor_total_issues: int,
    is_audit_signed_off: bool
) -> Dict[str, any]:
    # Stage 1: Document Gathering (5 Core Checklist Items)
    stage1 = min(100, int((documents_count / 5) * 100))
    # Stage 2: AI OCR Extraction Completeness
    stage2 = int((processed_count / documents_count * 100)) if documents_count > 0 else 0
    # Stage 3: Auditor Handover Pack Submission
    stage3 = 100 if is_handed_over else (100 if stage1 >= 80 else 0)
    # Stage 4: Resolution of Auditor Inquiries
    stage4 = int((auditor_approved_count / auditor_total_issues * 100)) if auditor_total_issues > 0 else 100
    # Stage 5: Final Audit Certification Sign-Off
    stage5 = 100 if is_audit_signed_off else 0

    overall = 100 if is_audit_signed_off else int(
        0.20 * stage1 + 0.20 * stage2 + 0.20 * stage3 + 0.20 * stage4 + 0.20 * stage5
    )
    return {"overall_percent": overall, "stages": [stage1, stage2, stage3, stage4, stage5]}
"""
    r_code = p_code.add_run(py_code_str)
    r_code.font.name = "Consolas"
    r_code.font.size = Pt(8.5)
    r_code.font.color.rgb = RGBColor.from_string("38BDF8")

    # ------------------ SECTION 5: RECOMMENDED REPO STRUCTURE ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("5. Recommended FastAPI Project Structure")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "To keep your backend modular, maintainable, and aligned with Next.js, structure your FastAPI repository as follows:\n\n"
        "taxease-backend/\n"
        "├── app/\n"
        "│   ├── main.py              # FastAPI app initialization, CORS middleware, router registration\n"
        "│   ├── core/                # Config, database connection engine (SQLAlchemy/asyncpg), security JWT\n"
        "│   ├── models/              # SQLAlchemy / SQLModel ORM classes (matching Section 2 tables)\n"
        "│   ├── schemas/             # Pydantic schemas (matching Section 3 API request & response payloads)\n"
        "│   ├── services/            # Business logic (tax_engine.py, document_extractor.py, notifications.py)\n"
        "│   └── routers/             # API routes\n"
        "│       ├── auth.py          # /api/auth/*\n"
        "│       ├── business.py      # /api/dashboard, /api/documents, /api/financials, /api/company/settings\n"
        "│       ├── auditor.py       # /api/auditor/dashboard, /api/auditor/companies, /api/auditor/requests\n"
        "│       ├── discussions.py   # /api/business/discussions, /api/auditor/discussions\n"
        "│       └── notifications.py # /api/notifications/*\n"
        "├── requirements.txt         # fastapi, uvicorn, sqlalchemy, pydantic, python-jose, psycopg2-binary\n"
        "└── .env                     # DATABASE_URL, SECRET_KEY, SUPABASE_KEY\n"
    )

    # Footer
    for section in doc.sections:
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("TaxEaseLK Backend Architecture Specification  •  FastAPI + PostgreSQL")
        r_ft.font.name = "Calibri"
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = RGBColor.from_string("94A3B8")

    filename = "TaxEaseLK_Backend_Architecture_and_API_Specification_Final.docx"
    try:
        doc.save(filename)
        print(f"Document successfully created: {filename}")
    except PermissionError:
        alt_filename = "TaxEaseLK_Backend_Architecture_and_API_Specification_Updated.docx"
        doc.save(alt_filename)
        print(f"Primary file locked by Word. Saved to: {alt_filename}")

if __name__ == "__main__":
    create_backend_doc()
