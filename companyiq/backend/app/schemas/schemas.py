"""
CompanyIQ — Pydantic Schemas for all structured I/O.
LLM outputs are validated against these schemas before storage.
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum


# ──────────────────────────────────────────────
# Auth Schemas
# ──────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)
    role: str = "analyst"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


# ──────────────────────────────────────────────
# Company Schemas
# ──────────────────────────────────────────────

class CompanyCreate(BaseModel):
    name: str = Field(min_length=1)
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None


class CompanyOut(BaseModel):
    id: str
    name: str
    industry: Optional[str]
    size: Optional[str]
    website: Optional[str]
    description: Optional[str]
    country: Optional[str]
    founded_year: Optional[int]
    employee_count: Optional[str]
    revenue_range: Optional[str]
    products_services: Optional[List[str]]
    technologies: Optional[List[str]]
    intelligence: Optional[Dict[str, Any]]
    last_researched_at: Optional[datetime]
    is_demo: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Research Schemas
# ──────────────────────────────────────────────

class ResearchRequest(BaseModel):
    company_name: str
    focus_area: Optional[str] = None
    message: Optional[str] = None   # full conversational input


class ResearchSessionOut(BaseModel):
    id: str
    company_id: str
    status: str
    focus_area: Optional[str]
    sources_count: int
    chunks_count: int
    duration_seconds: Optional[float]
    is_demo: bool
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Evidence & Confidence (used throughout)
# ──────────────────────────────────────────────

class EvidenceItem(BaseModel):
    source_type: str
    title: str
    url: Optional[str] = None
    document_id: Optional[str] = None
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    publication_date: Optional[str] = None
    retrieved_at: Optional[str] = None


class ConfidenceScore(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    label: str                  # "HIGH" | "MEDIUM" | "LOW"
    basis: str                  # "evidence_coverage" | "model_estimate" | "insufficient"
    evidence_count: int


# ──────────────────────────────────────────────
# Company Intelligence (LLM output schema)
# ──────────────────────────────────────────────

class CompanyProfile(BaseModel):
    """Structured LLM output for company overview section."""
    name: str
    industry: str
    description: str
    business_model: str
    products_services: List[str]
    market_position: str
    employee_count: Optional[str] = None
    revenue_range: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    technologies: List[str] = []
    strategic_priorities: List[str] = []
    recent_developments: List[str] = []
    potential_challenges: List[str] = []
    business_signals: List[str] = []
    competitive_landscape: List[str] = []
    decision_maker_roles: List[str] = []
    evidence: List[EvidenceItem] = []
    confidence: Optional[ConfidenceScore] = None
    insufficient_evidence: bool = False
    data_label: str = "AI_GENERATED"   # "AI_GENERATED" | "DEMO_DATA" | "HUMAN_MODIFIED"


class ResearchFinding(BaseModel):
    """A single research finding with source attribution."""
    topic: str
    finding: str
    source_title: str
    source_url: Optional[str] = None
    source_type: str
    publication_date: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    is_conflicting: bool = False
    conflicting_sources: List[str] = []


# ──────────────────────────────────────────────
# Opportunity Schemas
# ──────────────────────────────────────────────

class OpportunityScoreBreakdown(BaseModel):
    business_relevance: float = Field(ge=0.0, le=100.0)
    recent_activity: float = Field(ge=0.0, le=100.0)
    product_fit: float = Field(ge=0.0, le=100.0)
    historical_similarity: float = Field(ge=0.0, le=100.0)
    evidence_confidence: float = Field(ge=0.0, le=100.0)
    overall: float = Field(ge=0.0, le=100.0)
    level: str   # HIGH | MEDIUM | LOW | VERY_LOW


class Opportunity(BaseModel):
    """Structured opportunity with explainability."""
    title: str
    description: str
    opportunity_type: str
    what: str          # What is the opportunity?
    why: str           # Why is it relevant?
    evidence: List[EvidenceItem]
    confidence: ConfidenceScore
    limitations: str   # Missing or uncertain information
    score_breakdown: OpportunityScoreBreakdown
    insufficient_evidence: bool = False


class OpportunityOut(BaseModel):
    id: str
    company_id: str
    title: str
    description: Optional[str]
    opportunity_type: Optional[str]
    level: Optional[str]
    overall_score: Optional[float]
    score_business_relevance: Optional[float]
    score_recent_activity: Optional[float]
    score_product_fit: Optional[float]
    score_historical_similarity: Optional[float]
    score_evidence_confidence: Optional[float]
    what: Optional[str]
    why: Optional[str]
    evidence: Optional[List[Dict]]
    confidence: Optional[float]
    limitations: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Recommendation Schemas
# ──────────────────────────────────────────────

class RecommendationOut(BaseModel):
    id: str
    opportunity_id: Optional[str]
    company_id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    action: Optional[str]
    priority: str
    confidence: Optional[float]
    evidence: Optional[List[Dict]]
    status: str
    section_status: str
    human_note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Account Plan Schemas
# ──────────────────────────────────────────────

class AccountPlanSection(BaseModel):
    id: str
    title: str
    content: str
    section_type: str   # overview | goals | challenges | opportunities | stakeholders | actions | risks | evidence | timeline
    status: str = "AI_GENERATED"  # AI_GENERATED | HUMAN_MODIFIED | HUMAN_APPROVED
    priority: str = "medium"
    confidence: Optional[float] = None
    evidence: List[EvidenceItem] = []
    human_note: Optional[str] = None
    recommendations: List[Dict[str, Any]] = []
    order: int = 0


class AccountPlan(BaseModel):
    """Full account plan structure."""
    title: str
    company_name: str
    sections: List[AccountPlanSection]
    ai_confidence: float
    version: int = 1
    generated_at: str
    data_label: str = "AI_GENERATED"


class AccountPlanCreate(BaseModel):
    company_id: str
    research_session_id: Optional[str] = None
    focus: Optional[str] = None


class AccountPlanUpdate(BaseModel):
    title: Optional[str] = None
    sections: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = None


class AccountPlanOut(BaseModel):
    id: str
    company_id: str
    title: Optional[str]
    version: int
    status: str
    sections: Optional[List[Dict[str, Any]]]
    ai_confidence: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Feedback Schema
# ──────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    recommendation_id: str
    company_id: Optional[str] = None
    feedback_type: str   # accept | reject | edit | not_relevant | needs_more_evidence
    feedback_text: Optional[str] = None
    modified_content: Optional[str] = None


class FeedbackOut(BaseModel):
    id: str
    user_id: str
    company_id: Optional[str]
    recommendation_id: Optional[str]
    feedback_type: str
    feedback_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Research Update / Change Detection
# ──────────────────────────────────────────────

class ChangeDetected(BaseModel):
    field: str
    previous_value: Any
    new_value: Any
    change_category: str
    impact: str        # high | medium | low
    description: str


class ResearchUpdate(BaseModel):
    change_category: str
    impact_level: str
    changes_detected: List[ChangeDetected]
    affected_sections: List[str]
    recommended_action: str
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]


class ResearchUpdateOut(BaseModel):
    id: str
    company_id: str
    change_category: Optional[str]
    impact_level: Optional[str]
    changes_detected: Optional[List[Dict]]
    affected_sections: Optional[List[str]]
    recommended_action: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Conversation / Chat Schemas
# ──────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str   # user | assistant
    content: str


class ConversationRequest(BaseModel):
    message: str
    company_id: Optional[str] = None
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    conversation_id: str
    message_id: str
    role: str = "assistant"
    content: str
    intent: str
    structured_data: Optional[Dict[str, Any]] = None
    retrieval_count: Optional[int] = None
    latency_ms: Optional[float] = None
    model_used: Optional[str] = None
    insufficient_evidence: bool = False


# ──────────────────────────────────────────────
# Notification Schema
# ──────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: str
    company_id: Optional[str]
    title: Optional[str]
    message: Optional[str]
    notification_type: Optional[str]
    impact_level: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Evaluation Schemas
# ──────────────────────────────────────────────

class EvaluationMetrics(BaseModel):
    system_type: str        # baseline | ai_rag
    precision: float
    recall: float
    f1_score: float
    acceptance_rate: float
    avg_response_time_ms: float
    evidence_coverage: float
    false_positive_rate: float
    false_negative_rate: float
    failure_rate: float
    user_satisfaction: Optional[float] = None
    is_synthetic: bool = True


class EvaluationReport(BaseModel):
    baseline: EvaluationMetrics
    ai_rag: EvaluationMetrics
    improvement_pct: Dict[str, float]
    notes: str
    generated_at: str


# ──────────────────────────────────────────────
# Generic API responses
# ──────────────────────────────────────────────

class SuccessResponse(BaseModel):
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
    error_type: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
