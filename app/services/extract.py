"""Gemini extraction of the six CIT inputs from a company's uploaded statutory documents.

PDFs and images go to the model natively; XLSX/CSV are flattened to text first. All of a
company's documents are sent in one request, since figures are often split across statements
(income statement in one file, the capital-allowance schedule in another). The result is a
suggestion the user confirms in the form; nothing is saved here.
"""
import csv
import io
from pathlib import Path

from fastapi import HTTPException
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

from app.core.config import settings
from app.models import Document

MAX_TEXT_CHARS = 60_000
# ponytail: inline; switch to client.files.upload() if statutory sets routinely exceed the inline cap.
MAX_INLINE_TOTAL = 18 * 1024 * 1024  # under Gemini's ~20MB inline request ceiling (uploads are <=10MB each)
NATIVE_EXTS = (".pdf", ".png", ".jpg", ".jpeg")
TEXT_EXTS = (".xlsx", ".csv")
RETRYABLE_CODES = {429, 500, 502, 503, 504}  # newly-GA flash models return transient 503 "high demand"
FALLBACK_MODELS = ("gemini-3.6-flash", "gemini-3.8-flash")  # tried in order after the configured model
FIELDS = ["revenue", "cost_of_sales", "operating_expenses", "accounting_depreciation", "entertainment_expenses", "tax_depreciation_allowances"]

PROMPT = """You are a Sri Lankan chartered accountant preparing a Corporate Income Tax computation under the
Inland Revenue Act No. 24 of 2017. From the attached financial document(s) extract these annual figures in LKR
for the most recent financial year shown:
- revenue: total revenue / turnover / sales
- cost_of_sales: cost of sales / cost of goods sold
- operating_expenses: total operating expenses (administrative + selling + distribution), excluding cost of sales and finance costs
- accounting_depreciation: depreciation and amortisation charged in the accounts
- entertainment_expenses: entertainment expenses
- tax_depreciation_allowances: capital allowances / tax depreciation under the Fourth Schedule (only if explicitly stated)
The figures may be split across several attached documents; combine them. Where the same figure appears in
more than one document with different values, prefer the audited / final statement and note the discrepancy.
Rules: use positive numbers in full rupees (not thousands). If a figure is not present, set value to null and
confidence to 0. Never guess or derive a figure that is not in the document. confidence is 0-1. Put any
caveats (e.g. figures stated in Rs. '000, comparative year used, discrepancies) in notes."""


class Figure(BaseModel):
    value: float | None = Field(description="Amount in LKR, or null if not found")
    confidence: float = Field(ge=0, le=1)


class CitExtraction(BaseModel):
    revenue: Figure
    cost_of_sales: Figure
    operating_expenses: Figure
    accounting_depreciation: Figure
    entertainment_expenses: Figure
    tax_depreciation_allowances: Figure
    notes: str = ""


def _spreadsheet_text(data: bytes, ext: str) -> str:
    if ext == ".csv":
        return data.decode(errors="ignore")[:MAX_TEXT_CHARS]
    import openpyxl  # xlsx only; legacy .xls is not supported by openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    out = io.StringIO()
    w = csv.writer(out)
    for ws in wb.worksheets:
        w.writerow([f"# sheet: {ws.title}"])
        for row in ws.iter_rows(values_only=True):
            if any(c is not None for c in row):
                w.writerow(["" if c is None else c for c in row])
        if out.tell() > MAX_TEXT_CHARS:
            break
    return out.getvalue()[:MAX_TEXT_CHARS]


def _build_parts(docs: list[Document]) -> tuple[list, list[str]]:
    """Turn each readable document into Gemini content parts. Returns (parts, skipped_names).

    Unsupported types (.xls) and docs that would blow the inline size cap are skipped, not fatal.
    """
    from google.genai import types

    from app.services import files
    parts: list = []
    skipped: list[str] = []
    total = 0
    for doc in docs:
        ext = Path(doc.stored_name).suffix.lower()
        if ext not in NATIVE_EXTS and ext not in TEXT_EXTS:
            skipped.append(f"{doc.name} (unsupported type)")
            continue
        data = files.read_bytes(doc.stored_name)
        if total + len(data) > MAX_INLINE_TOTAL:
            skipped.append(f"{doc.name} (skipped, request size limit)")
            continue
        total += len(data)
        if ext in NATIVE_EXTS:
            parts.append(types.Part.from_bytes(data=data, mime_type=doc.content_type))
        else:
            parts.append(f"Document '{doc.name}' as CSV rows:\n{_spreadsheet_text(data, ext)}")
    return parts, skipped


def _model_chain() -> list[str]:
    """Primary model first, then fallbacks — on a transient overload a different pool may be free."""
    chain = [settings.GEMINI_MODEL]
    for m in FALLBACK_MODELS:
        if m not in chain:
            chain.append(m)
    return chain


def _generate(client, contents):
    """One structured-JSON call; on transient 503/429 fall through to the next model, else 502."""
    from google.genai import errors, types
    cfg = types.GenerateContentConfig(response_mime_type="application/json", response_schema=CitExtraction, temperature=0)
    last = None
    for model in _model_chain():
        try:
            return client.models.generate_content(model=model, contents=contents, config=cfg)
        except errors.APIError as e:
            last = e
            if e.code in RETRYABLE_CODES:
                continue  # busy pool — try the next model
            raise HTTPException(502, f"Gemini extraction failed: {e}") from e
        except Exception as e:  # network/other errors surface as a clean 502, never a 500 stack trace
            raise HTTPException(502, f"Gemini extraction failed: {e}") from e
    raise HTTPException(503, "The extraction model is busy right now — please try again in a moment.") from last


def extract_cit_inputs(docs: list[Document]) -> dict:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(503, "Document extraction is not configured (GEMINI_API_KEY missing)")
    from google import genai

    parts, skipped = _build_parts(docs)
    if not parts:
        raise HTTPException(415, "No readable documents to extract (supports PDF, XLSX, CSV, PNG and JPG)")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    resp = _generate(client, [*parts, PROMPT])
    try:
        result: CitExtraction = resp.parsed or CitExtraction.model_validate_json(resp.text)
    except Exception as e:  # a response we can't parse is a clean 502, never a 500 stack trace
        raise HTTPException(502, f"Could not read the extraction result: {e}") from e

    notes = result.notes
    if skipped:
        notes = (notes + " " if notes else "") + "Not read: " + "; ".join(skipped) + "."
    return {
        "inputs": {to_camel(f): getattr(result, f).value for f in FIELDS},
        "confidence": {to_camel(f): getattr(result, f).confidence for f in FIELDS},
        "notes": notes,
    }
