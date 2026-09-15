"""One end-to-end walk through the business <-> auditor flow on a scratch SQLite DB.

Run: .venv/bin/pytest -q
"""
import os
import tempfile
import time

import pytest

_tmp = tempfile.mkdtemp()
os.environ.update({
    "DATABASE_URL": f"sqlite:///{_tmp}/test.db", "SECRET_KEY": "test-secret-key-that-is-long-enough-for-hs256", "UPLOAD_DIR": f"{_tmp}/uploads", "DEBUG": "true",
})

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.services import events  # noqa: E402

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

    # directory lists the registered auditor (ranked; no reviews yet) and is searchable
    directory = biz.get("/api/auditors/directory").json()
    assert any(a["email"] == "kl@bdo.lk" and a["completedAudits"] == 0 for a in directory)
    assert [a["email"] for a in biz.get("/api/auditors/directory", params={"search": "bdo"}).json()] == ["kl@bdo.lk"]
    assert biz.get("/api/auditors/directory", params={"search": "zzz"}).json() == []

    # invite -> notification -> accept
    assert biz.post("/api/engagement/invite", json={"auditorEmail": "nobody@x.lk"}).status_code == 404
    r = biz.post("/api/engagement/invite", json={"auditorEmail": "kl@bdo.lk", "taxYear": "2025/26"})
    assert r.status_code == 201, r.text
    assert biz.post("/api/engagement/invite", json={"auditorEmail": "kl@bdo.lk"}).status_code == 409
    assert unread(aud) == 1
    invites = aud.get("/api/auditor/engagements", params={"status": "invited"}).json()
    assert invites[0]["companyName"] == "ABC (Pvt) Ltd"
    eng_id = invites[0]["id"]
    biz_user_id = biz.get("/api/auth/me").json()["user"]["id"]
    q = events.subscribe_queue(biz_user_id)
    assert aud.post(f"/api/auditor/engagements/{eng_id}/accept").json()["status"] == "active"
    for _ in range(50):  # publish hops onto the event loop thread; give it a moment
        if q.qsize():
            break
        time.sleep(0.02)
    ev = q.get_nowait()
    assert ev["type"] == "notification" and ev["notification"]["title"] == "Auditor accepted your invitation"
    events.unsubscribe_queue(biz_user_id, q)
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
    assert docs["missingCount"] == 4 and docs["checklist"]["items"][0]["providedDocumentId"] == doc_id and docs["unsentCount"] == 1
    # the auditor's view does not move before submission: no progress, no audit-log trace
    assert aud.get("/api/auditor/engagements").json()[0]["progressPercent"] == 0
    assert not any(e["eventType"] == "DOCUMENT_UPLOADED" for e in aud.get("/api/auditor/audit-log").json())
    # private until the handover pack is submitted
    assert aud.get(f"/api/documents/{doc_id}/file").status_code == 404
    assert aud.post(f"/api/auditor/documents/{doc_id}/verify").status_code == 404
    assert aud.get(f"/api/auditor/engagements/{eng_id}").json()["documents"] == []
    assert unread(aud) == 1  # no upload notification yet

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
    assert biz.get("/api/dashboard").json()["steps"][2]["progressPercent"] == 100  # stage 3 = handover
    assert aud.get("/api/auditor/engagements").json()[0]["progressPercent"] > 0
    assert biz.get("/api/documents").json()["unsentCount"] == 0
    assert len(aud.get(f"/api/auditor/engagements/{eng_id}").json()["documents"]) == 1
    assert aud.get(f"/api/documents/{doc_id}/file").status_code == 200
    assert aud.post(f"/api/auditor/documents/{doc_id}/verify").json()["status"] == "verified"
    assert biz.delete(f"/api/documents/{doc_id}").status_code == 409  # verified docs are immutable
    # after handover, new uploads reach the auditor immediately
    tb = biz.post("/api/documents", files={"file": ("tb.csv", b"a,b\n", "text/csv")}).json()
    assert tb["submittedAt"] is not None

    # request (HIGH) -> business answers with files -> auditor sends back -> answers again -> resolve
    r = aud.post(f"/api/auditor/engagements/{eng_id}/requests", json={"title": "Entertainment add-back", "description": "Sec 11(1)(c)", "priority": "HIGH"})
    assert r.status_code == 201 and r.json()["referenceCode"] == "REQ-2025-001" and r.json()["companyName"] == "ABC (Pvt) Ltd"
    req_id = r.json()["id"]
    dash = biz.get("/api/dashboard").json()
    assert dash["attentionItems"][0]["severity"] == "critical" and dash["attentionItems"][0]["link"] == f"/auditor-review?request={req_id}"
    assert biz.get("/api/nav/badges").json()["requests"] == 1
    assert aud.post(f"/api/auditor/requests/{req_id}/resolve").status_code == 409  # nothing to review yet
    assert aud.post(f"/api/auditor/requests/{req_id}/remind").status_code == 204
    r = biz.post(f"/api/requests/{req_id}/respond", data={"note": "See attached"},
                 files=[("attachments", ("a.pdf", PDF, "application/pdf")), ("attachments", ("b.csv", b"a,b\n1,2\n", "text/csv"))])
    assert r.status_code == 201 and len(r.json()["attachments"]) == 2
    att_id = r.json()["attachments"][0]["id"]
    assert aud.get(f"/api/attachments/{att_id}/file").status_code == 200
    assert aud.get("/api/nav/badges").json()["requests"] == 1
    assert aud.get("/api/auditor/requests").json()[0]["response"]["note"] == "See attached"
    assert aud.post(f"/api/auditor/engagements/{eng_id}/approve").status_code == 409  # open request blocks sign-off
    assert aud.post(f"/api/auditor/requests/{req_id}/revision", json={"note": "Need VAT number on invoice"}).json()["status"] == "revision_requested"
    assert biz.get("/api/requests").json()[0]["response"]["revisionNote"] == "Need VAT number on invoice"
    assert biz.post(f"/api/requests/{req_id}/respond", data={"note": "Updated"}).status_code == 201
    assert aud.post(f"/api/auditor/requests/{req_id}/resolve").json()["status"] == "resolved"
    assert biz.get("/api/dashboard").json()["attentionItems"] == []

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

    # sign-off is blocked while a submitted document is still unverified
    assert aud.post(f"/api/auditor/engagements/{eng_id}/approve").status_code == 409
    assert aud.post(f"/api/auditor/documents/{tb['id']}/verify").json()["status"] == "verified"
    # a dismissed request must not block sign-off
    r2 = aud.post(f"/api/auditor/engagements/{eng_id}/requests", json={"title": "Optional extra", "priority": "LOW"})
    assert aud.post(f"/api/auditor/engagements/{eng_id}/approve").status_code == 409  # open request blocks
    assert aud.post(f"/api/auditor/requests/{r2.json()['id']}/dismiss").json()["status"] == "dismissed"

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


