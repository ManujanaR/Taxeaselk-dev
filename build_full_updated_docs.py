# -*- coding: utf-8 -*-
"""
Comprehensive script to generate updated Word documents covering:
1. Auditor Side Notifications vs Business Side Notifications
2. Business and Auditor Profile Icons, Display Names, Role Chips, and Copyable User IDs
3. Auditor Discussions (multi-client threads, search, status toggle, message bubbles, reply composer)
4. Auditor Settings (all 5 tabs: Profile & Credentials, Firm & Team, Preferences, Notifications, Security)
5. Assigned Auditor Rating & Reputation System (RateAuditorModal, 3 dimensions, and AuditorRankRating drawer)
"""
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_frontend_specification():
    doc = Document()

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

    def add_callout(text_list, title="SPECIFICATION NOTE", color_hex=NAVY_HEX, bg_hex="EFF6FF"):
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
    run_sub = p_sub.add_run("Comprehensive element-by-element functional definition, formulas, data origin mappings, auditor interactions, dynamic pipeline behaviors, rating calculations, profile identity menus, and settings across Business and Auditor portals.")
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

    # ------------------ SECTION 1: ARCHITECTURE ------------------
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
        "2. Auditor Portal: Empowers chartered accountants and audit firms to oversee multi-client portfolios, issue Requests for Information (RFI), review client responses and attached evidence, verify corporate tax packs, customize document checklists per company, and execute formal audit sign-offs."
    )

    add_callout([
        "Key System Interactions Explicitly Documented:",
        "• Top Nav Bar & Badges: Company name & FY update from Settings; Auditor sees All Companies + Year selector.",
        "• Notifications Engine: Business notifications grab auditor RFIs, reviews, and messages; Auditor notifications grab client uploads, responses, appointment invites, and discussions.",
        "• Profile Icon & Identity Menu: Shows user initials avatar, display name, email, role chip ('Admin' vs 'Auditor'), copyable User ID ('BIZ-XXXXXXXX' vs 'AUD-XXXXXXXX'), and secure logout.",
        "• Assigned Auditor Rating Engine: How businesses submit 1-5 star reviews with 3 performance dimensions (Timeliness, Communication, Tax Rigor), and how this drives the auditor's top bar Rank Badge and reputation drawer.",
        "• Auditor Discussions: Multi-client thread selector, company/topic search filter, status toggle (Open/Closed), bubble distinction, and real-time reply composer.",
        "• Auditor Settings: Full 5-tab breakdown (Profile & Credentials, Firm & Team, Audit Preferences, Notifications, Security & Access).",
        "• Auditor-Created Document Checklist: How the auditor customizes and publishes statutory document requirements per company, and how the business fulfills them."
    ], title="SPECIFICATION STANDARD & SCOPE", color_hex=NAVY_HEX, bg_hex="F0FDF4")

    # ------------------ SECTION 2: COMMON LAYOUT & CHROME ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("2. Common Layout, Top Bar & Global Chrome Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

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
            "Displays 'All Companies' badge and active Tax Year dropdown (e.g., '2025/26').",
            "• Origin: Auditor multi-client portfolio data (cached in localStorage and Supabase company registry).",
            "Allows auditor to toggle between consolidated view across all assigned clients or filter down to a single corporate entity."
        ),
        (
            "Business Notifications\n(Top Bar Bell Panel)",
            "Notification bell with dynamic red unread counter badge. Clicking opens feed showing:\n• Auditor RFIs & Information Requests\n• Audit Review comments & discrepancy notices\n• Status updates ('Under Review' -> 'Approved')\n• New discussion replies from assigned auditor\n• Published document checklist updates",
            "• Origin: '/api/notifications' filtered by role='business' and company_name.\n• Automatically listens to real-time events and pollers.",
            "• Clicking notification marks item as read, decrements counter, and deep-links directly to target page (/auditor-review, /documents, /discussions).\n• Includes 'Mark All as Read' button."
        ),
        (
            "Auditor Notifications\n(Top Bar Bell Panel)",
            "Notification bell with dynamic red unread counter badge. Clicking opens feed showing:\n• Client document uploads (e.g. 'ABC (Pvt) Ltd uploaded Financial Statements')\n• Client RFI responses & evidence attachments (e.g. 'ABC (Pvt) Ltd responded to REQ-2026-004')\n• Client appointment invitations (e.g. 'New Engagement Request from XYZ Ltd')\n• Client discussion messages (e.g. 'Inquiry on Entertainment Expenses')\n• Statutory filing deadline approaching reminders",
            "• Origin: '/api/notifications' filtered by role='auditor'.\n• Grabs multi-client events across all assigned companies.",
            "• Clicking notification marks item as read, decrements badge counter, and deep-links directly to target client page (/responses, /auditor-documents, /auditor-discussions).\n• Includes 'Mark All as Read' and 'View All' footer."
        ),
        (
            "Profile Icon & Menu\n(Business Side)",
            "Top-right user avatar pill showing:\n• Avatar circle with initials: 'AU' (Admin User)\n• Role chip: 'Admin'\n• Display Name: 'Admin User'\n• Registered Email: 'admin@abc.lk'\n• Formatted User ID: 'BIZ-XXXXXXXX' with 1-click Copy button\n• Links: Profile & Settings (/settings)\n• Sign Out button",
            "• Sourced from 'taxease_user' session storage and Supabase Auth.\n• User ID formatted with prefix 'BIZ-' for business accounts.",
            "• Clicking 'Copy' copies User ID to clipboard with green checkmark confirmation.\n• Clicking 'Settings' navigates to '/settings'.\n• Clicking 'Sign Out' clears tokens and redirects to '/sign-in'."
        ),
        (
            "Profile Icon & Menu\n(Auditor Side)",
            "Top-right user avatar pill showing:\n• Avatar circle with initials: 'PA' (Professional Auditor)\n• Role chip: 'Auditor'\n• Display Name: 'Professional Auditor' / Lead Partner\n• Registered Email: 'auditor@example.com'\n• Formatted User ID: 'AUD-XXXXXXXX' with 1-click Copy button\n• Links: Profile & Credentials (/auditor-settings)\n• Sign Out button",
            "• Sourced from 'taxease_user' session storage and Supabase Auth.\n• User ID formatted with prefix 'AUD-' for auditor accounts.",
            "• Clicking 'Copy' copies Auditor ID to clipboard.\n• Clicking 'Profile' or 'Settings' navigates to '/auditor-settings'.\n• Clicking 'Sign Out' purges session and redirects to '/sign-in'."
        ),
        (
            "Auditor Rank & Rating Badge\n(Auditor Top Bar Extra)",
            "Top Bar badge displaying auditor's public standing:\n• Rank Chip: 'Rank #1' or 'Verified Auditor'\n• Star Score: e.g. '4.9 ★' in gold\n• Total Reviews Count: e.g. '(49)'\n• Chevron indicator opening comprehensive reputation drawer",
            "• Dynamic sync via 'taxease_auditor_rating_updated' event, localStorage, and '/api/auditors/{email}/reviews'.\n• Recomputes live whenever a business client submits a review via RateAuditorModal.",
            "Clicking opens reputation drawer displaying overall rating, completed audits count, on-time sign-off rate, dimension breakdown (Accuracy, Responsiveness, Turnaround), and verified client review comments."
        ),
        (
            "Language Switcher Toggle\n(EN | සිං | தமி)",
            "Three-way segmented toggle pill in the top header:\n• EN (English)\n• සිං (Sinhala)\n• தமி (Tamil)",
            "• Origin: Hand-rolled zero-dependency i18n Context ('LanguageContext.tsx') with translation dictionaries in 'translations.ts'.\n• Persisted to localStorage ('taxease_language').",
            "Instantly re-renders all UI titles, headers, navigation labels, and subtitles across the entire app into the selected national language without losing page state."
        ),
        (
            "Navigation Sidebar",
            "Brand logo (TaxEaseLK with flag emblem) + structured navigation links with Lucide icons.\n• Business: Dashboard, Documents, Financials, Auditor Review, Discussions, Settings.\n• Auditor: Dashboard, Companies, Documents, Responses, Requests, Discussions, Settings.",
            "Highlights active route with blue accent bar and light-blue background fill. Clicking smoothly routes between pages."
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

    # ------------------ SECTION 3: AUTH ------------------
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)
    r = h1.add_run("3. Authentication & Onboarding Module Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

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
    r = h1.add_run("4. Business Portal: Detailed Component Explanations")
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
            "• Formula: (Uploaded Checklist Documents / Total Required Documents set by Assigned Auditor) * 100%.\n• Source: Evaluates active documents against the company's checklist.",
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

    # 4.2 Documents
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.2 Business Documents Page ('/documents') & Auditor-Customized Checklist")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

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
            "Auditor Document Checklist\n(Configured by Assigned Auditor)",
            "A dynamic, company-specific statutory checklist card itemizing the documents requested by the appointed auditor:\n• Shows presets: Standard Statutory CIT, BOI & Exporter Pack, or Manufacturing & Trading Pack\n• Custom document requirements added by the auditor\n• Header displays: 'Requested by [Auditor Name] • [Firm Name]'\n• Dynamic fulfillment indicator (Provided vs. Missing count & Audit Pack Readiness %)",
            "• Origin: Created and published by the assigned auditor via AuditorChecklistModal ('/api/auditor/checklists' & 'taxease_checklist_[companyName]').\n• Auto-syncs via 'taxease_checklist_updated' window event whenever the assigned auditor modifies the company's checklist requirements.",
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

    # 4.3 Financials
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.3 Business Financials & Tax Computation Page ('/financials')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

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

    # 4.4 Auditor Review & Rating
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.4 Business Auditor Review Page ('/auditor-review') & Rating Engine")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

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

    # 4.5 Discussions & 4.6 Settings
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("4.5 Business Discussions ('/discussions') & 4.6 Settings ('/settings')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    tbl_bother = doc.add_table(rows=1, cols=4)
    tbl_bother.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_bother, "CBD5E1")
    bother_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(bother_cols):
        cell = tbl_bother.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

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

    for item in bother_rows:
        row_cells = tbl_bother.add_row().cells
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
    r = h1.add_run("5. Auditor Portal: Detailed Component Explanations")
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    # 5.1 & 5.2
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.1 Auditor Dashboard & 5.2 Companies Management")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    tbl_adash = doc.add_table(rows=1, cols=4)
    tbl_adash.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_adash, "CBD5E1")
    adash_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
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
            "Auditor Dashboard Overview Tiles",
            "1. Active Clients (assigned companies count)\n2. Pending Reviews / Under Review (active computations count)\n3. Completed This Period (certified returns count)\n4. Priority Reviews Card (sorted by urgency with due dates)\n5. Workload Breakdown (Pending, Under Review, Waiting, Ready, Completed)",
            "• Sourced from '/api/auditor/dashboard'.\n• Aggregates active client portfolio metrics.",
            "Clicking any tile or workload row routes directly to that filtered review queue."
        ),
        (
            "Companies Directory Table",
            "Master client registry table:\n• Company Name & TIN (with Copy button)\n• Financial Year\n• CIT Filing Status Badge ('Draft', 'Under Review', 'Ready', 'Approved', 'Waiting')\n• Issue Count Pair (Critical in red / Warning in amber)\n• Pack Progress Bar with %\n• Due Date countdown chip\n• Actions: 'View Profile' & 'Open Checklist'",
            "• Sourced from '/api/auditor/companies'.",
            "• 'View Profile' opens company drawer.\n• 'Open Checklist' opens AuditorChecklistModal."
        ),
        (
            "Auditor Document Checklist Manager\n('AuditorChecklistModal.tsx')",
            "Modal allowing auditor to customize statutory document requirements per company:\n• Presets: Standard Statutory CIT, BOI & Exporter Pack, Manufacturing & Trading Pack\n• Add Custom Document Items with required/optional toggles and specific auditor notes\n• 'Save & Publish Checklist' button",
            "• Writes to 'taxease_checklist_[companyName]' and POSTs to '/api/auditor/checklists'.\n• Dispatches 'taxease_checklist_updated' window event.",
            "Instantly publishes the custom checklist to the client's '/documents' page and dynamically sets the company's Stage 1 upload checklist."
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

    # 5.3 Responses, 5.4 Requests, 5.5 Documents
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.3 Review Queue / Responses, 5.4 Requests & 5.5 Auditor Documents")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    tbl_aops = doc.add_table(rows=1, cols=4)
    tbl_aops.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_aops, "CBD5E1")
    aops_cols = ["Component / Section", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(aops_cols):
        cell = tbl_aops.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    aops_rows = [
        (
            "Review Queue / Responses\n('/responses')",
            "• Segmented filter tabs: All, Unreviewed, Resolved, Revision Requested.\n• Client Response Cards: RFI ID, Company Name, Category, Client Explanation Note, Submitter Name & Timestamp, Attached Evidence Files (with Download action).\n• Action Buttons: 'Mark as Resolved' & 'Request Revision' modal.",
            "• Sourced from '/api/auditor/responses'.\n• Populated when business answers inquiries on '/auditor-review'.",
            "• 'Mark as Resolved' resolves the issue.\n• 'Request Revision' sends revision notice back to the company's attention card."
        ),
        (
            "Requests for Information\n('/requests')",
            "• Stat Overview: Total Requests, Pending, Responded, Resolved.\n• 'New Request' button opening modal (Select Company, Title, Category, Priority High/Med/Low, Due Date, Description).\n• RFIs Table with 'Send Reminder' action.",
            "• Sourced from '/api/auditor/requests'.",
            "Creates formal audit requests; alerts client via top bar bell and dashboard attention notices."
        ),
        (
            "Auditor Documents Repository\n('/auditor-documents')",
            "• Multi-company document packs overview.\n• Drill-down table: File Name, Document Type, AI OCR Confidence Bar %, Upload Date, File Size, Status ('Review Required' vs 'Verified').\n• Actions: 'Verify' checkmark and 'Request Missing Document'.",
            "• Sourced from client uploaded document store.",
            "Auditor clicks 'Verify' to mark a file verified; sets status to 'verified' with green badge."
        )
    ]

    for item in aops_rows:
        row_cells = tbl_aops.add_row().cells
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

    # 5.6 Auditor Discussions
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.6 Auditor Discussions Page ('/auditor-discussions') - Multi-Client Communication")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    tbl_adisc = doc.add_table(rows=1, cols=4)
    tbl_adisc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_adisc, "CBD5E1")
    adisc_cols = ["Feature / Sub-Component", "Displayed Content & Logic", "Data Origin & Backend Flow", "Interaction & Behavior"]
    for i, title in enumerate(adisc_cols):
        cell = tbl_adisc.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

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

    for item in adisc_rows:
        row_cells = tbl_adisc.add_row().cells
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

    # 5.7 Audit Log & 5.8 Auditor Settings
    h2 = doc.add_heading(level=2)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    r = h2.add_run("5.7 Compliance Audit Log & 5.8 Auditor Settings ('/auditor-settings')")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE_HEX)

    tbl_asett = doc.add_table(rows=1, cols=4)
    tbl_asett.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_asett, "CBD5E1")
    asett_cols = ["Subsystem / Tab", "Displayed Content & Logic", "Data Origin & Calculation Formula", "Interaction & Behavior"]
    for i, title in enumerate(asett_cols):
        cell = tbl_asett.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor.from_string(NAVY_HEX)

    asett_rows = [
        (
            "Audit Log & Compliance Trail\n('/audit-log')",
            "• Filter bar (Company, Actor, Event Type, Date, FY)\n• Immutable audit log table with Timestamp, Company Name, Actor & Role, Event Type Badge (Success, Warning, Info, Pending), and Event Details.\n• Append-only ledger recording all key compliance transactions.",
            "• Sourced from '/api/auditor/audit-log'.",
            "Satisfies statutory record-keeping requirements under the Sri Lanka Inland Revenue Act and provides evidentiary audit defense."
        ),
        (
            "Auditor Settings Tab 1:\nProfile & Credentials",
            "• Full Name, Work Email, Phone, Designation\n• Professional License Number\n• CA Sri Lanka / ICASL Member Number\n• IRD Tax Practitioner Registration Number\n• Firm Registration Number & Address\n• Digital Signature / Stamp Upload (with instant image preview)",
            "• Sourced from 'AuditorProfileSettings' model and localStorage ('taxease_auditor_profile').",
            "Maintains authenticated professional credentials stamped onto certified tax returns."
        ),
        (
            "Auditor Settings Tab 2:\nFirm & Team Management",
            "• Audit team hierarchy table: Audit Partner, Senior Auditor, Audit Assistant, Tax Specialist\n• Columns: Name & Initials, Email, Role Badge, Assigned Companies Count, Status ('Active' / 'Invited')\n• 'Invite Team Member' button & modal",
            "• Sourced from firm user directory.",
            "Allows audit firms to delegate client company portfolios across senior auditors and assistants."
        ),
        (
            "Auditor Settings Tab 3:\nAudit Preferences",
            "• Default Tax Year (e.g. '2025/26')\n• Accounting Standard dropdown ('SLFRS / LKAS for SMEs' vs 'Full SLFRS')\n• Materiality Threshold Percentage slider (e.g. 5%)\n• Automated Client Reminder Schedules (days before deadline)\n• Auto-Request Standard Pack toggle\n• Strict VAT/SVAT Reconciliation toggle",
            "• Configures firm-wide auditing rules applied across client tax calculations.",
            "Controls automated reminder dispatches and default checklist templates."
        ),
        (
            "Auditor Settings Tab 4:\nNotifications",
            "Granular notification channel toggles:\n• Client Document Uploaded\n• Client Response Received\n• Discussion Message Received\n• Deadline Approaching\n• Client Invitation Received\n• Digest Frequency picker ('Instant', 'Daily Digest', 'Weekly')",
            "• Controls email and in-app notification triggers for the auditor.",
            "Ensures audit partners stay informed on client submissions without alert fatigue."
        ),
        (
            "Auditor Settings Tab 5:\nSecurity & Access",
            "• Two-Factor Authentication (2FA) switch\n• Session Timeout duration (minutes)\n• IP Whitelist toggle\n• Immutable Audit Trail enforcement toggle\n• Active Devices & Sessions table (Device, Browser, IP, Last Active, 'Revoke' action)",
            "• Firm security policy and device authorization store.",
            "Guarantees compliance with professional data protection and confidentiality mandates."
        )
    ]

    for item in asett_rows:
        row_cells = tbl_asett.add_row().cells
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

    # Footer
    for section in doc.sections:
        footer = section.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_ft = p_ft.add_run("TaxEaseLK Platform Specification  •  Confidential & Proprietary")
        r_ft.font.name = "Calibri"
        r_ft.font.size = Pt(8.5)
        r_ft.font.color.rgb = RGBColor.from_string("94A3B8")

    filename = "TaxEaseLK_Frontend_Functional_Specification_Final.docx"
    doc.save(filename)
    print(f"Document successfully created: {filename}")

if __name__ == "__main__":
    create_frontend_specification()
