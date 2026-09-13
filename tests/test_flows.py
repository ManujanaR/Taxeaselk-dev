"""One end-to-end walk through the business <-> auditor flow on a scratch SQLite DB.

Run: .venv/bin/pytest -q
"""
import io
import os
import tempfile

import pytest

_tmp = tempfile.mkdtemp()
os.environ.update({
    "DATABASE_URL": f"sqlite:///{_tmp}/test.db", "SECRET_KEY": "test-secret-key-that-is-long-enough-for-hs256", "UPLOAD_DIR": f"{_tmp}/uploads", "DEBUG": "true",
})

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


@pytest.fixture(scope="module")
def clients():
    with TestClient(app) as biz, TestClient(app) as aud:
        r = biz.post("/api/auth/register/business", json={"email": "fin@abc.lk", "password": "password123", "fullName": "Nimal Silva",
                                                          "companyName": "ABC (Pvt) Ltd", "industrySector": "Services"})
        assert r.status_code == 201, r.text
        r = aud.post("/api/auth/register/auditor", json={"email": "kl@bdo.lk", "password": "password123", "fullName": "K.L. Perera",
                                                        "firmName": "BDO Partners"})
        assert r.status_code == 201, r.text
        yield biz, aud


def unread(c):
    return c.get("/api/notifications").json()["unreadCount"]


def test_role_guards(clients):
    biz, aud = clients
    assert biz.get("/api/auditor/dashboard").status_code == 403
    assert aud.get("/api/dashboard").status_code == 403
    assert TestClient(app).get("/api/dashboard").status_code == 401


