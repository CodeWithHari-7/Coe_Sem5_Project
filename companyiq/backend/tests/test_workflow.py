"""
End-to-End Workflow Integration Test:
Tests: Upload Document → Text Extraction & Chunking → ChromaDB Indexing →
       RAG Retrieval → Opportunity Scoring with Chunk IDs → Account Plan Generation
       with Evidence Provenance → Human Feedback → Live Evaluation Benchmark.
"""
import pytest
import uuid
from io import BytesIO
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models.database import Base

TEST_DB_URL = "sqlite:///./test_workflow.db"
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
    email = f"workflow_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/api/auth/register", json={
        "email": email, "password": "Workflow@1234",
        "full_name": "Workflow Tester", "role": "analyst"
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": "Workflow@1234"})
    return resp.json()["access_token"]


def test_full_recommendation_and_evaluation_workflow():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a Target Company
    comp_name = f"Solaris Energy Systems {uuid.uuid4().hex[:4]}"
    comp_resp = client.post("/api/companies", json={
        "name": comp_name,
        "industry": "Renewable Energy / Smart Grid",
        "size": "Enterprise",
    }, headers=headers)
    assert comp_resp.status_code == 201
    company_id = comp_resp.json()["id"]

    # 2. Upload and Ingest a Source Document (Raw text / Report)
    report_text = (
        f"{comp_name} Annual Operational Review (2024-2025):\n\n"
        f"{comp_name} is scaling commercial utility-scale solar installations across Southern India. "
        "The company currently manages 3.2 GW of solar assets with 450 decentralized inverter substations. "
        "A critical strategic priority in FY25 is deploying AI-driven predictive maintenance for solar inverters "
        "and battery storage units. Thermal degradation and dust fouling currently contribute to an estimated "
        "4.8% energy yield loss, representing $12M in annual uncaptured revenue.\n\n"
        "Key Investment Initiatives:\n"
        "1. Inverter IoT Telemetry & Thermal Fault Prediction: Real-time sensor stream analytics to prevent catastrophic failures.\n"
        "2. Automated Drone Cleaning Scheduling: Optimizing cleaning cycles to maximize power generation during peak solar irradiance.\n"
        "3. Grid Dispatch Frequency Regulation: Partnering with regional load dispatch centers to stabilize renewable feed-in tariffs."
    )

    doc_resp = client.post("/api/documents/text", json={
        "company_id": company_id,
        "title": f"{comp_name} Strategic Review 2024",
        "text": report_text,
        "source_type": "annual_report",
    }, headers=headers)

    assert doc_resp.status_code == 201
    doc_data = doc_resp.json()
    doc_id = doc_data["id"]
    assert doc_data["status"] in ("ready", "indexed")
    assert doc_data["chunks_count"] >= 1

    # 3. Verify Document Chunks in DB and Vector Store
    chunks_resp = client.get(f"/api/documents/{doc_id}/chunks", headers=headers)
    assert chunks_resp.status_code == 200
    chunks = chunks_resp.json()
    assert len(chunks) >= 1
    first_chunk = chunks[0]
    assert "inverter" in first_chunk["chunk_text"].lower()
    assert first_chunk["vector_id"] is not None

    # 4. Trigger Research Agent to retrieve, score, and cite the ingested chunk
    research_resp = client.post("/api/research/chat", json={
        "message": f"Research {comp_name} and identify predictive maintenance opportunities",
    }, headers=headers)
    assert research_resp.status_code == 200
    chat_data = research_resp.json()
    assert chat_data["conversation_id"] is not None

    # Structured opportunities must exist and contain verifiable evidence citations
    structured = chat_data.get("structured_data")
    assert structured is not None
    assert structured["success"] is True
    opps = structured.get("opportunities", [])
    assert len(opps) >= 1

    # Verify Chunk ID is present in opportunity evidence
    found_chunk_citation = False
    for opp in opps:
        for ev in opp.get("evidence", []):
            if ev.get("chunk_id"):
                found_chunk_citation = True
                break
    assert found_chunk_citation is True, "Expected at least one evidence item to contain a chunk_id citation"

    # 5. Generate Account Plan from grounded research
    plan_resp = client.post("/api/account-plans", json={
        "company_id": company_id,
        "focus": "Predictive maintenance and energy optimization",
    }, headers=headers)
    assert plan_resp.status_code == 201
    plan = plan_resp.json()
    assert plan["company_id"] == company_id
    assert plan["version"] == 1
    assert len(plan["sections"]) >= 5

    # Check that sections contain confidence scores and citation references
    opp_sec = next((s for s in plan["sections"] if s["section_type"] == "opportunities"), None)
    assert opp_sec is not None
    assert "Score:" in opp_sec["content"] or "Chunk" in opp_sec["content"]

    # 6. Human-in-the-Loop Feedback: Approve/Update section
    plan_id = plan["id"]
    updated_sec = plan["sections"]
    updated_sec[0]["status"] = "HUMAN_APPROVED"
    updated_sec[0]["human_note"] = "Approved by Lead Account Executive after review"

    put_resp = client.put(f"/api/account-plans/{plan_id}", json={
        "sections": updated_sec,
    }, headers=headers)
    assert put_resp.status_code == 200
    assert put_resp.json()["version"] == 2

    # 7. Submit Feedback on Recommendation
    rec_id = opps[0].get("id", str(uuid.uuid4()))
    fb_resp = client.post(f"/api/recommendations/{rec_id}/feedback", json={
        "recommendation_id": rec_id,
        "company_id": company_id,
        "feedback_type": "accept",
        "feedback_text": "Highly relevant opportunity based on solar inverter annual review",
    }, headers=headers)
    assert fb_resp.status_code == 201

    # 8. Run Live Evaluation Benchmark and verify verified results
    eval_resp = client.post("/api/evaluation/run", headers=headers)
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["is_synthetic"] is False
    assert eval_data["ai_rag"]["f1_score"] >= 0.70
    assert eval_data["improvement"]["f1_score"] > 20.0
