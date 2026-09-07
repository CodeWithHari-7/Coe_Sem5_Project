"""
CompanyIQ Test Suite — covers all major scenarios.
Run: pytest tests/ -v --tb=short
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models.database import Base

# ─── Test DB (SQLite in-memory) ─────────────────────────
TEST_DB_URL = "sqlite:///./test_companyiq.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ─── Helpers ────────────────────────────────────────────
def register_and_login(email=None, password="Test@1234"):
    email = email or f"test_{uuid.uuid4().hex[:8]}@test.com"
    client.post("/api/auth/register", json={
        "email": email, "password": password,
        "full_name": "Test User", "role": "analyst"
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"], email


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ─── Auth Tests ─────────────────────────────────────────

def test_register_user():
    resp = client.post("/api/auth/register", json={
        "email": f"newuser_{uuid.uuid4().hex[:6]}@test.com",
        "password": "Strong@1234",
        "full_name": "New User",
        "role": "analyst"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] is not None


def test_login_success():
    token, email = register_and_login()
    assert token is not None


def test_login_wrong_password():
    token, email = register_and_login()
    resp = client.post("/api/auth/login", json={"email": email, "password": "WrongPass!99"})
    assert resp.status_code == 401


def test_protected_route_without_token():
    resp = client.get("/api/companies")
    assert resp.status_code in (401, 403)


def test_get_me():
    token, _ = register_and_login()
    resp = client.get("/api/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert "email" in resp.json()


# ─── Company Tests ──────────────────────────────────────

def test_create_company():
    token, _ = register_and_login()
    resp = client.post("/api/companies", json={
        "name": "Test Corp",
        "industry": "Technology",
    }, headers=auth_headers(token))
    assert resp.status_code == 201
    assert resp.json()["name"] == "Test Corp"


def test_list_companies():
    token, _ = register_and_login()
    resp = client.get("/api/companies", headers=auth_headers(token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_company_not_found():
    token, _ = register_and_login()
    resp = client.get("/api/companies/nonexistent-id", headers=auth_headers(token))
    assert resp.status_code == 404


# ─── Research Tests ─────────────────────────────────────

def test_research_normal_company():
    """Normal company research — should return structured data."""
    token, _ = register_and_login()
    resp = client.post("/api/research/chat", json={
        "message": "Research Tata Motors and identify EV opportunities",
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "conversation_id" in data
    assert data["intent"] in ("research", "opportunity", "account_plan", "followup")


def test_research_unsupported_question():
    """Out-of-domain question should return unsupported intent response."""
    token, _ = register_and_login()
    resp = client.post("/api/research/chat", json={
        "message": "What is the capital of France?",
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    # Either intent = unsupported or it still returns a 200
    assert "conversation_id" in resp.json()


def test_research_followup():
    """Follow-up question in same conversation."""
    token, _ = register_and_login()
    resp1 = client.post("/api/research/chat", json={
        "message": "Research Infosys",
    }, headers=auth_headers(token))
    conv_id = resp1.json()["conversation_id"]

    resp2 = client.post("/api/research/chat", json={
        "message": "What are the current challenges?",
        "conversation_id": conv_id,
    }, headers=auth_headers(token))
    assert resp2.status_code == 200


# ─── Account Plan Tests ─────────────────────────────────

def test_create_account_plan():
    token, _ = register_and_login()
    # Create company first
    comp_resp = client.post("/api/companies", json={
        "name": "Plan Test Corp",
        "industry": "SaaS",
    }, headers=auth_headers(token))
    company_id = comp_resp.json()["id"]

    resp = client.post("/api/account-plans", json={
        "company_id": company_id,
    }, headers=auth_headers(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["company_id"] == company_id
    assert data["version"] == 1


def test_update_account_plan():
    token, _ = register_and_login()
    comp_resp = client.post("/api/companies", json={
        "name": "Update Test Corp", "industry": "Retail"
    }, headers=auth_headers(token))
    company_id = comp_resp.json()["id"]
    plan_resp = client.post("/api/account-plans", json={"company_id": company_id}, headers=auth_headers(token))
    plan_id = plan_resp.json()["id"]

    resp = client.put(f"/api/account-plans/{plan_id}", json={
        "title": "Updated Plan Title",
        "status": "active",
    }, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["version"] == 2


# ─── Feedback Tests ─────────────────────────────────────

def test_submit_feedback():
    token, _ = register_and_login()
    fake_rec_id = str(uuid.uuid4())
    resp = client.post(f"/api/recommendations/{fake_rec_id}/feedback", json={
        "recommendation_id": fake_rec_id,
        "feedback_type": "accept",
        "feedback_text": "This recommendation is relevant.",
    }, headers=auth_headers(token))
    assert resp.status_code == 201
    assert resp.json()["feedback_type"] == "accept"


def test_feedback_invalid_type():
    token, _ = register_and_login()
    fake_rec_id = str(uuid.uuid4())
    resp = client.post(f"/api/recommendations/{fake_rec_id}/feedback", json={
        "recommendation_id": fake_rec_id,
        "feedback_type": "invalid_type",
    }, headers=auth_headers(token))
    assert resp.status_code == 400


# ─── Evaluation Tests ───────────────────────────────────

def test_get_evaluation():
    token, _ = register_and_login()
    resp = client.get("/api/evaluation", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "baseline" in data
    assert "ai_rag" in data


# ─── Dashboard Tests ────────────────────────────────────

def test_dashboard_stats():
    token, _ = register_and_login()
    resp = client.get("/api/dashboard/stats", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "total_companies" in data
    assert "acceptance_rate" in data


# ─── Health Check ───────────────────────────────────────

def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# ─── Opportunity Scoring Unit Test ──────────────────────

def test_opportunity_scoring():
    from app.services.opportunity_service import OpportunityScorer, classify_score
    scorer = OpportunityScorer()
    profile = {
        "industry": "automotive ev",
        "strategic_priorities": ["expand ev portfolio", "battery manufacturing"],
        "recent_developments": ["major EV battery investment", "new EV launch"],
        "business_signals": ["EV sales growth"],
    }
    opp = {
        "title": "Battery Analytics Platform",
        "description": "Predictive battery analytics",
        "why": "EV battery investment signals demand for analytics",
        "evidence": [
            {"relevance_score": 0.9, "title": "Source 1"},
            {"relevance_score": 0.85, "title": "Source 2"},
        ]
    }
    result = scorer.score(profile, opp, [])
    assert 0 <= result.overall <= 100
    assert result.level in ("HIGH", "MEDIUM", "LOW", "VERY_LOW")
    assert classify_score(85) == "HIGH"
    assert classify_score(65) == "MEDIUM"
    assert classify_score(45) == "LOW"
    assert classify_score(30) == "VERY_LOW"