def test_full_engagement_flow(clients):
    biz, aud = clients

    # invite -> notification -> accept
    assert biz.post("/api/engagement/invite", json={"auditorEmail": "nobody@x.lk"}).status_code == 404
    r = biz.post("/api/engagement/invite", json={"auditorEmail": "kl@bdo.lk", "taxYear": "2025/26"})
    assert r.status_code == 201, r.text
    assert biz.post("/api/engagement/invite", json={"auditorEmail": "kl@bdo.lk"}).status_code == 409
    assert unread(aud) == 1
    invites = aud.get("/api/auditor/engagements", params={"status": "invited"}).json()
    assert invites[0]["companyName"] == "ABC (Pvt) Ltd"
    eng_id = invites[0]["id"]
    assert aud.post(f"/api/auditor/engagements/{eng_id}/accept").json()["status"] == "active"
    assert biz.get("/api/engagement").json()["engagement"]["status"] == "active"
    assert unread(biz) == 1

    # checklist -> upload against item -> verify
    presets = aud.get("/api/auditor/checklist-presets").json()
    r = aud.put(f"/api/auditor/engagements/{eng_id}/checklist", json={"items": presets[0]["items"]})
    assert r.status_code == 200 and len(r.json()) == 5
    docs = biz.get("/api/documents").json()
    assert docs["missingCount"] == 5 and docs["checklist"]["auditorFirm"] == "BDO Partners"
    item_id = docs["checklist"]["items"][0]["id"]
    r = biz.post("/api/documents", files={"file": ("afs.pdf", PDF, "application/pdf")}, data={"checklistItemId": item_id})
    assert r.status_code == 201, r.text
    doc_id = r.json()["id"]
    assert biz.post("/api/documents", files={"file": ("x.exe", b"MZ", "application/octet-stream")}).status_code == 415
    docs = biz.get("/api/documents").json()
    assert docs["missingCount"] == 4 and docs["checklist"]["items"][0]["providedDocumentId"] == doc_id
    assert aud.get(f"/api/documents/{doc_id}/file").status_code == 200
    assert aud.post(f"/api/auditor/documents/{doc_id}/verify").json()["status"] == "verified"
    assert biz.delete(f"/api/documents/{doc_id}").status_code == 409  # verified docs are immutable

    # financials -> waterfall
    r = biz.put("/api/financials", json={"revenue": 25e6, "costOfSales": 15.2e6, "operatingExpenses": 5.2e6,
                                          "accountingDepreciation": 1.8e6, "entertainmentExpenses": 0.3e6, "taxDepreciationAllowances": 1.5e6})
    assert r.status_code == 200, r.text
    assert r.json()["computed"]["citLiability"] == 1_560_000
    biz.put("/api/company", json={**biz.get("/api/company").json(), "citTaxRateCategory": "sme_14"})
    assert biz.get("/api/financials").json()["computed"]["citLiability"] == 728_000
    assert biz.post("/api/financials/extract", json={"documentId": doc_id}).status_code == 503  # no GEMINI key in tests

    # dashboard + handover
    dash = biz.get("/api/dashboard").json()
    assert dash["steps"][1]["progressPercent"] == 100 and dash["auditorStatus"] == "active"
    assert biz.post("/api/handover").status_code == 204
    assert biz.get("/api/dashboard").json()["steps"][3]["progressPercent"] == 100

    # issue -> respond with file -> resolve
    r = aud.post(f"/api/auditor/engagements/{eng_id}/issues", json={"title": "Entertainment add-back", "comment": "Sec 11(1)(c)", "severity": "critical"})
    issue_id = r.json()["id"]
    assert biz.get("/api/dashboard").json()["attentionItems"][0]["severity"] == "critical"
    r = biz.post(f"/api/issues/{issue_id}/respond", data={"responseText": "Vouchers attached"}, files={"file": ("v.pdf", PDF, "application/pdf")})
    assert r.status_code == 200 and r.json()["status"] == "pending_clarification" and len(r.json()["attachments"]) == 1
    att_id = r.json()["attachments"][0]["id"]
    assert aud.get(f"/api/attachments/{att_id}/file").status_code == 200
    assert aud.post(f"/api/auditor/engagements/{eng_id}/approve").status_code == 409  # open issue blocks sign-off
    assert aud.post(f"/api/auditor/issues/{issue_id}/resolve").json()["status"] == "resolved"

    # RFI -> respond with 2 files -> revision -> respond again -> resolve
    r = aud.post(f"/api/auditor/engagements/{eng_id}/requests", json={"title": "Bank confirmations", "priority": "HIGH", "dueDate": "2026-10-01"})
    req_id = r.json()["id"]
    assert r.json()["referenceCode"] == "REQ-2025-001"
    assert aud.post(f"/api/auditor/requests/{req_id}/remind").status_code == 204
    assert biz.get("/api/nav/badges").json()["requests"] == 1
    r = biz.post(f"/api/requests/{req_id}/respond", data={"note": "See attached"},
                 files=[("attachments", ("a.pdf", PDF, "application/pdf")), ("attachments", ("b.csv", b"a,b\n1,2\n", "text/csv"))])
    assert r.status_code == 201 and len(r.json()["attachments"]) == 2
    resp_id = r.json()["id"]
    assert aud.get("/api/nav/badges").json()["responses"] == 1
    assert aud.post(f"/api/auditor/responses/{resp_id}/revision", json={"note": "Need VAT number on invoice"}).json()["status"] == "revision_requested"
    assert biz.get("/api/requests").json()[0]["status"] == "revision_requested"
    assert biz.post(f"/api/requests/{req_id}/respond", data={"note": "Updated"}).status_code == 201
    assert aud.post(f"/api/auditor/responses/{resp_id}/resolve").json()["status"] == "resolved"

    # discussions
    r = biz.post("/api/threads", json={"topic": "Fixed asset classification", "category": "Fixed Assets", "text": "Is the laptop capex?"})
    assert r.status_code == 201
    thread_id = r.json()["id"]
    assert aud.get("/api/threads").json()[0]["unreadCount"] == 1
    assert aud.post(f"/api/threads/{thread_id}/messages", json={"text": "Yes, Fourth Schedule class 2."}).status_code == 201
    assert aud.get("/api/threads").json()[0]["unreadCount"] == 0
    assert biz.get(f"/api/threads/{thread_id}/messages").json()[1]["senderRole"] == "auditor"
    assert biz.get("/api/threads").json()[0]["unreadCount"] == 0
    assert aud.post(f"/api/threads/{thread_id}/status", json={"status": "closed"}).json()["status"] == "closed"

    # approve -> 100% -> rate
    assert aud.post(f"/api/auditor/engagements/{eng_id}/approve").json()["status"] == "approved"
    assert biz.get("/api/dashboard").json()["progressPercent"] == 100
    assert biz.post("/api/engagement/review", json={"rating": 5, "timeliness": 4, "communication": 5, "technical": 5, "comment": "Great"}).status_code == 201
    assert biz.post("/api/engagement/review", json={"rating": 5, "timeliness": 4, "communication": 5, "technical": 5}).status_code == 409
    reviews = aud.get("/api/auditor/reviews").json()
    assert reviews["averageRating"] == 5.0 and reviews["completedAudits"] == 1
    assert biz.get("/api/engagement").json()["auditor"]["averageRating"] == 5.0

    # audit trail + auditor dashboard
    log = aud.get("/api/auditor/audit-log").json()
    assert {e["eventType"] for e in log} >= {"AUDITOR_INVITED", "CHECKLIST_PUBLISHED", "DOCUMENT_UPLOADED", "AUDIT_APPROVED", "AUDITOR_RATED"}
    d = aud.get("/api/auditor/dashboard").json()
    assert d["completedThisPeriod"] == 1 and d["workload"]["approved"] == 1

    # read-all + logout
    assert biz.post("/api/notifications/read-all").status_code == 204 and unread(biz) == 0
    assert biz.post("/api/auth/logout").status_code == 204 and biz.get("/api/auth/me").status_code == 401
