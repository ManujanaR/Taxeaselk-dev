"""Gemini extraction of the six CIT inputs from an uploaded statutory document.

PDFs and images go to the model natively; XLSX/CSV are flattened to text first.
The result is a suggestion the user confirms in the form; nothing is saved here.
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
FIELDS = ["revenue", "cost_of_sales", "operating_expenses", "accounting_depreciation", "entertainment_expenses", "tax_depreciation_allowances"]

PROMPT = """You are a Sri Lankan chartered accountant preparing a Corporate Income Tax computation under the
Inland Revenue Act No. 24 of 2017. From the attached financial document extract these annual figures in LKR
for the most recent financial year shown:
- revenue: total revenue / turnover / sales
- cost_of_sales: cost of sales / cost of goods sold
- operating_expenses: total operating expenses (administrative + selling + distribution), excluding cost of sales and finance costs
- accounting_depreciation: depreciation and amortisation charged in the accounts
- entertainment_expenses: entertainment expenses
- tax_depreciation_allowances: capital allowances / tax depreciation under the Fourth Schedule (only if explicitly stated)
Rules: use positive numbers in full rupees (not thousands). If a figure is not present, set value to null and
confidence to 0. Never guess or derive a figure that is not in the document. confidence is 0-1. Put any
caveats (e.g. figures stated in Rs. '000, comparative year used) in notes."""


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


def _spreadsheet_text(path: Path) -> str:
    if path.suffix.lower() == ".csv":
        return path.read_text(errors="ignore")[:MAX_TEXT_CHARS]
    import openpyxl  # xlsx only; legacy .xls is not supported by openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
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


def extract_cit_inputs(doc: Document) -> dict:
    if not settings.GEMINI_API_KEY:
        raise HTTPException(503, "Document extraction is not configured (GEMINI_API_KEY missing)")
    from google import genai
    from google.genai import types

    path = settings.UPLOAD_DIR / doc.stored_name
    if not path.is_file():
        raise HTTPException(404, "File missing from storage")
    ext = path.suffix.lower()
    if ext in (".pdf", ".png", ".jpg", ".jpeg"):
        parts = [types.Part.from_bytes(data=path.read_bytes(), mime_type=doc.content_type), PROMPT]
    elif ext in (".xlsx", ".csv"):
        parts = [f"Document '{doc.name}' as CSV rows:\n{_spreadsheet_text(path)}", PROMPT]
    else:
        raise HTTPException(415, "Extraction supports PDF, XLSX, CSV, PNG and JPG")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    try:
        resp = client.models.generate_content(
            model=settings.GEMINI_MODEL, contents=parts,
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=CitExtraction, temperature=0),
        )
        result: CitExtraction = resp.parsed or CitExtraction.model_validate_json(resp.text)
    except Exception as e:  # network/model errors surface as a clean 502, never a 500 stack trace
        raise HTTPException(502, f"Gemini extraction failed: {e}") from e

    return {
        "inputs": {to_camel(f): getattr(result, f).value for f in FIELDS},
        "confidence": {to_camel(f): getattr(result, f).confidence for f in FIELDS},
        "notes": result.notes,
    }