def test_cancel_resets_workspace():
    with TestClient(app) as biz, TestClient(app) as aud:
        biz.post("/api/auth/register/business", json={"email": "c-biz@x.lk", "password": "password123", "fullName": "Owner", "companyName": "Reset Co"})
        aud.post("/api/auth/register/auditor", json={"email": "c-aud@x.lk", "password": "password123", "fullName": "A", "firmName": "F"})
        biz.post("/api/engagement/invite", json={"auditorEmail": "c-aud@x.lk"})
        eng_id = aud.get("/api/auditor/engagements", params={"status": "invited"}).json()[0]["id"]
        aud.post(f"/api/auditor/engagements/{eng_id}/accept")
        aud.put(f"/api/auditor/engagements/{eng_id}/checklist", json={"items": [{"name": "TB", "category": "Trial Balance", "description": "", "required": True}]})
        biz.post("/api/documents", files={"file": ("tb.pdf", PDF, "application/pdf")})
        biz.put("/api/financials", json={"revenue": 100, "costOfSales": 10, "operatingExpenses": 10})
        biz.post("/api/handover")
        aud.post(f"/api/auditor/engagements/{eng_id}/requests", json={"title": "Q"})
        # name change via company settings
        biz.put("/api/company", json={**biz.get("/api/company").json(), "fullName": "New Owner"})
        assert biz.get("/api/auth/me").json()["user"]["fullName"] == "New Owner"

        assert biz.post("/api/engagement/cancel").status_code == 204
        assert biz.get("/api/documents").json()["documents"] == [] and biz.get("/api/documents").json()["checklist"]["items"] == []
        assert biz.get("/api/financials").json()["inputs"] is None
        assert biz.get("/api/dashboard").json()["progressPercent"] == 0 and biz.get("/api/dashboard").json()["auditorStatus"] == "none"
        assert biz.get("/api/engagement").json()["engagement"] is None and biz.get("/api/requests").json() == []
        assert aud.get("/api/auditor/engagements").json() == []
        assert [e["eventType"] for e in aud.get("/api/auditor/audit-log").json()] == []  # no engagement => no log access
        assert biz.get("/api/notifications").json()["unreadCount"] == 0
        # a new invitation starts clean
        biz.post("/api/engagement/invite", json={"auditorEmail": "c-aud@x.lk"})
        assert aud.get("/api/auditor/engagements", params={"status": "invited"}).json()[0]["progressPercent"] == 0
