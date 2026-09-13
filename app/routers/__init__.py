from app.routers.auditor import router as auditor
from app.routers.auth import router as auth
from app.routers.business import router as business
from app.routers.discussions import router as discussions
from app.routers.documents import router as documents
from app.routers.events import router as events
from app.routers.financials import router as financials
from app.routers.requests import router as requests
from app.routers.notifications import router as notifications

ROUTERS = [auth, business, auditor, documents, financials, requests, discussions, notifications, events]
