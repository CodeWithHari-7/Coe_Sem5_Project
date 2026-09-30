"""
Test Suite for Edge Cases:
- Sparse Profiles (missing/incomplete data)
- Conflicting Preferences (contradictory objectives)
- Unavailable Options / Negative Constraints (incompatible platform requests)
- Out-of-Domain Requests (non-business queries)
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models.database import Base, Company
from app.agents.research_agent import ResearchAgent

TEST_DB_URL = "sqlite:///./test_edge_cases.db"
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


def get_token():
    email = f"edge_user_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/api/auth/register", json={
        "email": email, "password": "Password@123",
        "full_name": "Edge Tester", "role": "analyst"
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": "Password@123"})
    return resp.json()["access_token"]


# ─── 1. Sparse Profiles Tests ──────────────────────────────────────────

def test_sparse_profile_handling_direct_agent():
    """Verify research agent detects unindexed / sparse accounts without hallucinating."""
    agent = ResearchAgent()
    sparse_name = f"Unknown Stealth Startup {uuid.uuid4().hex[:4]}"
    res = agent.research_company(sparse_name)

    assert res["success"] is True
    assert res.get("insufficient_evidence") is True
    profile = res.get("company_profile", {})
    confidence = profile.get("confidence", {})
    assert confidence.get("label") == "LOW"
    assert confidence.get("value", 1.0) <= 0.45
    assert "sparse" in profile.get("description", "").lower()
    assert len(res.get("opportunities", [])) >= 1
    # Check that opportunity is a discovery/upload prompt rather than hallucinated commercial deal
    opp = res["opportunities"][0]
    assert opp.get("confidence", {}).get("label") == "LOW"


def test_sparse_profile_via_api():
    """API chat with a sparse company returns insufficient_evidence flag."""
    token = get_token()
    sparse_name = f"NonExistentCo_{uuid.uuid4().hex[:5]}"
    resp = client.post("/api/research/chat", json={
        "message": f"Research {sparse_name}",
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    data = resp.json()
    assert "conversation_id" in data
    # Insufficient evidence flag should be propagated
    if data.get("structured_data"):
        assert data["structured_data"].get("insufficient_evidence") is True


# ─── 2. Conflicting Preferences Tests ──────────────────────────────────

def test_conflicting_preferences_detection():
    """Detect contradictory objectives in user query."""
    agent = ResearchAgent()
    conflict_msg = "We need to cut all R&D costs and reduce our budget by 80% immediately while doubling R&D headcount and tripling our AI investment."
    conflict = agent.detect_conflicts(conflict_msg)
    assert conflict is not None
    assert "contradictory" in conflict.lower() or "cost reduction" in conflict.lower()


def test_conflicting_preferences_intent_classifier():
    """Intent classification flags conflict detected."""
    agent = ResearchAgent()
    conflict_query = "Cut budget by 70% but expand R&D investment immediately for Tata Motors"
    classified = agent.classify_intent(conflict_query)
    assert classified.get("conflict_detected") is True
    assert classified.get("conflict_details") is not None


def test_followup_handles_conflicting_preferences():
    """Follow-up answer includes warning notice when user specifies contradictory constraints."""
    agent = ResearchAgent()
    ans = agent.answer_followup(
        question="Cut R&D budget by 60% while expanding R&D headcount by 300%",
        company_name="Tata Motors",
        conversation_history=[],
    )
    assert "Notice" in ans or "Contradictory" in ans or "conflict" in ans.lower()


# ─── 3. Unavailable Options Tests ──────────────────────────────────────

def test_unavailable_options_detection():
    """Detect request for incompatible technology (e.g. diesel engines on pure EV)."""
    agent = ResearchAgent()
    unavail = agent.detect_unavailable_options("Ola Electric", "Propose diesel combustion engine options")
    assert unavail is not None
    assert "unavailable" in unavail.lower()
    assert "electric mobility" in unavail.lower() or "combustion" in unavail.lower()


def test_followup_rejects_unavailable_option():
    """Follow-up answer clearly explains option incompatibility."""
    agent = ResearchAgent()
    ans = agent.answer_followup(
        question="Can we supply petrol combustion engines for their new scooter?",
        company_name="Ola Electric",
        conversation_history=[],
    )
    assert "Constraint Incompatibility" in ans or "Unavailable" in ans


# ─── 4. Out-of-Domain Requests Tests ───────────────────────────────────

def test_out_of_domain_queries():
    """Test various non-business out-of-domain requests are classified as unsupported."""
    agent = ResearchAgent()

    queries = [
        "What is the weather forecast in Paris tomorrow?",
        "Can you write a poem about autumn leaves?",
        "How to bake a chocolate cake at home?",
        "Who won the 2024 football tournament?",
        "What is the capital of France?",
    ]

    for q in queries:
        classified = agent.classify_intent(q)
        assert classified.get("intent") == "unsupported", f"Expected unsupported for: {q}"


def test_out_of_domain_chat_response():
    """API endpoint returns polite business-domain boundary message for out-of-domain query."""
    token = get_token()
    resp = client.post("/api/research/chat", json={
        "message": "What is the weather in London right now?",
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "unsupported"
    assert "research" in data["content"].lower() or "specialized" in data["content"].lower()
