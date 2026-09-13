# -*- coding: utf-8 -*-
"""
Script to generate TaxEaseLK_Frontend_Functional_Specification.docx
"""
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = Document()

    # Set page margins (1 inch all around)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # Color definitions
    NAVY_HEX = "1E3A8A"
    BLUE_HEX = "2563EB"
    DARK_HEX = "0F172A"
    GRAY_HEX = "475569"
    LIGHT_BG_HEX = "F8FAFC"
    BORDER_HEX = "CBD5E1"
    ACCENT_GREEN = "059669"
    ACCENT_AMBER = "D97706"
    ACCENT_RED = "DC2626"

    # Helper XML shading & border functions
    def set_cell_background(cell, color_hex):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

    def set_table_borders(table, color_hex="E2E8F0"):
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

    def add_callout(text_list, title="SPECIFICATION NOTE", color_hex=NAVY_HEX, bg_hex="EFF6FF"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(6.7)
        cell = tbl.cell(0, 0)
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

        # Left border highlight
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
    run_pre = p_pre.add_run("TAXEASELK PLATFORM SPECIFICATION")
    run_pre.font.name = "Calibri"
    run_pre.font.size = Pt(11)
    run_pre.font.bold = True
    run_pre.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(6)
    run_title = p_title.add_run("Frontend Functional Explanations & Component Requirement Specification")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor.from_string(DARK_HEX)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run("Comprehensive element-by-element functional definition, formulas, data origin mappings, auditor interactions, and dynamic pipeline behaviors for Business and Auditor portals.")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor.from_string(GRAY_HEX)

    # Meta Table
    tbl_meta = doc.add_table(rows=2, cols=4)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_meta, "CBD5E1")
    meta_headers = ["Project", "Application Version", "Scope Covered", "Target Roles"]
    meta_values = ["TaxEaseLK", "v1.0 (Next.js 14 + Tailwind)", "Full Frontend Architecture", "Business Owner & Statutory Auditor"]
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

    # ------------------ EXECUTIVE OVERVIEW ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("1. Executive Platform Architecture & How Explanations Are Formatted")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "TaxEaseLK is an integrated digital Corporate Income Tax (CIT) compliance and audit handover ecosystem built specifically "
        "for Sri Lankan private limited companies (Pvt Ltd) and registered audit practitioners under the Inland Revenue Act No. 24 of 2017. "
        "The frontend is architected into two distinct, high-efficiency portals sharing common layout design tokens, an i18n localization engine (English, Sinhala, Tamil), "
        "and a synchronized state layer:\n"
        "1. Business Owner Portal: Equips corporate finance teams to manage statutory tax settings, upload and OCR-extract mandatory tax documents, compute trading metrics, monitor statutory add-backs/capital allowances, and securely collaborate with their assigned statutory auditor.\n"
        "2. Auditor Portal: Empowers chartered accountants and audit firms to oversee multi-client portfolios, issue Requests for Information (RFI), review client responses and attached evidence, verify corporate tax packs, and execute formal audit sign-offs."
    )

    add_callout([
        "This document follows the exact specification format demonstrated in the platform requirements review:",
        "• Element & Tile Identification: Identifies the exact UI label, component, and location on the screen.",
        "• Data Source & Sync Logic: Explains whether the data is sourced from Settings, Supabase backend, local browser storage, or live events.",
        "• Mathematical Formula / Business Rule: Explains the exact formula (e.g. Accounting Profit = Revenue - Expenses, Uploaded / Checklist Count, Weighted Pipeline Stages).",
        "• Trigger & User/Auditor Actions: Clarifies who updates the state, what inputs or actions trigger recalculation, and how updates cascade."
    ], title="SPECIFICATION STANDARD", color_hex=NAVY_HEX, bg_hex="F0FDF4")

    # ------------------ SECTION 2: COMMON LAYOUT & CHROME ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("2. Common Layout, Top Bar & Global Chrome Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The top navigation bar and layout chrome remain persistent across both portals, ensuring consistent situational awareness, live synchronization, and zero-latency role detection."
    )

    tbl_chrome = doc.add_table(rows=1, cols=4)
    tbl_chrome.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_chrome, "CBD5E1")
    chrome_cols = ["Chrome Element", "Displayed Content & Logic", "Data Origin & Sync Flow", "Interactive Action & Result"]
    for i, title in enumerate(chrome_cols):
        cell = tbl_chrome.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    chrome_rows = [
        (
            "Business Top Nav Badges\n(Company Name & FY)",
            "Displays two pill badges:\n1. [Company Name] (e.g., 'ABC (Pvt) Ltd')\n2. [FY Year] (e.g., 'FY 2025/26')",
            "• Origin: Settings -> Company Profile.\n• Sync: Listens to 'taxease_company_updated' custom window event and localStorage ('taxease_company_settings').\n• Immediate update upon user saving settings without page reload.",
            "Visual indicator of active corporate tax context. Keeps finance staff aware of exactly which corporate tax entity and assessment year they are operating under."
        ),
        (
            "Auditor Top Nav Bar\n(Multi-Company Selector)",
            "Displays 'All Companies' badge and active Tax Year dropdown.",
            "• Origin: Auditor multi-client portfolio data (cached in localStorage and Supabase company registry).",
            "Allows auditor to toggle between consolidated view across all assigned clients or filter down to a single corporate entity."
        ),
        (
            "Notification Bell & Unread Counter",
            "Bell icon with dynamic red badge showing count of unread notifications (e.g., '3', '9+'). Clicking opens a rich dropdown panel.",
            "• Origin: '/api/notifications' (filtered by active role & company name).\n• Business grab: Auditor RFIs, review comments, status changes, new discussion messages.\n• Auditor grab: Client document uploads, RFI responses, discussion messages, appointment invites.",
            "• Clicking notification marks item as read, decrements counter, and deep-links directly to target page (/auditor-review, /responses, /discussions).\n• Includes 'Mark All as Read' and 'View All' actions."
        ),
        (
            "Language Switcher Toggle\n(EN | සිං | தமி)",
            "Three-way segmented toggle pill in the top header:\n• EN (English)\n• සිං (Sinhala)\n• தமி (Tamil)",
            "• Origin: Hand-rolled zero-dependency i18n Context ('LanguageContext.tsx') with translation dictionaries in 'translations.ts'.\n• Persisted to localStorage ('taxease_language').",
            "Instantly re-renders all UI titles, headers, navigation labels, and subtitles across the entire app into the selected national language without losing page state."
        ),
        (
            "Global Search Input",
            "Search box with magnifying glass icon in header.\nPlaceholder: 'Search anything...'",
            "• Client-side filter on active view / global query hook.",
            "Filters records on table-heavy pages (Documents, Companies, RFIs, Audit Log) in real time as the user types."
        ),
        (
            "Profile Menu Dropdown",
            "Avatar pill with user initials (e.g., 'AO'), display name, user email, and role chip ('Admin' / 'Auditor').",
            "• Origin: 'taxease_user' session storage / Supabase auth session.",
            "Clicking reveals dropdown containing:\n1. Profile details & Role chip\n2. Link to Settings (/settings or /auditor-settings)\n3. 'Log Out' button (clears tokens and redirects to /sign-in)."
        ),
        (
            "Navigation Sidebar",
            "Brand logo (TaxEaseLK with Sri Lankan flag emblem) + structured navigation links with Lucide icons.",
            "• Business Links: Dashboard, Documents, Financials, Auditor Review, Discussions, Settings.\n• Auditor Links: Dashboard, Companies, Review Queue, Requests, Responses, Documents, Discussions, Audit Log, Settings.",
            "Highlights active route with blue accent bar and light-blue background fill. Clicking smoothly routes between pages using Next.js App Router."
        ),
        (
            "Application Splash Screen",
            "Full-screen branded loading splash matching Figma design tokens, displaying TaxEaseLK logo and progress indicator.",
            "• Origin: 'AppSplash.tsx' mounted in root layout.\n• Tracks browser session load.",
            "Displays for ~1 second only on cold browser open or hard refresh, then smoothly fades out. Does NOT flash during internal page navigations."
        )
    ]

    for item in chrome_rows:
        row_cells = tbl_chrome.add_row().cells
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

    # ------------------ SECTION 3: AUTH & ONBOARDING ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("3. Authentication & Onboarding Module Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The authentication subsystem guarantees strict separation of duties between corporate tax filers and statutory auditors from the very first onboarding touchpoint."
    )

    tbl_auth = doc.add_table(rows=1, cols=4)
    tbl_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_auth, "CBD5E1")
    auth_cols = ["Screen / Route", "Key Fields & Elements", "Business Logic & Validations", "Flow & Redirection"]
    for i, title in enumerate(auth_cols):
        cell = tbl_auth.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    auth_rows = [
        (
            "Choose Role Page\n('/role')",
            "Two distinct role selection cards:\n1. 'Business Owner' (Building icon) - 'File your Pvt Ltd company income tax file'\n2. 'Auditor' (ShieldCheck icon) - 'Review and approve your client companies Income tax files'",
            "• Informs user of access rights and UI features.\n• Decouples registration flow based on statutory responsibilities.",
            "• Clicking Business Owner routes to '/sign-up/business'.\n• Clicking Auditor routes to '/sign-up/auditor'.\n• 'Back' link returns to '/sign-in'."
        ),
        (
            "Sign In Page\n('/sign-in')",
            "• Email Input\n• Password Input (toggle show/hide)\n• 'Remember Me' Checkbox\n• 'Forgot Password?' link\n• 'Sign In' Button\n• Quick Demo Credentials Fill Pills (Admin Demo / Auditor Demo)",
            "• Authenticates against Supabase Auth / FastAPI auth endpoint.\n• Determines user role from account metadata ('business' or 'auditor').\n• Stores JWT access token and user session.",
            "• If role is 'business' -> Redirects to '/dashboard'.\n• If role is 'auditor' -> Redirects to '/auditor-dashboard'.\n• If credentials invalid -> Displays inline error alert."
        ),
        (
            "Sign Up - Business\n('/sign-up/business')",
            "• Company Name (Pvt Ltd legal entity)\n• Full Name (Finance Director / Owner)\n• Work Email\n• Password & Confirm Password\n• Agreement checkbox to Terms & IRD Compliance Declaration\n• 'Create Business Account' button",
            "• Validates legal company format.\n• Enforces secure password requirements.\n• Initializes default company profile in database with standard 30% CIT rate and FY 2025/26.",
            "• Upon successful submission, registers user, sets role='business', stores initial company settings in localStorage and backend, and routes directly to '/dashboard'."
        ),
        (
            "Sign Up - Auditor\n('/sign-up/auditor')",
            "• Audit Firm / Organization Name\n• Lead Auditor Full Name\n• CA Sri Lanka / ICASL Member Number\n• Work Email\n• Password & Confirm Password\n• Declaration of Professional Standing checkbox\n• 'Create Auditor Account' button",
            "• Validates professional credential format (ICASL/CA Sri Lanka registration).\n• Establishes auditor profile capable of managing multi-client engagements.",
            "• Upon successful submission, registers user, sets role='auditor', initializes empty review queue and client list, and routes directly to '/auditor-dashboard'."
        ),
        (
            "Forgot Password\n('/forgot-password')",
            "• Email Input field\n• 'Send Reset Link' button\n• 'Back to Sign In' link",
            "• Validates registered email address.\n• Dispatches password recovery link via Supabase Auth email service.",
            "• Displays confirmation message upon dispatch.\n• Allows user to return to login screen."
        )
    ]

    for item in auth_rows:
        row_cells = tbl_auth.add_row().cells
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

    # ------------------ SECTION 4: BUSINESS PORTAL ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("4. Business Portal: In-Depth Component Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    # 4.1 Dashboard
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.1 Business Dashboard Page ('/dashboard')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Dashboard is the central command center for the business taxpayer. It synthesizes statutory tax readiness, audit handover progress, and critical action items into real-time visual indicators."
    )

    add_callout([
        "Matches user specification from platform review:",
        "1. Top nav bar: Company name ('ABC PVT LTD') & financial year ('FY 2025/26') update dynamically from Settings.",
        "2. Top nav bar: Notification grabs auditor requests, discussion messages, and status updates.",
        "3. Audit Handover & Verification Pipeline: Progress bar fills dynamically as Stage 1 to Stage 5 tiles fill.",
        "4. Document tile: Upload documents count correctly as (uploaded / checklist count).",
        "5. Accounting Profit tile: Calculates Accounting Profit = (Revenue - Expenses).",
        "6. Auditor status tile: Shows Auditor status updated by assigned auditor [Waiting / Under Review / Approved].",
        "7. Requires your attention tile: Shows assigned Auditor Queries & Exceptions Notices."
    ], title="CORE DASHBOARD SPECIFICATION HIGHLIGHTS", color_hex=BLUE_HEX, bg_hex="EFF6FF")

    tbl_dash = doc.add_table(rows=1, cols=4)
    tbl_dash.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_dash, "CBD5E1")
    dash_cols = ["Dashboard Tile / Element", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Dynamic Behavior & Target Action"]
    for i, title in enumerate(dash_cols):
        cell = tbl_dash.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    dash_rows = [
        (
            "Dashboard Subtitle\n(Company & FY sync)",
            "Subtitle text:\n'Real-time statutory tax compliance dashboard for [Company Name] • Assessment Year [FY]'",
            "• Origin: 'DashboardSubtitle.tsx' listening to 'taxease_company_updated' event and reading 'taxease_company_settings'.\n• If user changes company name or FY in settings, this subtitle updates immediately.",
            "Provides instant confirmation of active entity context directly under the main H1 page header."
        ),
        (
            "Audit Handover & Verification Pipeline\n(Main Progress Bar)",
            "• Main progress bar displaying composite % (e.g. 65% Complete).\n• Status Chip:\n- <60%: 'Awaiting Documents' (amber)\n- 60-99%: 'Handover In Progress' (blue)\n- 100%: 'Audit Pack Signed Off' (emerald)",
            "• Origin: Composite weighted sum of 5 pipeline stages:\nOverall % = (Stage 1 % * 0.20) + (Stage 2 % * 0.20) + (Stage 3 % * 0.20) + (Stage 4 % * 0.20) + (Stage 5 % * 0.20).\n• Also listens to 'taxease_audit_status_updated'. If auditor signs off ('Approved'), jumps to 100%.",
            "Updates whenever documents are uploaded, AI finishes extraction, or the auditor marks review milestones."
        ),
        (
            "Pipeline Stage 1:\nDocument Gathering",
            "• Title: 'Stage 1: Document Gathering'\n• Ratio: e.g., '4 / 5 Gathered'\n• Stage bar & status chip (Clock / Alert / Done)",
            "• Formula: (Uploaded Checklist Documents / 5 Required Documents) * 100%.\n• Source: Evaluates presence of 5 core categories in Document inventory.",
            "Clicking card routes directly to '/documents' so user can upload remaining statutory files."
        ),
        (
            "Pipeline Stage 2:\nFinancial Data",
            "• Title: 'Stage 2: Financial Data'\n• Ratio: e.g., '5 / 5 Schedules Ready'\n• Sublabel: 'Income Statement & BS Synced'",
            "• Formula: Based on extraction and population of the 5 financial schedules (P&L, Balance Sheet, Trial Balance, Ledger, Fixed Assets).",
            "Clicking card routes to '/financials' to inspect line-item ledger extractions."
        ),
        (
            "Pipeline Stage 3:\nAI Extraction",
            "• Title: 'Stage 3: AI Extraction'\n• Ratio: e.g., '96% Avg Confidence'\n• Sublabel: 'Zero extraction syntax errors'",
            "• Formula: Mean average of AI confidence scores across all processed document rows: sum(aiConfidencePercent) / count.",
            "Clicking card routes to '/documents' to review any files flagged for human confirmation."
        ),
        (
            "Pipeline Stage 4:\nAuditor Handover",
            "• Title: 'Stage 4: Auditor Handover'\n• Ratio: e.g., 'Pack Dispatched'\n• Sublabel: 'Locked for statutory audit'",
            "• Formula: Set to 100% once business clicks 'Submit Handover Pack to Auditor', or proportionate based on pack readiness.",
            "Clicking card routes to '/auditor-review' to verify handover package status."
        ),
        (
            "Pipeline Stage 5:\nAuditor Inquiries & Sign-Off",
            "• Title: 'Stage 5: Auditor Inquiries'\n• Ratio: e.g., '1 Pending Inquiry' or 'Audit Signed Off'\n• Sublabel: 'BDO Partners / CA Sri Lanka'",
            "• Formula: 100% when auditor sets status to 'Approved' and all inquiries are resolved. Pro-rated as (Resolved Inquiries / Total Inquiries).",
            "Clicking card routes to '/auditor-review' to answer pending auditor requests."
        ),
        (
            "Document Stat Tile\n(Uploaded / Checklist)",
            "• Value: e.g., '4 / 5'\n• Hint: '1 statutory document pending upload' (amber) or 'All statutory docs gathered' (emerald)",
            "• Formula: Value = (data.documentsUploaded) / (data.documentsTotal).\n• Recalculates dynamically whenever a document is added or removed from the Documents page.",
            "Provides an instant high-level checklist check so business knows if statutory pack is complete."
        ),
        (
            "Accounting Profit Tile\n(Revenue - Expenses)",
            "• Value: e.g., 'Rs. 4,600,000'\n• Hint: 'From audited / draft financial statements'",
            "• Formula: Accounting Profit = Gross Revenue (Turnover) - Total Operating Expenses & Cost of Sales.\n• Sourced directly from Financial Statements (Profit & Loss / Income Statement).",
            "Establishes the commercial starting base before tax adjustments under Sri Lankan tax law."
        ),
        (
            "Auditor Status Tile\n(Waiting / Review / Approved)",
            "• Value: 'Waiting for Submission' | 'Under Review' | 'Approved'\n• Dynamic hint explaining current audit state",
            "• Source: Updated by the assigned auditor in the Auditor Portal or stored in 'taxease_last_audit_status'.\n• Displays 'Approved' when statutory auditor certifies the tax file.",
            "Visual milestone showing whether auditor is currently inspecting, awaiting company responses, or has certified."
        ),
        (
            "Quick Actions Card",
            "Three high-efficiency action buttons:\n1. 'Upload Documents' (with Upload icon)\n2. 'AI Guidance' (with Sparkles icon & blue pill)\n3. 'View Financials' (with FileBarChart icon)",
            "• Upload Documents -> routes to '/documents'.\n• View Financials -> routes to '/financials'.\n• AI Guidance -> Roadmap feature tooltipped for tax optimization tips.",
            "Allows finance managers to jump directly to data entry or reports with a single click."
        ),
        (
            "Requires Your Attention Card\n(Auditor Inquiries & Notices)",
            "Card displaying list of active auditor queries, discrepancy notices, and documentation requests.\n• Critical severity: Red border & background.\n• Warning severity: Amber border & background.\n• If empty: Emerald 'All Caught Up' badge.",
            "• Source: Directly mirrors open inquiries created by the auditor in Auditor Portal ('/api/auditor-review/issues').\n• Displays Issue Title, description, and direct 'Review' link.",
            "Clicking 'Review' deep-links to '/auditor-review?issue=[issueId]' so business can immediately submit explanations or upload requested supporting invoices."
        )
    ]

    for item in dash_rows:
        row_cells = tbl_dash.add_row().cells
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

    # 4.2 Documents Page
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.2 Business Documents Page ('/documents')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Documents page handles client-side file intake, validation, AI OCR extraction simulation, and statutory document checklist compliance."
    )

    tbl_docs = doc.add_table(rows=1, cols=4)
    tbl_docs.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_docs, "CBD5E1")
    docs_cols = ["Component / Tile", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(docs_cols):
        cell = tbl_docs.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    docs_rows = [
        (
            "Category Selection Dropdown",
            "Dropdown above the upload zone with pre-configured statutory categories:\n• Auto-Detect from File Name\n• Financial Statements (Audited / Draft)\n• Trial Balance (12-month final)\n• General Ledger Extracts\n• Fixed Asset Schedule\n• CIT Return / Prior Assessments",
            "• Controlled client state ('selectedCategory').\n• Overrides auto-detection heuristic when user explicitly picks a statutory category.",
            "Ensures uploaded files are immediately tagged with the exact statutory classification required by the auditor."
        ),
        (
            "Stat Card 1: Total Uploaded",
            "Number of documents currently loaded in the company's document repository.",
            "• Formula: documents.length.\n• Recomputes live as files are added or deleted.",
            "Gives instant inventory count of compliance attachments."
        ),
        (
            "Stat Card 2: Processed by AI",
            "Count of files that successfully passed AI OCR extraction without syntax issues.",
            "• Formula: documents.filter(d => d.status === 'processed').length.\n• Represents clean, parseable data.",
            "Signals that financial figures have been cleanly ingested into the tax engine."
        ),
        (
            "Stat Card 3: Review Required",
            "Count of files where AI extraction confidence fell below threshold or manual check is needed.",
            "• Formula: documents.filter(d => d.status === 'review_required').length.",
            "Alerts user that scanned handwriting, low-res scans, or unformatted schedules need manual verification."
        ),
        (
            "Stat Card 4: Missing Checklist Count",
            "Count of mandatory statutory checklist documents still missing (e.g., '1 Document Missing' or 'All Gathered').",
            "• Formula: Math.max(0, 5 - fulfilledCount), where required categories are Financial Statements, Trial Balance, Ledger, Fixed Assets, and CIT Return.\n• Re-evaluates every time documents list changes.",
            "Shows amber alert badge if <5, turns emerald checkmark when all 5 statutory items are satisfied."
        ),
        (
            "Document Upload Zone\n(Drag & Drop)",
            "Dashed drop box with cloud upload icon, file format labels (PDF, XLSX, CSV, PNG, JPG up to 10MB), and 'Browse Files' button.",
            "• Validation ('lib/files.ts'): Rejects unsupported file extensions or files exceeding 10MB with inline error banner.\n• Supports multi-file drag-and-drop.",
            "• Accepted files appear in table immediately in 'processing' status with animated spinner.\n• Sends file via FormData to backend API or simulates AI OCR completion with confidence %."
        ),
        (
            "Auditor Document Checklist\n(Created by Assigned Auditor)",
            "A dynamic, company-specific statutory checklist card itemizing the documents requested by the appointed auditor:\n• Preset Statutory Packs (Standard CIT, BOI & Exporter Pack, Manufacturing & Trading)\n• Custom document requirements added by the auditor\n• Header displays: 'Requested by [Auditor Name] • [Firm Name]'\n• Dynamic fulfillment indicator (Provided vs. Missing count & Audit Pack Readiness %)",
            "• Origin: Created and published by the assigned auditor via AuditorChecklistModal ('/api/auditor/checklists' & 'taxease_checklist_[companyName]').\n• Auto-syncs via 'taxease_checklist_updated' window event whenever the assigned auditor modifies the company's checklist requirements.",
            "• Evaluates uploaded documents against the auditor's required items.\n• Clicking any missing item automatically selects that category in the upload dropdown and focuses the upload zone."
        ),
        (
            "Document Inventory Table",
            "Table listing all company documents with columns:\n• Document Name & Icon\n• Document Category\n• Live Status Badge ('Processed', 'Review Required', 'Processing')\n• AI Confidence Bar (colored mini progress bar with %)\n• Upload Date & File Size\n• Remove Action (Trash icon)",
            "• AI Confidence Bar: Green if >=95%, amber if 85-94%, red if <85%.\n• Status Badge: 'Processed' (green check), 'Review Required' (amber alert), 'Processing' (blue pulse).",
            "• Clicking trash icon deletes document from local state & backend, triggers 'taxease_documents_updated' event, and updates stat tiles instantly."
        )
    ]

    for item in docs_rows:
        row_cells = tbl_docs.add_row().cells
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

    # 4.3 Financials Page
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.3 Business Financials & Tax Computation Page ('/financials')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Financials page bridges commercial accounting and statutory corporate taxation under the Inland Revenue Act No. 24 of 2017. "
        "It features commercial trading metrics, statutory CIT waterfall reconciliation, interactive schedule tables, and an AI Audit Summary generator."
    )

    tbl_fin = doc.add_table(rows=1, cols=4)
    tbl_fin.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_fin, "CBD5E1")
    fin_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(fin_cols):
        cell = tbl_fin.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    fin_rows = [
        (
            "Commercial Metric 1:\nGross Turnover",
            "• Value: e.g., 'Rs. 25,000,000'\n• Sublabel: 'Commercial Inflows'",
            "• Total top-line gross revenue recognized during the assessment year.\n• Extracted from audited / draft Income Statement.",
            "Primary benchmark for company size, VAT/SVAT thresholds, and turnover tax assessments."
        ),
        (
            "Commercial Metric 2:\nCost of Sales (COS)",
            "• Value: e.g., 'Rs. 15,200,000'\n• Sublabel: 'Direct Production Costs'",
            "• Direct material, labor, and import landing costs directly tied to revenue.\n• Extracted from trading account / manufacturing schedules.",
            "Subtracted from Gross Turnover to calculate Gross Profit."
        ),
        (
            "Commercial Metric 3:\nGross Profit & Trading Margin",
            "• Value: e.g., 'Rs. 9,800,000'\n• Badge: e.g., '39.2%'\n• Sublabel: 'Trading Margin'",
            "• Formula: Gross Profit = Gross Turnover - Cost of Sales.\n• Gross Margin % = (Gross Profit / Gross Turnover) * 100%.",
            "Evaluates operational profitability prior to overheads and administrative operating expenditures."
        ),
        (
            "Commercial Metric 4:\nOperating OPEX",
            "• Value: e.g., 'Rs. 5,200,000'\n• Sublabel: 'Admin & Sales Overheads'",
            "• Total administrative, selling, marketing, utility, and general overhead expenses.\n• Extracted from general ledger expense breakdown.",
            "Analyzed during tax audit for disallowable items (entertainment, fines, depreciation)."
        ),
        (
            "Commercial Metric 5:\nAccounting Profit PBT",
            "• Value: e.g., 'Rs. 4,600,000'\n• Badge: '18.4% Net'\n• Sublabel: 'Draft for Auditor Review'",
            "• Formula: Accounting Profit = Gross Profit - Operating OPEX (Revenue - Total Expenses).\n• Forms the foundational figure for corporate tax computation.",
            "Serves as Step 1 of the statutory tax reconciliation waterfall."
        ),
        (
            "Statutory CIT Computation Banner\n(Waterfall Step 1 to 5)",
            "Prominent waterfall banner computing indicative CIT liability:\n1. Accounting PBT ('Rs. 4,600,000')\n2. (+) Disallowables Section 11 ('+Rs. 2,100,000')\n3. (-) Capital Allowances 4th Sched ('-Rs. 1,500,000')\n4. Taxable Income ('Rs. 5,200,000')\n5. Indicative CIT Liability at 30% ('Rs. 1,560,000')",
            "• Formula:\nTaxable Income = Accounting PBT + Section 11 Disallowables - 4th Schedule Allowances.\nCIT Liability = Taxable Income * CIT Rate (30% standard or 14% concessionary).\n• Reflects IRD Gazette 2311/38 statutory tax rate rules.",
            "• Includes 'Breakdown' toggle expanding detailed Section 11 add-back items (accounting depreciation, entertainment) and Fourth Schedule capital depreciation.\n• Displays Auditor Status chip ('Under Review by Auditor' or 'Approved')."
        ),
        (
            "Interactive Schedules Table\n(5 Sub-Tabs)",
            "Tabbed financial viewer with tabs:\n1. Income Statement\n2. Balance Sheet\n3. Trial Balance\n4. General Ledger\n5. Fixed Assets",
            "• Displays structured line items with Item Name, Amount (LKR), Source Document, Tax Category, and AI Extraction Confidence bar.\n• Highlights subtotals and totals in bold with gray backgrounds.",
            "Allows finance director and auditor to inspect specific line items, verify tax treatments, and cross-reference supporting ledger accounts."
        ),
        (
            "AI Financial Report Modal\n('AI Audit Summary')",
            "Comprehensive modal opened by clicking 'AI Audit Summary':\n• Executive Summary paragraph\n• Profitability Analysis grid\n• Detailed Statutory Tax Reconciliation breakdown\n• Corporate Compliance Score (e.g., 94%)\n• Key Tax Risks identified by AI\n• Actionable Recommendations\n• 'Print / Export PDF' action",
            "• Generated by AI analysis of uploaded financial statements and ledger books.\n• Identifies potential audit exposure, missing vouchers, and tax saving opportunities under Inland Revenue Act.",
            "Enables finance executives to review audit risks and print a formal briefing report before meeting with the auditor."
        ),
        (
            "Export Handover Pack Button",
            "Header action button: 'Export Handover Pack' with Download icon.",
            "• Packages financial schedules, tax computation waterfall, and document index.",
            "Triggers clean printable/exportable tax audit file ready for statutory submission or offline archive."
        )
    ]

    for item in fin_rows:
        row_cells = tbl_fin.add_row().cells
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

    # 4.4 Auditor Review Page
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.4 Business Auditor Review & Sign-Off Page ('/auditor-review')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Auditor Review page governs professional collaboration between the business and its statutory auditor, tracking engagement status, sign-off progress, and audit queries."
    )

    tbl_rev = doc.add_table(rows=1, cols=4)
    tbl_rev.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_rev, "CBD5E1")
    rev_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(rev_cols):
        cell = tbl_rev.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    rev_rows = [
        (
            "Invite Auditor Button & Modal",
            "Top-right button 'Invite Auditor' opening invitation modal:\n• Auditor / Firm Name\n• Auditor Email Address\n• Tax Year (e.g., '2025/26')\n• Custom Appointment Message",
            "• Origin: Direct dispatch to '/api/auditor/invitations'.\n• Automatically creates a pending engagement invitation in the Auditor Portal.",
            "Sends invitation to auditor; when auditor accepts, links company to auditor's active client list and updates Assigned Auditor Card."
        ),
        (
            "Assigned Auditor Profile Card",
            "Card displaying appointed statutory auditor:\n• Auditor Name (e.g., 'K.L. Perera, FCA')\n• Audit Firm (e.g., 'BDO Partners / Ernst & Young')\n• Professional Badges: 'ICASL Certified', 'CA Sri Lanka Fellow'\n• Contact Email & Phone\n• Review Status Badge ('Active', 'Waiting for Review', 'Approved')\n• Submission Date & Expected Sign-Off Date\n• Auditor Review Progress Bar (e.g., 65%)\n• Actions: 'Rate Auditor', 'Message Auditor', 'Cancel Engagement'",
            "• Sourced from backend '/api/auditor-review' (or local engagement state 'taxease_assigned_auditor_[company]').\n• Progress Bar reflects percentage of verified items in auditor's checklist.",
            "• 'Message Auditor' routes to '/discussions'.\n• 'Rate Auditor' opens 5-star rating modal.\n• 'Cancel Engagement' opens confirmation dialog to revoke auditor access if needed."
        ),
        (
            "CIT Status Summary Counts Card",
            "Summary breakdown card showing 4 rows:\n• Approved Items count (emerald)\n• Warning Items count (amber)\n• Critical Items count (red)\n• Pending Items count (gray)",
            "• Aggregated count of auditor inquiry items and checklist verifications.\n• Recomputes live as auditor marks items or company resolves queries.",
            "Provides at-a-glance status of outstanding blockers preventing final CIT sign-off."
        ),
        (
            "Auditor Inquiries & Exceptions Manager",
            "Interactive list of issues/queries raised by auditor during inspection:\n• Issue Title & Source (e.g., 'Fixed Assets Additions - Inadequate Documentation')\n• Severity Badge: 'Critical Action Required' (red) vs 'Pending Clarification' (amber)\n• Auditor Comment text\n• Company Response Textarea (reply input)\n• File Attachment Upload (drag & drop receipts/invoices)\n• 'Submit Explanation & Resolve' button",
            "• Sourced from '/api/auditor-review/issues'.\n• Matches items highlighted on the Dashboard 'Requires your attention' card.",
            "• Business types explanation and attaches invoices/agreements.\n• Submitting marks item as resolved, notifies auditor in Auditor Portal ('/responses'), and clears dashboard attention warning."
        ),
        (
            "Rate Auditor Modal",
            "Modal dialog with 5 interactive gold stars, review feedback textarea, and 'Submit Professional Review' button.",
            "• Submits feedback to auditor profile rating database.",
            "Saves rating, stores review record, and displays updated star score on the auditor's public profile and audit rank badge."
        )
    ]

    for item in rev_rows:
        row_cells = tbl_rev.add_row().cells
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

    # 4.5 Discussions Page
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.5 Business Discussions Page ('/discussions')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Discussions page provides an authenticated, real-time messaging channel between the business finance team and the assigned statutory auditor, organized by tax topic."
    )

    tbl_disc = doc.add_table(rows=1, cols=4)
    tbl_disc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_disc, "CBD5E1")
    disc_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(disc_cols):
        cell = tbl_disc.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    disc_rows = [
        (
            "Active Auditor Header Banner",
            "Header card displaying assigned auditor's name, audit firm, credential badge, and direct communication status.",
            "• Sourced from active engagement profile for current company.",
            "Assures business that messages are transmitted directly to certified practitioner."
        ),
        (
            "Topic Threads List & Filter",
            "Left-side pane listing conversation threads:\n• Topic Title (e.g., 'Entertainment Expense Add-Backs')\n• Category Tag (Tax Computation, Depreciation, General)\n• Last message snippet & timestamp\n• Unread badge\n• Status Filter: 'All', 'Open', 'Closed'\n• 'New Discussion' (+) button",
            "• Sourced from '/api/business/discussions'.\n• Automatically groups queries by subject matter.",
            "Clicking any thread loads full message history in the right-hand conversation stream."
        ),
        (
            "Start New Discussion Modal",
            "Modal dialog:\n• Topic Title\n• Category Dropdown\n• Initial Message Textarea\n• 'Start Discussion' button",
            "• Submits POST to '/api/business/discussions'.",
            "Creates new conversation thread, notifies auditor in Auditor Portal ('/auditor-discussions'), and triggers top bar notification."
        ),
        (
            "Message Stream & Composer",
            "Right-side message stream:\n• Auditor messages: Gray bubble with Auditor badge on left.\n• Business messages: Blue bubble with Company badge on right.\n• Timestamp on every message.\n• Bottom Reply Box: Textarea + 'Send Message' button.",
            "• Real-time or polling sync.\n• Auto-scrolls to latest message upon arrival.",
            "Typing reply and hitting Send appends message immediately to the thread and updates last message preview in left panel."
        )
    ]

    for item in disc_rows:
        row_cells = tbl_disc.add_row().cells
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

    # 4.6 Settings Page
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.6 Business Settings Page ('/settings') & Dynamic Sync Engine")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Settings page is the single source of truth for company identity, tax registration parameters, and finance team roles. "
        "Every change made here immediately propagates across the entire platform via the dynamic sync engine."
    )

    tbl_sett = doc.add_table(rows=1, cols=4)
    tbl_sett.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_sett, "CBD5E1")
    sett_cols = ["Settings Field / Element", "Displayed Content & Logic", "Data Origin & Storage", "Cascading Impact on Frontend"]
    for i, title in enumerate(sett_cols):
        cell = tbl_sett.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    sett_rows = [
        (
            "Company Legal Name\n('companyName')",
            "Input field for registered corporate entity name (e.g., 'ABC (Pvt) Ltd').",
            "• Stored in localStorage ('taxease_company_settings') and Supabase 'companies' table.",
            "CRITICAL SYNC:\nSaving updates:\n1. Top Nav Bar company badge\n2. Dashboard subtitle\n3. Financials report title\n4. Document uploads company metadata\n5. Auditor client directory name."
        ),
        (
            "Financial Assessment Year\n('financialYear')",
            "Input field for tax year (e.g., '2025/26' or 'FY 2025/26').",
            "• Stored in localStorage ('taxease_company_settings') and Supabase tax profiles.",
            "CRITICAL SYNC:\nSaving updates:\n1. Top Nav Bar 'FY 2025/26' pill\n2. Dashboard assessment year badge\n3. Financials AY badge\n4. Auditor compliance tax year index."
        ),
        (
            "Company Registration Number\n('registrationNumber')",
            "Input field for Registrar of Companies (ROC) PV number (e.g., 'PV 00294812').",
            "• Company profile metadata.",
            "Appears on formal tax packs, export documents, and auditor appointment agreements."
        ),
        (
            "Taxpayer Identification Number\n('tinNumber')",
            "Input field for Inland Revenue Department (IRD) TIN (e.g., '192847291-0000').",
            "• Mandatory IRD identifier.",
            "Cross-referenced on all tax schedules and displayed in the Auditor Companies directory."
        ),
        (
            "VAT & SVAT Registration\n('vatNumber' / 'svatNumber')",
            "• VAT Number input\n• 'Registered for Simplified VAT (SVAT)' toggle\n• SVAT Number input (conditionally enabled)",
            "• Sri Lankan indirect tax compliance profile.",
            "Determines whether VAT/SVAT reconciliation schedules are mandated during audit review."
        ),
        (
            "CIT Tax Rate Category\n('citTaxRateCategory')",
            "Dropdown with statutory Sri Lankan categories:\n• Standard Corporate Rate (30%)\n• SME / Manufacturing / Export Concessionary (14%)\n• Specialized Concessionary Rate (15%)\n• Other Specific Rate",
            "• Determines CIT multiplier in the Tax Computation waterfall banner on '/financials'.",
            "Changing from 30% to 14% immediately recalculates Indicative CIT Liability on Financials page and AI Report."
        ),
        (
            "Contact Email & Phone",
            "Input fields for official corporate finance contact email and phone number.",
            "• Company contact card data.",
            "Used by the auditor to reach finance executives and listed on audit queries."
        ),
        (
            "Registered Business Address & Sector",
            "• Address textarea (e.g., 'No. 45, Galle Road, Colombo 03')\n• Industry Sector dropdown (Information Technology, Manufacturing, Services, Retail).",
            "• Demographic and industrial classification.",
            "Allows AI to apply sector-specific depreciation rates and tax incentives."
        ),
        (
            "Live Save Engine\n('Save Changes' button)",
            "Primary button: 'Save Changes' with loading spinner and green checkmark feedback.",
            "• Writes to localStorage ('taxease_company_settings')\n• Dispatches 'taxease_company_updated' window event\n• POSTs to '/api/company/settings'.",
            "Triggers instantaneous cross-component re-render across TopBar, Dashboard, and Documents without page refresh."
        ),
        (
            "Team & Users Tab\n('UsersTab.tsx')",
            "Team management table listing finance users:\n• User Name & Initials\n• Email Address\n• Role Badge: 'Owner', 'Finance Director', 'Senior Accountant', 'Tax Officer', 'Viewer'\n• Status: 'Active', 'Invited'\n• 'Can Sign Tax Returns' permission toggle\n• 'Invite Team Member' button & modal",
            "• Sourced from company user directory.",
            "Enforces role-based permissions inside the company, controlling who can upload docs vs who can execute final tax sign-offs."
        )
    ]

    for item in sett_rows:
        row_cells = tbl_sett.add_row().cells
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

    # ------------------ SECTION 5: AUDITOR PORTAL ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("5. Auditor Portal: In-Depth Component Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    # 5.1 Auditor Dashboard
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.1 Auditor Dashboard ('/auditor-dashboard')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Auditor Dashboard provides statutory auditors with high-level visibility across their client portfolio, workload queue, and urgent priority reviews."
    )

    tbl_adash = doc.add_table(rows=1, cols=4)
    tbl_adash.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_adash, "CBD5E1")
    adash_cols = ["Auditor Dashboard Tile", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(adash_cols):
        cell = tbl_adash.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    adash_rows = [
        (
            "Stat Tile 1: Active Clients",
            "• Value: e.g., '14'\n• Sublabel: 'Active companies under your review'\n• Button: 'View Companies'",
            "• Total count of corporate taxpayer clients assigned to this auditor firm in database.",
            "Clicking 'View Companies' routes to '/companies' management directory."
        ),
        (
            "Stat Tile 2: Pending Reviews / Under Review",
            "• Value: e.g., '6'\n• Sublabel: 'CIT computations currently under review'\n• Button: 'Review Queue'",
            "• Count of companies currently in 'Under Review' or 'Ready for Auditor' status.",
            "Clicking 'Review Queue' routes to '/responses' / Review Queue."
        ),
        (
            "Stat Tile 3: Completed This Period",
            "• Value: e.g., '8'\n• Sublabel: 'Reviews completed this period'\n• Button: 'View All'",
            "• Count of corporate tax returns certified and signed off ('Approved') by this auditor during active tax cycle.",
            "Serves as audit milestone tracker and billing completion indicator."
        ),
        (
            "Priority Reviews Card",
            "List of corporate files requiring urgent auditor intervention:\n• Company Name\n• Severity Tag: 'Critical' (red), 'Attention' (amber), 'Ready' (green)\n• Detail note (e.g., '2 unverified fixed asset additions')\n• Pack Progress Bar with %\n• Due Date (e.g., 'Due in 3 days')\n• 'Review' button",
            "• Sourced from '/api/auditor/priority-reviews'.\n• Sorted by filing deadline proximity and issue severity.",
            "Clicking 'Review' deep-links directly into that company's audit pack and response items."
        ),
        (
            "Auditor Workload Breakdown Card",
            "Structured workload queue breakdown:\n• Pending (gray count)\n• Under Review (blue count)\n• Waiting for Company (amber count)\n• Ready for Auditor Approval (purple count)\n• Completed (emerald count)\n• 'Open Review Queue' button",
            "• Live count of corporate files across each stage of the audit lifecycle.",
            "Clicking 'Open Review Queue' routes to the filterable review queue."
        ),
        (
            "Recent Audit Activity Stream",
            "Audit stream card showing recent portfolio events:\n• Event title (e.g., 'Document Uploaded', 'RFI Responded', 'Audit Certified')\n• Client company name\n• Timestamp (e.g., '12m ago', '2h ago')",
            "• Real-time log of client actions across all assigned entities.",
            "Allows lead partner to monitor team activities and incoming client submissions."
        )
    ]

    for item in adash_rows:
        row_cells = tbl_adash.add_row().cells
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

    # 5.2 Companies Management Page
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.2 Auditor Companies Management Page ('/companies')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Companies page acts as the auditor's master client engagement registry, managing client invitations, filing statuses, issue counts, and statutory audit checklists."
    )

    tbl_comp = doc.add_table(rows=1, cols=4)
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_comp, "CBD5E1")
    comp_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(comp_cols):
        cell = tbl_comp.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    comp_rows = [
        (
            "Client Invitations Modal & Badge",
            "Top banner / button showing pending engagement invites from business owners (e.g., '2 New Client Invitations').\n• Modal displays:\n- Company Name & Reg No\n- Sender Representative Name & Email\n- Tax Year\n- Estimated Turnover\n- 'Accept Appointment' & 'Decline' actions",
            "• Sourced from '/api/auditor/invitations'.\n• Populated when businesses click 'Invite Auditor' on '/auditor-review'.",
            "• 'Accept Appointment' formally establishes auditor engagement, moves company into active client list, and notifies business.\n• 'Decline' archives the request."
        ),
        (
            "Companies Directory Table",
            "Master table with columns:\n• Company Name (with legal icon)\n• TIN Number & Copy button\n• Financial Year\n• CIT Filing Status Badge ('Draft', 'Under Review', 'Ready for Auditor', 'Approved', 'Waiting for Company')\n• Issue Count Pair (Critical in red pill / Warning in amber pill)\n• Pack Progress Bar (% with color coding)\n• Filing Due Date (with countdown chip)\n• Actions: 'View Profile' & 'Open Checklist'",
            "• Sourced from '/api/auditor/companies'.\n• CitStatusBadge applies color tokens matching platform status hierarchy.\n• IssueCountPair summarizes open audit findings.",
            "• 'View Profile' opens complete corporate drawer with contact details, address, turnover, and assigned tax office.\n• 'Open Checklist' launches AuditorChecklistModal."
        ),
        (
            "Auditor Document Checklist Manager\n('AuditorChecklistModal.tsx')",
            "Interactive modal allowing the assigned auditor to create, configure, and publish a company-specific document checklist:\n• Preset Packs:\n  1. Standard Statutory CIT Pack (Financial Statements, Trial Balance, Ledger, Assets, Prior CIT)\n  2. BOI & Exporter Pack (Adds BOI Agreements, Export Realization Certificates, Customs CUSDEC)\n  3. Manufacturing & Trading Pack (Adds Physical Stock Valuation, WHT/AIT Sched 10 Certificates)\n• Custom Document Creator: Auditor can add custom required/optional items with specific audit instructions/notes.\n• Save & Publish: Publishes checklist directly to the company's Documents page via '/api/auditor/checklists' and 'taxease_checklist_[companyName]'.",
            "• Sourced from 'taxease_checklist_[companyName]' and backend checklist repository.\n• Automatically synchronizes with the business user's 'AuditorDocumentChecklist.tsx' component via custom window events.",
            "• When the auditor clicks 'Save & Publish', the company's Documents page and Dashboard instantly update to require these specific documents.\n• Company checklist readiness is calculated against this auditor-created list."
        ),
        (
            "Add Company / New Client Modal",
            "Header action button 'Add Company' opening registration modal:\n• Company Name\n• TIN Number\n• Financial Year\n• Contact Person & Email\n• 'Add to Portfolio' button",
            "• Adds company directly into auditor's client registry.",
            "Instantly appends company to table, allowing immediate document requests and audit onboarding."
        )
    ]

    for item in comp_rows:
        row_cells = tbl_comp.add_row().cells
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

    # 5.3 Review Queue / Client Responses
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.3 Auditor Review Queue & Client Responses Page ('/responses')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Responses page is the auditor's inbox for inspecting evidence submitted by corporate clients in answer to audit inquiries and requests for information (RFI)."
    )

    tbl_resp = doc.add_table(rows=1, cols=4)
    tbl_resp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_resp, "CBD5E1")
    resp_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(resp_cols):
        cell = tbl_resp.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    resp_rows = [
        (
            "Workflow Filter Tabs",
            "Four segmented filter buttons:\n• All Responses (total count)\n• Unreviewed (amber pill)\n• Resolved (emerald pill)\n• Revision Requested (red pill)",
            "• Filter state: 'activeFilter'.\n• Recomputes counts live from active response set.",
            "Filters response cards instantly so auditor can focus on uninspected evidence."
        ),
        (
            "Client Response Cards",
            "Structured inspection card per client submission:\n• RFI Reference Code (e.g., 'REQ-2026-004')\n• RFI Title & Category\n• Client Company Name (with building icon)\n• Submitter Name & Submission Timestamp\n• Client Explanation Note box\n• Attached Evidence Files list (PDF, XLSX with file size and Download button)\n• Status Badge ('Unreviewed', 'Resolved', 'Revision Requested')",
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
            "Button: 'Request Revision' opening modal dialog:\n• Revision feedback textarea explaining what is missing (e.g., 'Please provide official tax invoice with VAT registration number')\n• 'Send Revision Request' button",
            "• Calls 'requestAuditorRevision(id, note)'.\n• Sets status to 'revision_requested'.",
            "Sends revision notice back to the business dashboard attention list so client can re-upload."
        )
    ]

    for item in resp_rows:
        row_cells = tbl_resp.add_row().cells
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

    # 5.4 Requests for Information (RFI) Page
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.4 Auditor Requests for Information (RFI) Page ('/requests')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "The Requests page lets auditors issue formal Requests for Information (RFI), set deadlines, track client fulfillment, and dispatch automatic reminders."
    )

    tbl_req = doc.add_table(rows=1, cols=4)
    tbl_req.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_req, "CBD5E1")
    req_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(req_cols):
        cell = tbl_req.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    req_rows = [
        (
            "Stat Cards (4 Overview Tiles)",
            "• Total Requests\n• Pending\n• Responded\n• Resolved",
            "• Formula: Computed dynamically from 'requests' array based on status property.",
            "Provides quick metrics on audit inquiry clearance rate."
        ),
        (
            "Create New Request Modal\n('New Request' button)",
            "Modal form:\n• Target Company dropdown\n• Request Title (e.g., 'Bank Confirmation Letters')\n• Category (Financial Statements, Fixed Assets, Tax Reliefs, General Inquiry)\n• Priority Level: High (red), Medium (amber), Low (blue)\n• Submission Due Date\n• Detailed Instructions Textarea\n• 'Send Request' button",
            "• POSTs to '/api/auditor/requests'.\n• Writes record to database.",
            "• Dispatches notification to company top bar bell.\n• Adds urgent item to business dashboard 'Requires your attention' card."
        ),
        (
            "Requests Management Table",
            "Table displaying all RFIs:\n• Reference Code (e.g., 'REQ-2026-003')\n• Client Company\n• Title & Description\n• Category\n• Priority Badge\n• Due Date (with overdue highlight if expired)\n• Status Badge ('Pending', 'Responded', 'Resolved')\n• 'Send Reminder' button",
            "• Sourced from '/api/auditor/requests'.\n• Filterable via live search query.",
            "Clicking 'Send Reminder' dispatches a high-priority push/email notification to the company finance director."
        )
    ]

    for item in req_rows:
        row_cells = tbl_req.add_row().cells
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

    # 5.5 Auditor Documents, Discussions, Audit Log, Settings
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.5 Auditor Documents, Discussions, Compliance Log & Settings")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "Supporting compliance modules enable cross-client document inspection, multi-threaded communication, immutable audit logging, and practitioner credential management."
    )

    tbl_aother = doc.add_table(rows=1, cols=4)
    tbl_aother.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_aother, "CBD5E1")
    aother_cols = ["Page / Subsystem", "Key Components & Visual Elements", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(aother_cols):
        cell = tbl_aother.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    aother_rows = [
        (
            "Auditor Documents Repository\n('/auditor-documents')",
            "• Client Document Packs Grid: Card per company showing document completion % and total files.\n• Drill-down view: Comprehensive file table with File Name, Category, AI Confidence Bar, Upload Date, File Size, Status ('Review Required' vs 'Verified'), and 'Verify' checkmark action.\n• 'Request Missing Document' action button.",
            "• Sourced from multi-company document repository.\n• Allows auditor to directly certify individual schedules.",
            "Auditor clicks 'Verify' on a file to confirm figures match trial balance; updates file status to 'verified' with green badge."
        ),
        (
            "Auditor Discussions Page\n('/auditor-discussions')",
            "• Left pane: Multi-client conversation threads grouped by company name.\n• Displays company name, discussion topic, unread counter, and timestamp.\n• Right pane: Full conversation viewer and reply box.",
            "• Sourced from '/api/auditor/discussions'.\n• Bridges auditor responses straight to business discussions.",
            "Allows auditor to manage simultaneous technical clarifications across multiple corporate clients without switching tabs."
        ),
        (
            "Audit Log & Compliance Trail\n('/audit-log')",
            "• Filter bar (Company, Actor, Event Type, Date, FY)\n• Immutable audit log table:\n- Timestamp\n- Company Name\n- Actor (User name & role)\n- Event Type Badge (Success, Warning, Info, Pending)\n- Event Details (e.g., 'Certified Tax Computation AY 2025/26', 'Uploaded Audited P&L')",
            "• Sourced from '/api/auditor/audit-log'.\n• Append-only ledger recording all key compliance transactions.",
            "Satisfies statutory record-keeping requirements under the Sri Lanka Inland Revenue Act and provides evidentiary audit defense."
        ),
        (
            "Auditor Settings & Profile\n('/auditor-settings')",
            "Five comprehensive settings tabs:\n1. Profile & Credentials (CA Sri Lanka No, IRD Practitioner Reg, Firm Reg No, Stamp upload)\n2. Firm & Team (Manage senior auditors, assistants, specialists)\n3. Audit Preferences (Default tax year, Materiality threshold %, Accounting standard)\n4. Notifications (Client upload alerts, deadline reminders)\n5. Security (2FA, active sessions, IP whitelist)",
            "• Sourced from 'AuditorFullSettings' model.\n• Stored in database profile and localStorage.",
            "Configures firm-wide auditing parameters and maintains authenticated practitioner credentials on certified tax returns."
        )
    ]

    for item in aother_rows:
        row_cells = tbl_aother.add_row().cells
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

    # ------------------ SECTION 6: MASTER DATA FLOW & INTEGRATION MATRIX ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("6. Master Data Flow & Cross-Portal Integration Matrix")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(
        "This master cross-reference matrix summarizes how every major frontend UI element connects across data sources, mathematical formulas, user actions, and downstream effects."
    )

    tbl_matrix = doc.add_table(rows=1, cols=5)
    tbl_matrix.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_matrix, "CBD5E1")
    matrix_cols = ["UI Element / Tile", "Portal & Location", "Mathematical Formula / Logic", "Data Origin & Trigger", "Downstream Platform Impact"]
    for i, title in enumerate(matrix_cols):
        cell = tbl_matrix.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    matrix_rows = [
        (
            "Company & FY Badges",
            "Top Navigation Bar (Business)",
            "Displays [Company Name] and [FY Year] from active settings profile.",
            "Settings -> 'taxease_company_settings' via 'taxease_company_updated' event.",
            "Keeps active corporate taxpayer context visible on every page."
        ),
        (
            "Notification Bell & Dropdown",
            "Top Navigation Bar (Both Portals)",
            "Unread counter = count of unread items. Decrements on click.",
            "'/api/notifications' filtered by user role and active company name.",
            "Alerts users to incoming RFIs, uploaded files, and review sign-offs."
        ),
        (
            "Pipeline Progress Bar",
            "Dashboard (Business)",
            "Overall % = 20% * (Stage 1 + Stage 2 + Stage 3 + Stage 4 + Stage 5). Jumps to 100% on Sign-off.",
            "DashboardSummary.steps[] + 'taxease_audit_status_updated'.",
            "Provides executive gauge of corporate audit handover readiness."
        ),
        (
            "Document Stat Tile",
            "Dashboard (Business)",
            "Value = (Uploaded Checklist Count) / (5 Required Statutory Docs).",
            "Evaluates active documents repository against statutory categories.",
            "Warns user if statutory compliance files are missing."
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
            "Requires Attention Card",
            "Dashboard (Business)",
            "Lists all unresolved auditor queries with critical/warning badges.",
            "Direct mirror of open issues from '/api/auditor-review/issues'.",
            "Deep-links user to '/auditor-review' to submit explanations."
        ),
        (
            "Missing Checklist Count",
            "Documents Page (Business)",
            "Missing = Math.max(0, 5 - fulfilledCount).",
            "Client-side inspection of documents table against 5 core keys.",
            "Controls amber warning alert and auto-selects missing upload category."
        ),
        (
            "AI Confidence Bar",
            "Documents & Financials",
            "Mean average of OCR field recognition scores (0 - 100%).",
            "Simulated OCR parser / FastAPI AI extraction endpoint.",
            "Flags low-confidence documents for human audit verification."
        ),
        (
            "Commercial 5-Metric Grid",
            "Financials Page (Business)",
            "1. Gross Turnover\n2. Cost of Sales\n3. Gross Profit (Turnover - COS)\n4. Operating OPEX\n5. Accounting PBT",
            "Extracted from structured schedules table and ledger mappings.",
            "Establishes trading margin and net margin percentages."
        ),
        (
            "CIT Waterfall Banner",
            "Financials Page (Business)",
            "Taxable Income = PBT + Sec 11 Disallowables - 4th Sched Allowances.\nCIT = Taxable Income * 30%.",
            "Statutory calculation under Sri Lanka Inland Revenue Act No. 24.",
            "Calculates official corporate income tax liability estimate."
        ),
        (
            "Assigned Auditor Card",
            "Auditor Review (Business)",
            "Displays auditor name, firm, ICASL badges, and review %.",
            "'/api/auditor-review' & 'taxease_assigned_auditor_[company]'.",
            "Centralizes direct communication and engagement management."
        ),
        (
            "Client Invitations Modal",
            "Companies Page (Auditor)",
            "Lists incoming engagement requests with Accept/Decline actions.",
            "Populated when business clicks 'Invite Auditor' on '/auditor-review'.",
            "Accepting dynamically binds business to auditor's multi-client portfolio."
        ),
        (
            "Auditor Document Checklist Manager",
            "Companies Page (Auditor)",
            "The assigned auditor configures and publishes the custom document checklist for each client company (standard CIT, BOI/export, manufacturing, or custom).",
            "AuditorChecklistModal -> '/api/auditor/checklists' & 'taxease_checklist_[companyName]'.",
            "Directly populates the business's 'AuditorDocumentChecklist.tsx' component and dictates the client's Stage 1 upload requirements."
        ),
        (
            "Client Response Cards",
            "Review Queue / Responses (Auditor)",
            "Displays client explanation note and downloadable evidence files.",
            "Populated when business submits answer on '/auditor-review'.",
            "Allows auditor to either Mark Resolved or Request Revision."
        )
    ]

    for item in matrix_rows:
        row_cells = tbl_matrix.add_row().cells
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

    # ------------------ FOOTER & PAGE NUMBERING ------------------
    for section in doc.sections:
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("TaxEaseLK Platform Specification  •  Confidential & Proprietary")
        r_ft.font.name = "Calibri"
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = RGBColor.from_string("94A3B8")

    # Save document
    filename = "TaxEaseLK_Frontend_Functional_Specification.docx"
    try:
        doc.save(filename)
        print(f"Document successfully created: {filename}")
    except PermissionError:
        alt_filename = "TaxEaseLK_Frontend_Functional_Specification_Updated.docx"
        doc.save(alt_filename)
        print(f"Primary file locked by Word. Saved updated version to: {alt_filename}")

if __name__ == "__main__":
    create_document()
