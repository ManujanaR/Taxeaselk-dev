# -*- coding: utf-8 -*-
"""
Script to generate the maximally-detailed TaxEaseLK_Complete_Frontend_Specification.docx
with deep, exhaustive component-by-component breakdowns for BOTH Business and Auditor portals.
"""
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_exhaustive_specification():
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
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

    def add_callout(text_list, title="SPECIFICATION STANDARD", color_hex=NAVY_HEX, bg_hex="EFF6FF"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(6.8)
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

    def add_section_table(headers, rows):
        tbl = doc.add_table(rows=1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl, "CBD5E1")
        for i, title in enumerate(headers):
            cell = tbl.cell(0, i)
            set_cell_background(cell, "F1F5F9")
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(title)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            r.font.bold = True
            r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

        for item in rows:
            row_cells = tbl.add_row().cells
            for col_idx, text in enumerate(item):
                cell = row_cells[col_idx]
                set_cell_margins(cell, 70, 70, 90, 90)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15
                r = p.add_run(text)
                r.font.name = "Calibri"
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor.from_string(DARK_HEX)
                if col_idx == 0:
                    r.font.bold = True
                    set_cell_background(cell, "F8FAFC")
        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ------------------ COVER / HEADER TITLE ------------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(0)
    p_pre.paragraph_format.space_after = Pt(4)
    run_pre = p_pre.add_run("TAXEASELK MASTER ARCHITECTURE & FUNCTIONAL SPECIFICATION")
    run_pre.font.name = "Calibri"
    run_pre.font.size = Pt(11)
    run_pre.font.bold = True
    run_pre.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(6)
    run_title = p_title.add_run("Exhaustive Component-by-Component Functional & Integration Specification")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor.from_string(DARK_HEX)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run("In-depth technical specification of every tile, formula, data source, modal, button, and dynamic interaction across both the Business Owner Portal (Pvt Ltd) and the External Auditor Portal (CA Sri Lanka / Audit Firm).")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor.from_string(GRAY_HEX)

    # Meta Table
    tbl_meta = doc.add_table(rows=2, cols=4)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_meta, "CBD5E1")
    meta_headers = ["Project", "Application Version", "Portals Covered", "Statutory Standard"]
    meta_values = ["TaxEaseLK", "v1.0 (Next.js 14 + Tailwind)", "Business Owner & External Auditor", "Inland Revenue Act No. 24 of 2017"]
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

    # ------------------ SECTION 1: ARCHITECTURE & COLLABORATION MODEL ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("1. Dual-Portal Architecture & Collaboration Lifecycle")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "TaxEaseLK operates on a strict separation-of-duties collaboration model between corporate tax filers and certified external auditors under Sri Lanka Inland Revenue Act No. 24 of 2017:\n\n"
        "1. Business Owner Portal (Pvt Ltd Finance Team): Acts as the filing client. Sets corporate identity parameters, uploads mandatory statutory files, computes trading and accounting metrics, reviews preliminary Section 11 tax add-backs and Fourth Schedule capital allowances, answers auditor RFIs with evidence, and rates the auditor.\n\n"
        "2. Auditor Portal (Independent CA Sri Lanka / Audit Firm): Acts as the external verifier. Manages a multi-client corporate portfolio, accepts appointment invitations, configures and publishes customized document checklists per client, reviews submitted answers and evidence vouchers in the review queue, inspects OCR confidence scores, conducts multi-threaded discussions, and executes final statutory audit sign-offs."
    )

    add_callout([
        "Complete Specification Standard:",
        "For every single component in both portals, this specification explicitly defines:",
        "1. Element / Tile Identification: Visual component, icons, and layout location.",
        "2. Displayed Content & Logic: What figures, text, badges, and progress indicators are rendered.",
        "3. Data Origin & Calculation Formula: Mathematical formulas (e.g. Accounting Profit = Revenue - Expenses, CIT = Taxable Income * 30%, composite pipeline weighting) and backend endpoints.",
        "4. Interactive Trigger & Downstream Results: What happens on click, what events are dispatched, and how changes immediately cascade to the other portal."
    ], title="SPECIFICATION DEPTH COMMITMENT", color_hex=NAVY_HEX, bg_hex="F0FDF4")

    # ------------------ SECTION 2: COMMON LAYOUT & CHROME ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("2. Common Layout, Top Bar & Global Chrome (Deep Breakdown)")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    chrome_headers = ["Chrome Element", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Cross-Portal Result"]
    chrome_rows = [
        (
            "Business Top Nav Badges\n(Company Name & FY)",
            "Two distinct pills:\n1. [Company Name] (e.g. 'ABC (Pvt) Ltd') in blue\n2. [FY Year] (e.g. 'FY 2025/26') in gray",
            "• Sourced from 'taxease_company_settings' and backend database.\n• Syncs live via 'taxease_company_updated' custom window event.",
            "Changes made in Settings immediately update these top bar badges without page reload, keeping the active corporate context visible on every page."
        ),
        (
            "Auditor Top Nav Bar\n(Multi-Company Selector)",
            "1. 'All Companies' badge\n2. Active Tax Year picker (e.g. '2025/26')\n3. Auditor Rank & Rating Badge",
            "• Sourced from auditor multi-client portfolio registry and localStorage.",
            "Allows the auditor to filter review queues across all assigned clients or toggle to a specific client company."
        ),
        (
            "Business Notifications Panel\n('NotificationBell.tsx')",
            "Bell icon with animated red unread badge ('3', '9+'). Dropdown displays:\n• Auditor Requests for Information (RFIs)\n• Audit Review comments & discrepancy notices\n• Review status milestone changes ('Under Review' -> 'Approved')\n• New discussion replies from assigned auditor\n• Published document checklist updates",
            "• Origin: '/api/notifications?role=business&company_name=...'.\n• Unread badge counter = count of unread items.\n• Automatically refreshes on window focus and storage sync.",
            "• Clicking notification marks item read, decrements counter, and deep-links directly to target page (/auditor-review, /documents, /discussions).\n• 'Mark All as Read' marks all company notifications read.\n• 'View All' routes to Discussions."
        ),
        (
            "Auditor Notifications Panel\n('NotificationBell.tsx')",
            "Bell icon with animated red unread badge ('3', '9+'). Dropdown displays:\n• Client Document Uploads (e.g. 'ABC (Pvt) Ltd uploaded Financial Statements')\n• Client RFI Responses with evidence attachments (e.g. 'ABC (Pvt) Ltd responded to REQ-2026-004')\n• Client Appointment Invitations (e.g. 'New Engagement Request from XYZ Ltd')\n• Client Discussion Inquiries (e.g. 'Inquiry on Entertainment Expenses')\n• Upcoming statutory IRD filing deadline alerts",
            "• Origin: '/api/notifications?role=auditor'.\n• Multi-client feed aggregating events across all assigned portfolio entities.",
            "• Clicking notification marks item read, decrements counter, and deep-links directly to target client page (/responses, /auditor-documents, /auditor-discussions).\n• 'Mark All as Read' clears auditor badge."
        ),
        (
            "Profile Menu & Identity Card\n(Business Side)",
            "Top-right user avatar menu:\n• Avatar circle with initials: 'AU' (Admin User)\n• Role chip: 'Admin'\n• Display Name: 'Admin User'\n• Registered Email: 'admin@abc.lk'\n• Formatted User ID: 'BIZ-XXXXXXXX' with 1-click 'Copy' button\n• Links: Profile & Settings (/settings)\n• Sign Out button",
            "• Sourced from 'taxease_user' session storage and Supabase Auth.\n• User ID formatted with prefix 'BIZ-'.",
            "• Clicking 'Copy' copies User ID to clipboard with toast confirmation.\n• Clicking 'Settings' navigates to '/settings'.\n• Clicking 'Sign Out' clears tokens and redirects to '/sign-in'."
        ),
        (
            "Profile Menu & Identity Card\n(Auditor Side)",
            "Top-right user avatar menu:\n• Avatar circle with initials: 'PA' (Professional Auditor)\n• Role chip: 'Auditor'\n• Display Name: 'Professional Auditor' / Lead Partner Name\n• Registered Email: 'auditor@example.com'\n• Formatted User ID: 'AUD-XXXXXXXX' with 1-click 'Copy' button\n• Links: Profile & Credentials (/auditor-settings)\n• Sign Out button",
            "• Sourced from 'taxease_user' session storage and Supabase Auth.\n• User ID formatted with prefix 'AUD-'.",
            "• Clicking 'Copy' copies Auditor ID to clipboard.\n• Clicking 'Profile' or 'Settings' navigates to '/auditor-settings'.\n• Clicking 'Sign Out' purges session and redirects to '/sign-in'."
        ),
        (
            "Auditor Rank & Rating Badge\n('AuditorRankRating.tsx')",
            "Top Bar badge showing public standing:\n• Rank Chip: 'Rank #1' or 'Verified Auditor'\n• Gold Star Score: e.g. '4.9 ★'\n• Total Reviews Count: e.g. '(49)'\n• Chevron indicator",
            "• Dynamic sync via 'taxease_auditor_rating_updated' event, localStorage, and '/api/auditors/{email}/reviews'.\n• Recalculates live whenever a business client submits a review.",
            "Clicking opens the **Auditor Reputation Drawer** displaying overall rating score (out of 5.0), completed audits count, on-time sign-off rate %, dimension breakdown progress bars (Accuracy %, Responsiveness %, Turnaround %), and verified client review comments."
        ),
        (
            "Language Switcher Toggle\n(EN | සිං | தமி)",
            "Segmented pill toggle:\n• EN (English)\n• සිං (Sinhala)\n• தமி (Tamil)",
            "• Origin: 'LanguageContext.tsx' reading dictionaries in 'translations.ts'.\n• Persisted to localStorage ('taxease_language').",
            "Instantly re-renders all UI headings, labels, and subtitles across the entire application into the selected language without page reload."
        ),
        (
            "Navigation Sidebar",
            "Collapsible sidebar with TaxEaseLK flag emblem logo and structured navigation links.\n• Business: Dashboard, Documents, Financials, Auditor Review, Discussions, Settings.\n• Auditor: Dashboard, Companies, Documents, Responses, Requests, Discussions, Settings.",
            "Highlights active page with blue accent bar and light-blue background fill. Clicking smoothly navigates via Next.js App Router."
        )
    ]
    add_section_table(chrome_headers, chrome_rows)

    # ------------------ SECTION 3: BUSINESS PORTAL ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("3. Business Portal: Deep Component-by-Component Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    # 3.1 Dashboard
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("3.1 Business Dashboard Page ('/dashboard')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    dash_headers = ["Dashboard Element / Tile", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Dynamic Trigger & Downstream Action"]
    dash_rows = [
        (
            "Dashboard Subtitle\n(Company & FY sync)",
            "Subtitle text:\n'Real-time statutory tax compliance dashboard for [Company Name] • Assessment Year [FY]'",
            "• Sourced from 'DashboardSubtitle.tsx' listening to 'taxease_company_updated' event and reading 'taxease_company_settings'.",
            "Instantly updates whenever company legal name or financial year is modified in Settings."
        ),
        (
            "Audit Handover & Verification Pipeline\n(Main Progress Bar)",
            "• Composite Progress Bar displaying overall % (e.g. 65% Complete).\n• Status Chip:\n- <60%: 'Awaiting Documents' (amber)\n- 60-99%: 'Handover In Progress' (blue)\n- 100%: 'Audit Pack Signed Off' (emerald)",
            "• Formula: Overall % = (Stage 1 % * 0.20) + (Stage 2 % * 0.20) + (Stage 3 % * 0.20) + (Stage 4 % * 0.20) + (Stage 5 % * 0.20).\n• Automatically jumps to 100% when auditor executes sign-off.",
            "Recomputes live whenever documents are uploaded, OCR finishes, or auditor resolves inquiry items."
        ),
        (
            "Pipeline Stage 1:\nDocument Gathering",
            "• Title: 'Stage 1: Document Gathering'\n• Ratio: e.g. '4 / 5 Gathered'\n• Progress bar and status icon",
            "• Formula: (Uploaded Checklist Documents / Total Required Documents set by Assigned Auditor) * 100%.\n• Evaluates active files against the company's checklist.",
            "Clicking card routes to '/documents' so user can upload remaining statutory compliance files."
        ),
        (
            "Pipeline Stage 2:\nFinancial Data",
            "• Title: 'Stage 2: Financial Data'\n• Ratio: e.g. '5 / 5 Schedules Ready'\n• Sublabel: 'Income Statement & BS Synced'",
            "• Formula: Based on extraction and population of the 5 financial schedules (P&L, Balance Sheet, Trial Balance, Ledger, Fixed Assets).",
            "Clicking card routes to '/financials' to inspect line-item ledger extractions."
        ),
        (
            "Pipeline Stage 3:\nAI Extraction",
            "• Title: 'Stage 3: AI Extraction'\n• Ratio: e.g. '96% Avg Confidence'\n• Sublabel: 'Zero extraction syntax errors'",
            "• Formula: Mean average of AI confidence scores across all processed document rows: sum(aiConfidencePercent) / count.",
            "Clicking card routes to '/documents' to review any files flagged for human confirmation."
        ),
        (
            "Pipeline Stage 4:\nAuditor Handover",
            "• Title: 'Stage 4: Auditor Handover'\n• Ratio: e.g. 'Pack Dispatched'\n• Sublabel: 'Locked for statutory audit'",
            "• Formula: 100% once business clicks 'Submit Handover Pack to Auditor', or proportionate based on pack readiness.",
            "Clicking card routes to '/auditor-review' to verify handover package status."
        ),
        (
            "Pipeline Stage 5:\nAuditor Inquiries & Sign-Off",
            "• Title: 'Stage 5: Auditor Inquiries'\n• Ratio: e.g. '1 Pending Inquiry' or 'Audit Signed Off'\n• Sublabel: 'BDO Partners / CA Sri Lanka'",
            "• Formula: 100% when auditor sets status to 'Approved' and all inquiries are resolved. Pro-rated as (Resolved Inquiries / Total Inquiries).",
            "Clicking card routes to '/auditor-review' to answer pending auditor requests."
        ),
        (
            "Document Stat Tile\n(Uploaded / Checklist)",
            "• Value: e.g. '4 / 5'\n• Hint: '1 statutory document pending upload' (amber) or 'All statutory docs gathered' (emerald)",
            "• Formula: Value = (Uploaded Checklist Documents) / (Total Required Documents set by Assigned Auditor).",
            "Warns finance team of missing files required by their auditor."
        ),
        (
            "Accounting Profit Tile\n(Revenue - Expenses)",
            "• Value: e.g. 'Rs. 4,600,000'\n• Hint: 'From audited / draft financial statements'",
            "• Formula: Accounting Profit = Gross Turnover - Total Operating Expenses & Cost of Sales.\n• Extracted from Income Statement.",
            "Establishes commercial starting base before tax adjustments."
        ),
        (
            "Auditor Status Tile\n(Waiting / Review / Approved)",
            "• Value: 'Waiting for Submission' | 'Under Review' | 'Approved'\n• Dynamic hint explaining current audit state",
            "• Sourced from assigned auditor state in database and 'taxease_last_audit_status'.\n• Displays 'Approved' when statutory auditor certifies the tax return.",
            "Indicates statutory certification and readiness for IRD RAMIS filing."
        ),
        (
            "Requires Your Attention Card\n(Auditor Inquiries & Notices)",
            "Card displaying list of active auditor queries, discrepancy notices, and documentation requests.\n• Critical severity: Red border & background.\n• Warning severity: Amber border & background.\n• If empty: Emerald 'All Caught Up' badge.",
            "• Directly mirrors open inquiries created by the auditor in Auditor Portal ('/api/auditor-review/issues').\n• Displays Issue Title, description, and direct 'Review' link.",
            "Clicking 'Review' deep-links to '/auditor-review?issue=[issueId]' so business can immediately submit explanations or upload requested supporting invoices."
        )
    ]
    add_section_table(dash_headers, dash_rows)

    # 3.2 Documents Page & Auditor Checklist
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("3.2 Business Documents Page ('/documents') & Auditor-Customized Checklist")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    doc_headers = ["Component / Tile", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    doc_rows = [
        (
            "Category Selection Dropdown",
            "Dropdown above upload zone with categories:\n• Auto-Detect from File Name\n• Financial Statements (Audited / Draft)\n• Trial Balance (12-month final)\n• General Ledger Extracts\n• Fixed Asset Schedule\n• CIT Return / Prior Assessments",
            "• Controlled client state ('selectedCategory').\n• Overrides auto-detection heuristic when user explicitly picks a statutory category.",
            "Ensures uploaded files are immediately tagged with the exact statutory classification required by the auditor."
        ),
        (
            "Auditor Document Checklist\n('AuditorDocumentChecklist.tsx')",
            "Dynamic checklist card customized by appointed auditor:\n• Shows presets: Standard Statutory CIT, BOI & Exporter Pack, or Manufacturing & Trading Pack\n• Custom document requirements added by the auditor\n• Header displays: 'Requested by [Auditor Name] • [Firm Name]'\n• Readiness indicator: (Provided vs. Missing count & Audit Pack Readiness %)",
            "• Sourced from 'taxease_checklist_[companyName]' and backend checklist endpoint.\n• Auto-syncs via 'taxease_checklist_updated' window event whenever the assigned auditor modifies requirements.",
            "• Evaluates uploaded documents against the auditor's required items.\n• Clicking any missing item automatically selects that category in the upload dropdown and focuses the upload zone."
        ),
        (
            "Stat Cards (4 Overview Tiles)",
            "1. Uploaded Count (documents.length)\n2. Processed by AI (status === 'processed')\n3. Review Required (status === 'review_required')\n4. Missing Checklist Count (Math.max(0, totalRequired - fulfilledCount))",
            "• Recomputed live from document state and assigned auditor checklist.",
            "Provides an instant compliance summary before submitting to the auditor."
        ),
        (
            "Document Upload Zone",
            "Dashed drag-and-drop box validating file type (PDF, XLSX, CSV, PNG, JPG) and 10MB size limit.",
            "• Rejects invalid extensions or oversized files with inline banner.",
            "Accepted files enter 'processing' status with animated spinner and trigger AI OCR extraction."
        ),
        (
            "Document Inventory Table",
            "Table displaying:\n• Document Name & Category\n• Live Status Badge ('Processed', 'Review Required', 'Processing')\n• AI Confidence Bar with score %\n• Upload Date & Size\n• Trash Action (Remove)",
            "• Sourced from backend '/api/documents' and local storage.",
            "Clicking trash removes the document, triggers 'taxease_documents_updated', and recomputes stats."
        )
    ]
    add_section_table(doc_headers, doc_rows)

    # 3.3 Financials
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("3.3 Business Financials & Tax Computation Page ('/financials')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    fin_headers = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    fin_rows = [
        (
            "Commercial 5-Metric Grid",
            "1. Gross Turnover (Commercial Inflows)\n2. Cost of Sales (Direct Production Costs)\n3. Gross Profit (Trading Margin %)\n4. Operating OPEX (Admin & Sales Overheads)\n5. Accounting Profit PBT (Revenue - Expenses)",
            "• Extracted from audited/draft Income Statement and ledger schedules.\n• Gross Profit = Revenue - Cost of Sales.\n• Accounting Profit = Gross Profit - Operating Expenses.",
            "Establishes commercial performance benchmarks prior to tax adjustments."
        ),
        (
            "Statutory CIT Waterfall Banner",
            "Reconciliation Waterfall:\n1. Accounting PBT ('Rs. 4.6M')\n2. (+) Disallowables Section 11 ('+Rs. 2.1M')\n3. (-) Capital Allowances 4th Sched ('-Rs. 1.5M')\n4. Taxable Income ('Rs. 5.2M')\n5. Indicative CIT Liability at 30% ('Rs. 1.56M')",
            "• Inland Revenue Act No. 24 of 2017 (Gazette 2311/38).\n• Taxable Income = PBT + Disallowables - Capital Allowances.\n• CIT Liability = Taxable Income * CIT Rate (30% or 14%).",
            "Includes 'Breakdown' toggle expanding Section 11 add-back line items (depreciation, entertainment) and Fourth Schedule capital depreciation."
        ),
        (
            "Interactive Schedules Table",
            "5 sub-tabs: Income Statement, Balance Sheet, Trial Balance, General Ledger, Fixed Assets.",
            "• Displays structured line items with Item Name, Amount (LKR), Source Document, Tax Category, and AI Confidence bar.",
            "Allows detailed verification of balances and tax classifications."
        ),
        (
            "AI Audit Summary Modal",
            "Modal containing executive summary, profitability analysis, full tax reconciliation, compliance risk score, and recommendations.",
            "• Generated by AI parsing of ledger and financial statements.",
            "Allows company finance executives to print a briefing report before meeting the auditor."
        )
    ]
    add_section_table(fin_headers, fin_rows)

    # 3.4 Auditor Review & Rating
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("3.4 Business Auditor Review Page ('/auditor-review') & Rating Engine")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    rev_headers = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    rev_rows = [
        (
            "Assigned Auditor Card",
            "Profile card showing appointed statutory auditor:\n• Auditor Name & Firm (e.g., 'K.L. Perera, FCA' • 'BDO Partners')\n• Professional Badges: 'ICASL Certified', 'CA Sri Lanka Fellow'\n• Review Status Badge ('Waiting for Review', 'Under Review', 'Approved')\n• Review Progress Bar with %\n• Action Buttons: 'Rate Auditor', 'Message Auditor', 'Cancel Engagement'",
            "• Sourced from '/api/auditor-review' and 'taxease_assigned_auditor_[company]'.\n• Progress bar reflects verified checklist items.",
            "• 'Message Auditor' routes to '/discussions'.\n• 'Rate Auditor' launches RateAuditorModal.\n• 'Cancel Engagement' opens confirmation dialog."
        ),
        (
            "Rate Auditor Modal\n(Detailed Rating System)",
            "Comprehensive 5-star modal rating dialog:\n1. Overall Satisfaction: 1 to 5 interactive Gold Stars with dynamic descriptions (Needs Improvement, Fair, Good, Very Good, Exceptional)\n2. Dimension 1: Timeliness (Slider 1-5 for SLA & RAMIS deadlines)\n3. Dimension 2: Communication (Slider 1-5 for inquiry clarity & response speed)\n4. Dimension 3: Tax Rigor (Slider 1-5 for statutory compliance & accuracy)\n5. Client Review Comment Textarea\n6. Submit Button: 'Submit X★ Review'",
            "• Submits POST to '/api/auditors/rate'.\n• Updates 'taxease_auditor_rating' and dispatches 'taxease_auditor_rating_updated' event.\n• Recalculates auditor's public average score:\nNew Rating = ((Old Avg * Count) + Given Rating) / (Count + 1).",
            "Instantly updates the auditor's top bar Rank & Rating badge ('AuditorRankRating.tsx') and appends client review to the auditor's verified reputation drawer."
        ),
        (
            "Auditor Inquiries & Exceptions Manager",
            "Interactive list of issues/queries raised by auditor during inspection:\n• Issue Title & Severity Badge (Critical vs Pending Clarification)\n• Auditor Comment text\n• Company Response Textarea\n• File Attachment Upload (invoices/vouchers)\n• 'Submit Explanation & Resolve' button",
            "• Sourced from '/api/auditor-review/issues'.\n• Directly tied to Dashboard 'Requires your attention' card.",
            "Submitting explanation resolves the inquiry, notifies auditor in '/responses', and clears dashboard warning."
        )
    ]
    add_section_table(rev_headers, rev_rows)

    # 3.5 Discussions & 3.6 Settings
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("3.5 Business Discussions ('/discussions') & 3.6 Settings ('/settings')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    bother_headers = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    bother_rows = [
        (
            "Business Discussions Page\n('/discussions')",
            "• Active Auditor Banner with direct contact details.\n• Topic Threads List (categorized by Tax Computation, Fixed Assets, etc.) with unread badge.\n• 'New Discussion' (+) button.\n• Message stream with Auditor (left) vs Company (right) bubbles and timestamps.\n• Bottom Reply composer.",
            "• Sourced from '/api/business/discussions'.\n• Real-time or polling sync.",
            "Sending a message transmits it to the auditor's '/auditor-discussions' page and triggers top bar notification for the auditor."
        ),
        (
            "Business Settings & Profile\n('/settings')",
            "Comprehensive settings form with:\n• Company Name & Trading Name\n• ROC Registration Number (PV)\n• IRD TIN Number\n• VAT & SVAT Registration Numbers & Toggle\n• CIT Tax Rate Category (30% Standard vs 14% SME Concessionary)\n• Financial Year (e.g. '2025/26')\n• Contact Email & Phone, Registered Address, Industry Sector\n• Team & Users tab with role permissions",
            "• Sourced from 'taxease_company_settings' and backend database.",
            "Saving immediately dispatches 'taxease_company_updated' event, updating Top Nav Badges, Dashboard subtitle, and report titles without page reload."
        )
    ]
    add_section_table(bother_headers, bother_rows)

    # ------------------ SECTION 4: AUDITOR PORTAL (MAXIMAL DETAIL) ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("4. Auditor Portal: Exhaustive Component-by-Component Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    # 4.1 Auditor Dashboard
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.1 Auditor Dashboard Page ('/auditor-dashboard')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    adash_headers = ["Dashboard Element / Card", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Dynamic Trigger & Downstream Action"]
    adash_rows = [
        (
            "Stat Tile 1:\nActive Clients Tile",
            "• Value: e.g. '14'\n• Sublabel: 'Active companies under your review'\n• Action Button: 'View Companies'",
            "• Total count of corporate taxpayer clients assigned to this auditor firm in database.\n• Sourced from '/api/auditor/dashboard'.",
            "Clicking 'View Companies' routes to '/companies' management directory."
        ),
        (
            "Stat Tile 2:\nPending Reviews Tile",
            "• Value: e.g. '6'\n• Sublabel: 'CIT computations currently under review'\n• Action Button: 'Review Queue'",
            "• Count of companies currently in 'Under Review' or 'Ready for Auditor' status.\n• Sourced from '/api/auditor/dashboard'.",
            "Clicking 'Review Queue' routes to '/responses' / Review Queue."
        ),
        (
            "Stat Tile 3:\nCompleted Reviews Tile",
            "• Value: e.g. '8'\n• Sublabel: 'Reviews completed this period'\n• Action Button: 'View All'",
            "• Count of corporate tax returns certified and signed off ('Approved') by this auditor during active tax cycle.",
            "Serves as audit milestone tracker and billing completion indicator."
        ),
        (
            "Priority Reviews Card\n('AuditorPriorityReviews.tsx')",
            "List of corporate files requiring urgent auditor intervention:\n• Company Name\n• Severity Tag: 'CRITICAL' (red), 'ATTENTION' (amber), 'READY' (green), 'APPROVED' (emerald)\n• Detail note (e.g. '2 unverified fixed asset additions', 'Awaiting client response to invoice query')\n• Pack Progress Bar with %\n• Due Date countdown chip (e.g. 'Due in 3 days')\n• Direct Action Buttons: 'Approve' (instant sign-off) and 'Review' (deep-link)",
            "• Sourced from '/api/auditor/priority-reviews'.\n• Sorted by filing deadline proximity and issue severity.",
            "• Clicking 'Approve' immediately signs off the return, sets progress to 100%, and records real-time activity.\n• Clicking 'Review' deep-links directly into that company's audit pack and response items."
        ),
        (
            "Auditor Workload Queue Card",
            "Structured workload queue breakdown rows:\n• Pending (gray count)\n• Under Review (blue count)\n• Waiting for Company (amber count)\n• Ready for Auditor Approval (purple count)\n• Completed (emerald count)\n• 'Open Review Queue' button",
            "• Live count of corporate files across each stage of the audit lifecycle.",
            "Clicking 'Open Review Queue' routes to the filterable review queue."
        ),
        (
            "Recent Audit Activity Card\n('AuditorRecentActivityCard.tsx')",
            "Real-time activity feed:\n• Event Title (e.g. 'Document Uploaded', 'RFI Responded', 'CIT Computation Approved', 'Audit Checklist Updated')\n• Client Company Name\n• Timestamp (e.g. 'Just now', '12m ago', '2h ago')\n• Tone Icon (success green, warning amber, info blue)",
            "• Real-time log of client actions and audit certifications across all assigned entities.",
            "Allows lead partner to monitor team activities and incoming client submissions."
        )
    ]
    add_section_table(adash_headers, adash_rows)

    # 4.2 Companies Management Page
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.2 Auditor Companies Management Page ('/companies' & 'CompaniesManager.tsx')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    comp_headers = ["Feature / Sub-Component", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    comp_rows = [
        (
            "Client Invitations Banner & Modal",
            "Top banner / button showing pending engagement invites from business owners (e.g. '2 New Client Invitations').\n• Modal displays:\n- Company Name & ROC Reg No\n- Sender Representative Name & Email\n- Tax Year & Estimated Turnover (e.g. 'Rs. 25.0M')\n- 'Accept Appointment' & 'Decline' actions\n- Filter tabs: 'ALL', 'PENDING', 'ACCEPTED'",
            "• Sourced from '/api/auditor/invitations'.\n• Populated when businesses click 'Invite Auditor' on '/auditor-review'.",
            "• 'Accept Appointment' formally establishes auditor engagement, moves company into active client list, and notifies business.\n• 'Decline' archives the request."
        ),
        (
            "Search & Add Company Modal",
            "• Search bar: Filters by company name, TIN, and category.\n• 'Add Company' button opening modal:\n  - Company Legal Name\n  - ROC Registration Number (PV)\n  - IRD TIN Number\n  - Fiscal Year (2025/26)\n  - Contact Email & Phone\n  - 'Add to Portfolio' button",
            "• Adds company directly into auditor's client registry.",
            "Instantly appends company to table, allowing immediate document requests and audit onboarding."
        ),
        (
            "Companies Directory Table",
            "Master table with columns:\n• Company Name (with legal icon)\n• TIN Number & Copy button\n• Financial Year badge\n• CitStatusBadge ('Draft', 'Under Review', 'Ready for Auditor', 'Approved', 'Waiting for Company')\n• Issue Count Pair (Critical in red / Warning in amber)\n• Pack Progress Bar (% with color coding)\n• Filing Due Date (with countdown chip)\n• Actions: 'View Profile' & 'Open Checklist'",
            "• Sourced from '/api/auditor/companies'.\n• CitStatusBadge applies color tokens matching platform status hierarchy.\n• IssueCountPair summarizes open audit findings.",
            "• 'View Profile' opens complete corporate drawer with contact details, address, turnover, and assigned tax office.\n• 'Open Checklist' launches AuditorChecklistModal."
        ),
        (
            "Auditor Document Checklist Manager\n('AuditorChecklistModal.tsx')",
            "Interactive modal allowing the assigned auditor to create, configure, and publish a company-specific document checklist:\n• Preset Packs:\n  1. Standard Statutory CIT Pack (Financial Statements, Trial Balance, Ledger, Assets, Prior CIT)\n  2. BOI & Exporter Pack (Adds BOI Agreements, Export Realization Certificates, Customs CUSDEC)\n  3. Manufacturing & Trading Pack (Adds Physical Stock Valuation, WHT/AIT Sched 10 Certificates)\n• Custom Document Creator: Auditor can add custom required/optional items with specific audit instructions/notes.\n• Save & Publish: Publishes checklist directly to the company's Documents page via '/api/auditor/checklists' and 'taxease_checklist_[companyName]'.",
            "• Sourced from 'taxease_checklist_[companyName]' and backend checklist repository.\n• Automatically synchronizes with the business user's 'AuditorDocumentChecklist.tsx' component via custom window events.",
            "• When the auditor clicks 'Save & Publish', the company's Documents page and Dashboard instantly update to require these specific documents.\n• Company checklist readiness is calculated against this auditor-created list."
        )
    ]
    add_section_table(comp_headers, comp_rows)

    # 4.3 Review Queue & Responses
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.3 Auditor Review Queue & Client Responses Page ('/responses')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    resp_headers = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    resp_rows = [
        (
            "Workflow Filter Tabs",
            "Four segmented filter buttons:\n• All Responses (total count)\n• Unreviewed (amber pill)\n• Resolved (emerald pill)\n• Revision Requested (red pill)",
            "• Filter state: 'activeFilter'.\n• Recomputes counts live from active response set.",
            "Filters response cards instantly so auditor can focus on uninspected evidence."
        ),
        (
            "Client Response Cards",
            "Structured inspection card per client submission:\n• RFI Reference Code (e.g. 'REQ-2026-004')\n• RFI Title & Category\n• Client Company Name (with building icon)\n• Submitter Name & Submission Timestamp\n• Client Explanation Note box\n• Attached Evidence Files list (PDF, XLSX with file size and Download button)\n• Status Badge ('Unreviewed', 'Resolved', 'Revision Requested')",
            "• Sourced from '/api/auditor/responses'.\n• Populated when business answers an inquiry on '/auditor-review'.",
            "• Auditor clicks 'Download' to inspect attached invoices/schedules.\n• Provides two review actions:\n1. 'Mark as Resolved'\n2. 'Request Revision'"
        ),
        (
            "Mark as Resolved Action",
            "Button: 'Mark as Resolved' with green checkmark icon.",
            "• Calls 'resolveAuditorResponse(id)'.\n• Sets response status to 'resolved'.",
            "Removes blocker, increments resolved audit count, and sends confirmation notification to business."
        ),
        (
            "Request Revision Modal",
            "Button: 'Request Revision' opening modal dialog:\n• Revision feedback textarea explaining what is missing (e.g. 'Please provide official tax invoice with VAT registration number')\n• 'Send Revision Request' button",
            "• Calls 'requestAuditorRevision(id, note)'.\n• Sets status to 'revision_requested'.",
            "Sends revision notice back to the business dashboard attention list so client can re-upload."
        )
    ]
    add_section_table(resp_headers, resp_rows)

    # 4.4 Requests for Information
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.4 Auditor Requests for Information (RFI) Page ('/requests')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    req_headers = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    req_rows = [
        (
            "Stat Cards (4 Overview Tiles)",
            "• Total Requests\n• Pending\n• Responded\n• Resolved",
            "• Formula: Computed dynamically from 'requests' array based on status property.",
            "Provides quick metrics on audit inquiry clearance rate."
        ),
        (
            "Create New Request Modal\n('New Request' button)",
            "Modal form:\n• Target Company dropdown\n• Request Title (e.g. 'Bank Confirmation Letters')\n• Category (Financial Statements, Fixed Assets, Tax Reliefs, General Inquiry)\n• Priority Level: High (red), Medium (amber), Low (blue)\n• Submission Due Date\n• Detailed Instructions Textarea\n• 'Send Request' button",
            "• POSTs to '/api/auditor/requests'.\n• Writes record to database.",
            "• Dispatches notification to company top bar bell.\n• Adds urgent item to business dashboard 'Requires your attention' card."
        ),
        (
            "Requests Management Table",
            "Table displaying all RFIs:\n• Reference Code (e.g. 'REQ-2026-003')\n• Client Company\n• Title & Description\n• Category\n• Priority Badge\n• Due Date (with overdue highlight if expired)\n• Status Badge ('Pending', 'Responded', 'Resolved')\n• 'Send Reminder' button",
            "• Sourced from '/api/auditor/requests'.\n• Filterable via live search query.",
            "Clicking 'Send Reminder' dispatches a high-priority push/email notification to the company finance director."
        )
    ]
    add_section_table(req_headers, req_rows)

    # 4.5 Auditor Documents
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.5 Auditor Documents Repository Page ('/auditor-documents')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    adoc_headers = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    adoc_rows = [
        (
            "Client Document Packs Grid",
            "Card per assigned client company displaying:\n• Company Name\n• Document Pack Completion % (e.g. 80%)\n• Total Files Count\n• Pending Verification count vs Verified count\n• 'Open Company Pack' drill-down button",
            "• Aggregated from multi-company document repository.\n• Pack completion based on fulfilled checklist items.",
            "Clicking card drills down into that company's full document inventory."
        ),
        (
            "Document Drill-Down Table",
            "Comprehensive file inventory table:\n• File Name & Document Type\n• AI OCR Confidence Bar with score % (color-coded: Green >=95%, Amber 85-94%, Red <85%)\n• Upload Date & File Size\n• Status Badge ('Review Required' vs 'Verified')\n• Action Buttons: 'Verify' (Checkmark) and 'Request Missing Document'",
            "• Sourced from client uploaded document store.",
            "Auditor clicks 'Verify' on a file to confirm figures match trial balance; updates file status to 'verified' with green badge."
        )
    ]
    add_section_table(adoc_headers, adoc_rows)

    # 4.6 Auditor Discussions
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.6 Auditor Discussions Page ('/auditor-discussions') - Multi-Client Chat")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    adisc_headers = ["Feature / Sub-Component", "Displayed Content & Logic", "Data Origin & Backend Flow", "Interaction & Behavior"]
    adisc_rows = [
        (
            "Multi-Client Threads Pane\n(Left Panel)",
            "Scrollable list of conversation threads across all assigned companies:\n• Company Name badge (with Building icon)\n• Discussion Topic title\n• Last message preview snippet\n• Timestamp & Unread message counter badge\n• Status indicator ('Open' vs 'Closed')",
            "• Sourced from '/api/auditor/discussions'.\n• Filterable via real-time search box above the list.",
            "Clicking any thread loads its complete message history in the right-hand conversation viewer."
        ),
        (
            "Search & Filter Bar",
            "Search input with search icon located above thread list.\nPlaceholder: 'Search discussions...'",
            "• Client-side filter matching both company names and topic titles.",
            "Filters threads in real time as the auditor types, enabling quick access across large client portfolios."
        ),
        (
            "Active Conversation Header\n& Status Toggle",
            "Header of the selected discussion displaying:\n• Company Name & Topic Title\n• Thread Status Badge ('Open' in green / 'Closed' in gray)\n• Status Toggle Action: 'Mark as Closed' or 'Reopen Thread'",
            "• Status stored in thread state and database.",
            "Auditor can formally close resolved inquiries or reopen threads if follow-up clarifications are required."
        ),
        (
            "Message Stream Viewer",
            "Chronological message stream with distinct bubble styling:\n• Auditor messages: Displayed on the right in blue/navy bubble with timestamp.\n• Company messages: Displayed on the left in white/gray bubble with client sender name and timestamp.\n• Auto-scrolls to the latest message.",
            "• Sourced from thread message array.\n• Auto-refreshes on incoming messages.",
            "Provides transparent communication history accessible during audit defense."
        ),
        (
            "Auditor Reply Composer",
            "Bottom reply bar with textarea input and 'Send Reply' button (with Send icon).\nPlaceholder: 'Type a reply to [Company Name]...'",
            "• Appends new message to thread state immediately.\n• Submits POST to '/api/auditor/discussions/{thread_id}/reply'.\n• Emits notification to the client company.",
            "Transmits technical audit advice directly to the company's finance team without leaving the portal."
        )
    ]
    add_section_table(adisc_headers, adisc_rows)

    # 4.7 Audit Log
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.7 Compliance Audit Log Page ('/audit-log')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    alog_headers = ["Component / Feature", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    alog_rows = [
        (
            "Filter Bar",
            "Filter pills for:\n• Company Name\n• Company User / Actor\n• Event Type (Approval, Upload, RFI, Sign-off)\n• Date Range\n• Financial Year",
            "• Sourced from audit log query filters.",
            "Filters log entries to isolate specific transactions during compliance inquiries."
        ),
        (
            "Immutable Audit Trail Table",
            "Columns:\n• Timestamp (ISO date and time)\n• Company Name\n• Actor (User name and role: Lead Auditor, Finance Director)\n• Event Type Badge (Success in green, Warning in amber, Info in blue, Pending in gray)\n• Event Details (Verbatim description of compliance action)",
            "• Sourced from '/api/auditor/audit-log'.\n• Append-only ledger recording all key compliance transactions.",
            "Satisfies statutory record-keeping requirements under the Sri Lanka Inland Revenue Act and provides evidentiary audit defense."
        )
    ]
    add_section_table(alog_headers, alog_rows)

    # 4.8 Auditor Settings
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.8 Auditor Settings Page ('/auditor-settings' & 'AuditorSettingsTabs.tsx')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    asett_headers = ["Settings Tab", "Fields, Controls & Logic", "Data Origin & Backend Flow", "Downstream Impact"]
    asett_rows = [
        (
            "Tab 1: Profile & Credentials",
            "• Full Name, Work Email, Phone, Designation\n• Professional License Number\n• CA Sri Lanka / ICASL Member Number\n• IRD Tax Practitioner Registration Number\n• Firm Registration Number & Office Address\n• Digital Signature / Rubber Stamp Upload (with image preview)",
            "• Sourced from 'AuditorProfileSettings' model and localStorage ('taxease_auditor_profile').",
            "Maintains authenticated professional credentials stamped onto certified client tax returns."
        ),
        (
            "Tab 2: Firm & Team Management",
            "• Audit team hierarchy table: Audit Partner, Senior Auditor, Audit Assistant, Tax Specialist\n• Columns: Name & Initials, Email, Role Badge, Assigned Companies Count, Status ('Active' / 'Invited')\n• 'Invite Team Member' button & modal (Name, Email, Role)",
            "• Sourced from firm user directory.",
            "Allows audit firms to delegate client company portfolios across senior auditors and assistants."
        ),
        (
            "Tab 3: Audit Preferences",
            "• Default Tax Year (e.g. '2025/26')\n• Accounting Standard dropdown ('SLFRS / LKAS for SMEs' vs 'Full SLFRS')\n• Materiality Threshold Percentage slider (e.g. 5%)\n• Automated Client Reminder Schedules (days before deadline)\n• Auto-Request Standard Pack toggle\n• Strict VAT/SVAT Reconciliation toggle",
            "• Configures firm-wide auditing rules applied across client tax calculations.",
            "Controls automated reminder dispatches and default checklist templates."
        ),
        (
            "Tab 4: Notifications",
            "Granular notification channel toggles:\n• Client Document Uploaded\n• Client Response Received\n• Discussion Message Received\n• Deadline Approaching\n• Client Invitation Received\n• Digest Frequency picker ('Instant', 'Daily Digest', 'Weekly')",
            "• Controls email and in-app notification triggers for the auditor.",
            "Ensures audit partners stay informed on client submissions without alert fatigue."
        ),
        (
            "Tab 5: Security & Access",
            "• Two-Factor Authentication (2FA) switch\n• Session Timeout duration (minutes)\n• IP Whitelist toggle\n• Immutable Audit Trail enforcement toggle\n• Active Devices & Sessions table (Device, Browser, IP, Last Active, 'Revoke' action)",
            "• Firm security policy and device authorization store.",
            "Guarantees compliance with professional data protection and confidentiality mandates."
        )
    ]
    add_section_table(asett_headers, asett_rows)

    # 4.9 Rating & Reputation Engine
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.9 Assigned Auditor Rating & Reputation Engine (Deep Breakdown)")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    rate_headers = ["Rating Component / Flow", "Displayed Elements & Controls", "Calculation Algorithm & Formulas", "Downstream Platform Effect"]
    rate_rows = [
        (
            "Rate Auditor Modal\n(Business Side)",
            "1. Overall Star Rating: 1 to 5 interactive Gold Stars with tier descriptions (Needs Improvement, Fair, Good, Very Good, Exceptional)\n2. Dimension 1: Timeliness (Slider 1-5 for SLA & RAMIS deadlines)\n3. Dimension 2: Communication (Slider 1-5 for inquiry clarity & response speed)\n4. Dimension 3: Tax Rigor (Slider 1-5 for statutory compliance & accuracy)\n5. Client Review Comment Textarea\n6. Submit Button: 'Submit X★ Review'",
            "• Submits POST to '/api/auditors/rate'.\n• Updates 'taxease_auditor_rating' and dispatches 'taxease_auditor_rating_updated' event.\n• Recalculates auditor's public average score:\nNew Rating = ((Old Avg * Count) + Given Rating) / (Count + 1).",
            "Instantly updates the auditor's top bar Rank & Rating badge and appends client review to the auditor's verified reputation drawer."
        ),
        (
            "Auditor Rank & Rating Badge\n(Auditor Top Bar)",
            "Pill badge showing:\n• Rank: 'Rank #1' or 'Verified Auditor'\n• Gold Star Score: e.g. '4.9 ★'\n• Total Reviews Count: e.g. '(49)'",
            "• Sourced from '/api/auditors/{email}/reviews'.\n• Re-renders live upon new client review submission.",
            "Visible on every auditor page, establishing professional credibility."
        ),
        (
            "Auditor Reputation Drawer\n('AuditorRankRating.tsx')",
            "Comprehensive reputation drawer displaying:\n1. Overall rating score (out of 5.0)\n2. Total completed audits counter (e.g. 143)\n3. On-time sign-off rate % (e.g. 99.4%)\n4. Dimension breakdown progress bars: Accuracy %, Responsiveness %, Turnaround %\n5. Verified recent client reviews list with company names, star scores, service titles, and feedback comments.",
            "• Breakdown percentages:\nAccuracy % = (technical_rigor / 5.0) * 100.\nResponsiveness % = (communication / 5.0) * 100.\nTurnaround % = (timeliness / 5.0) * 100.",
            "Allows the auditor to inspect their firm's verified performance metrics and review feedback from corporate clients."
        )
    ]
    add_section_table(rate_headers, rate_rows)

    # ------------------ SECTION 5: MASTER DATA FLOW & INTEGRATION MATRIX ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("5. Master Data Flow & Cross-Portal Integration Matrix")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    matrix_headers = ["UI Element / Tile", "Portal & Location", "Mathematical Formula / Logic", "Data Origin & Trigger", "Downstream Platform Impact"]
    matrix_rows = [
        (
            "Company & FY Badges",
            "Top Navigation Bar (Business)",
            "Displays [Company Name] and [FY Year] from active settings profile.",
            "Settings -> 'taxease_company_settings' via 'taxease_company_updated' event.",
            "Keeps active corporate taxpayer context visible on every page."
        ),
        (
            "Notification Bell (Business)",
            "Top Navigation Bar (Business)",
            "Unread counter = count of unread notifications. Decrements on click.",
            "Grabs auditor RFIs, inquiry comments, audit status changes, and discussion replies.",
            "Alerts company finance team to outstanding auditor inquiries."
        ),
        (
            "Notification Bell (Auditor)",
            "Top Navigation Bar (Auditor)",
            "Unread counter = count of unread notifications. Decrements on click.",
            "Grabs client uploads, RFI responses, appointment invites, and discussion replies.",
            "Alerts auditor to incoming client submissions across portfolio."
        ),
        (
            "Profile Menu & User ID",
            "Top Navigation Bar (Both Portals)",
            "Avatar initials, Name, Email, Role chip ('Admin'/'Auditor'), Copyable ID ('BIZ-' / 'AUD-').",
            "Sourced from 'taxease_user' session storage and Supabase Auth.",
            "Provides user identity, clipboard ID copy, settings link, and secure logout."
        ),
        (
            "Auditor Rank & Rating Badge",
            "Top Navigation Bar (Auditor)",
            "Rank label ('Rank #1'), Overall rating ('4.9 ★'), Total reviews count. Drawer displays breakdown.",
            "Updated when client submits review via RateAuditorModal; recomputes average rating.",
            "Showcases auditor's verified public reputation and on-time compliance performance."
        ),
        (
            "Auditor Document Checklist Manager",
            "Companies Page (Auditor)",
            "Auditor configures and publishes custom document checklist per company (presets or custom items).",
            "AuditorChecklistModal -> '/api/auditor/checklists' & 'taxease_checklist_[companyName]'.",
            "Directly dictates the business user's Document Checklist and Stage 1 upload requirements."
        ),
        (
            "Auditor Document Checklist",
            "Documents Page (Business)",
            "Readiness % = (Provided Required / Total Required set by Auditor) * 100%.",
            "Syncs via 'taxease_checklist_updated' window event and backend checklist endpoint.",
            "Guides business on exact files requested by their appointed auditor."
        ),
        (
            "Pipeline Progress Bar",
            "Dashboard (Business)",
            "Overall % = 20% * (Stage 1 + Stage 2 + Stage 3 + Stage 4 + Stage 5). Jumps to 100% on Sign-off.",
            "DashboardSummary.steps[] + 'taxease_audit_status_updated'.",
            "Provides executive gauge of corporate audit handover readiness."
        ),
        (
            "Accounting Profit Tile",
            "Dashboard (Business)",
            "Accounting Profit = Gross Revenue (Turnover) - Total Operating Expenses.",
            "Extracted from Income Statement / Audited Accounts.",
            "Transfers directly into Step 1 of Statutory CIT Computation."
        ),
        (
            "Auditor Status Tile",
            "Dashboard (Business)",
            "Displays 'Waiting for Submission' | 'Under Review' | 'Approved'.",
            "Updated when Auditor changes review status in Auditor Portal.",
            "Indicates statutory certification and readiness for IRD RAMIS filing."
        ),
        (
            "Auditor Inquiries & Issues",
            "Auditor Review (Business) / Responses (Auditor)",
            "Auditor raises inquiry -> Business answers with note & vouchers -> Auditor resolves or requests revision.",
            "'/api/auditor-review/issues' and '/api/auditor/responses'.",
            "Resolves statutory discrepancies before final tax return certification."
        ),
        (
            "Auditor Discussions",
            "Discussions (Auditor & Business)",
            "Multi-client thread selector, status toggle ('Open'/'Closed'), Auditor vs Company bubbles, reply composer.",
            "'/api/auditor/discussions' and '/api/business/discussions'.",
            "Provides authenticated direct chat between auditor and client."
        ),
        (
            "Auditor Settings (5 Tabs)",
            "Auditor Settings (Auditor)",
            "Profile & Credentials, Firm & Team, Audit Preferences, Notifications, Security & Access.",
            "Sourced from 'AuditorFullSettings' model and localStorage.",
            "Configures firm-wide practice credentials, materiality thresholds, and team delegation."
        )
    ]
    add_section_table(matrix_headers, matrix_rows)

    # Footer
    for section in doc.sections:
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("TaxEaseLK Complete Platform Specification  •  Confidential & Proprietary")
        r_ft.font.name = "Calibri"
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = RGBColor.from_string("94A3B8")

    target_files = [
        "TaxEaseLK_Frontend_Functional_Specification_Final.docx",
        "TaxEaseLK_Complete_Frontend_and_Auditor_Portal_Specification.docx"
    ]
    for fn in target_files:
        try:
            doc.save(fn)
            print(f"Document successfully created: {fn}")
        except PermissionError:
            alt_fn = fn.replace(".docx", "_Updated.docx")
            doc.save(alt_fn)
            print(f"Primary file {fn} was locked. Saved to {alt_fn} instead.")

if __name__ == "__main__":
    create_exhaustive_specification()
