"""Multi-document extraction: the part-builder's skip/size-cap logic and the empty-set guard."""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")
os.environ.setdefault("UPLOAD_DIR", f"{_tmp}/uploads")
os.environ["GEMINI_API_KEY"] = ""

from fastapi import HTTPException  # noqa: E402
from app.models import Document  # noqa: E402
from app.services import extract, files  # noqa: E402


def _doc(name, ctype="application/pdf"):
    return Document(stored_name=name, content_type=ctype, name=name)


def test_build_parts_skips_unsupported_and_oversize(monkeypatch):
    monkeypatch.setattr(files, "read_bytes", lambda _n: b"x" * 20)
    monkeypatch.setattr(extract, "MAX_INLINE_TOTAL", 25)  # room for one 20-byte doc, not two
    docs = [_doc("income.pdf"), _doc("legacy.xls"), _doc("schedule.pdf")]
    parts, skipped = extract._build_parts(docs)
    assert len(parts) == 1  # income.pdf fits; .xls unsupported; second pdf busts the cap
    assert any("legacy.xls" in s and "unsupported" in s for s in skipped)
    assert any("schedule.pdf" in s and "size" in s for s in skipped)


def _api_error(code):
    from google.genai import errors
    e = errors.APIError.__new__(errors.APIError)
    e.code = code
    return e


def test_generate_falls_through_to_next_model_on_503(monkeypatch):
    import pytest
    monkeypatch.setattr(extract, "FALLBACK_MODELS", ("m-b", "m-c"))
    monkeypatch.setattr(extract.settings, "GEMINI_MODEL", "m-a")
    tried = []

    class FakeModels:
        def generate_content(self, *, model, **_kw):
            tried.append(model)
            if model != "m-c":
                raise _api_error(503)  # first two pools busy
            return "RESP"

    class FakeClient:
        models = FakeModels()

    assert extract._generate(FakeClient(), ["x"]) == "RESP"
    assert tried == ["m-a", "m-b", "m-c"]

    # a non-retryable error stops immediately and surfaces as 502
    class AlwaysBad:
        def generate_content(self, **_kw):
            raise _api_error(400)

    with pytest.raises(HTTPException) as ei:
        extract._generate(type("C", (), {"models": AlwaysBad()})(), ["x"])
    assert ei.value.status_code == 502

    # all pools busy -> clean 503
    class AllBusy:
        def generate_content(self, **_kw):
            raise _api_error(503)

    with pytest.raises(HTTPException) as ei:
        extract._generate(type("C", (), {"models": AllBusy()})(), ["x"])
    assert ei.value.status_code == 503


def test_extract_endpoint_requires_documents():
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        c.post("/api/auth/register/business", json={"email": "nodocs@x.lk", "password": "password123",
                                                    "fullName": "No Docs", "companyName": "NoDocs Ltd", "industrySector": "Services"})
        assert c.post("/api/financials/extract").status_code == 400  # nothing uploaded yet


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
