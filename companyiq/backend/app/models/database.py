"""
CompanyIQ — SQLAlchemy Database Models
All tables with proper foreign keys, timestamps, and indexes.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean,
    DateTime, ForeignKey, JSON, Enum as SAEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


def gen_uuid():
    return str(uuid.uuid4())


def now():
    return datetime.utcnow()


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    analyst = "analyst"


class SourceType(str, enum.Enum):
    website = "website"
    news = "news"
    pdf = "pdf"
    csv = "csv"
    excel = "excel"
    txt = "txt"
    knowledge_base = "knowledge_base"
    manual = "manual"


class DocumentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class ResearchStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class OpportunityLevel(str, enum.Enum):
    high = "HIGH"
    medium = "MEDIUM"
    low = "LOW"
    very_low = "VERY_LOW"


class FeedbackType(str, enum.Enum):
    accept = "accept"
    reject = "reject"
    edit = "edit"
    not_relevant = "not_relevant"
    needs_more_evidence = "needs_more_evidence"


class ChangeCategory(str, enum.Enum):
    new_information = "NEW_INFORMATION"
    updated_information = "UPDATED_INFORMATION"
    conflicting_information = "CONFLICTING_INFORMATION"
    stale_information = "STALE_INFORMATION"
    no_significant_change = "NO_SIGNIFICANT_CHANGE"


class PlanSectionStatus(str, enum.Enum):
    ai_generated = "AI_GENERATED"
    human_modified = "HUMAN_MODIFIED"
    human_approved = "HUMAN_APPROVED"


class AuditAction(str, enum.Enum):
    create = "create"
    read = "read"
    update = "update"
    delete = "delete"
    login = "login"
    logout = "logout"
    export = "export"


# ──────────────────────────────────────────────
# Tables
# ──────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.analyst, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    # Relationships
    research_sessions = relationship("ResearchSession", back_populates="user")
    account_plans = relationship("AccountPlan", back_populates="created_by_user")
    feedback = relationship("Feedback", back_populates="user")


class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    size = Column(String(50))          # SMB | Enterprise | Startup
    website = Column(String(500))
    description = Column(Text)
    country = Column(String(100))
    founded_year = Column(Integer)
    employee_count = Column(String(50))
    revenue_range = Column(String(100))
    products_services = Column(JSON)   # list of strings
    technologies = Column(JSON)        # list of strings
    strategic_priorities = Column(JSON)
    recent_events = Column(JSON)
    intelligence = Column(JSON)        # cached company intelligence blob
    last_researched_at = Column(DateTime)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    # Relationships
    sources = relationship("CompanySource", back_populates="company")
    documents = relationship("Document", back_populates="company")
    research_sessions = relationship("ResearchSession", back_populates="company")
    opportunities = relationship("Opportunity", back_populates="company")
    account_plans = relationship("AccountPlan", back_populates="company")
    research_updates = relationship("ResearchUpdate", back_populates="company")
    notifications = relationship("Notification", back_populates="company")

    __table_args__ = (
        Index("idx_companies_name", "name"),
        Index("idx_companies_industry", "industry"),
    )


class CompanySource(Base):
    __tablename__ = "company_sources"

    id = Column(String, primary_key=True, default=gen_uuid)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(SAEnum(SourceType), nullable=False)
    title = Column(String(500))
    url = Column(String(2000))
    document_identifier = Column(String(500))
    publication_date = Column(DateTime)
    retrieved_at = Column(DateTime, default=now)
    relevance_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

    company = relationship("Company", back_populates="sources")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_uuid)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"))
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000))
    source_type = Column(SAEnum(SourceType), nullable=False)
    status = Column(SAEnum(DocumentStatus), default=DocumentStatus.pending)
    title = Column(String(500))
    url = Column(String(2000))
    extracted_text = Column(Text)
    page_count = Column(Integer)
    word_count = Column(Integer)
    language = Column(String(20), default="en")
    meta_data = Column("metadata", JSON)
    error_message = Column(Text)
    uploaded_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    company = relationship("Company", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=gen_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"))
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer)
    topic = Column(String(100))
    vector_id = Column(String(500))    # ID in ChromaDB
    meta_data = Column("metadata", JSON)
    created_at = Column(DateTime, default=now)

    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunks_company", "company_id"),
        Index("idx_chunks_document", "document_id"),
    )


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, default=gen_uuid)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(ResearchStatus), default=ResearchStatus.pending)
    focus_area = Column(String(500))   # e.g., "EV battery technology"
    sources_count = Column(Integer, default=0)
    chunks_count = Column(Integer, default=0)
    duration_seconds = Column(Float)
    error_message = Column(Text)
    research_result = Column(JSON)     # full intelligence blob
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)
    completed_at = Column(DateTime)

    company = relationship("Company", back_populates="research_sessions")
    user = relationship("User", back_populates="research_sessions")
    conversations = relationship("Conversation", back_populates="research_session")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_uuid)
    research_session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"))
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"))
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String(500))
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    research_session = relationship("ResearchSession", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=gen_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)   # user | assistant | system
    content = Column(Text, nullable=False)
    intent = Column(String(100))                 # research | opportunity | account_plan | followup | unsupported
    structured_data = Column(JSON)               # parsed structured response
    retrieval_count = Column(Integer)
    latency_ms = Column(Float)
    model_used = Column(String(100))
    created_at = Column(DateTime, default=now)

    conversation = relationship("Conversation", back_populates="messages")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(String, primary_key=True, default=gen_uuid)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    research_session_id = Column(String, ForeignKey("research_sessions.id"))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    opportunity_type = Column(String(100))       # product_fit | expansion | partnership | risk
    level = Column(SAEnum(OpportunityLevel))
    overall_score = Column(Float)
    score_business_relevance = Column(Float)
    score_recent_activity = Column(Float)
    score_product_fit = Column(Float)
    score_historical_similarity = Column(Float)
    score_evidence_confidence = Column(Float)
    what = Column(Text)
    why = Column(Text)
    evidence = Column(JSON)                      # list of {source, title, url, snippet}
    confidence = Column(Float)
    limitations = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    company = relationship("Company", back_populates="opportunities")
    recommendations = relationship("Recommendation", back_populates="opportunity")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, default=gen_uuid)
    opportunity_id = Column(String, ForeignKey("opportunities.id", ondelete="CASCADE"))
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"))
    account_plan_id = Column(String, ForeignKey("account_plans.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500))
    description = Column(Text)
    action = Column(Text)
    priority = Column(String(20), default="medium")  # high | medium | low
    confidence = Column(Float)
    evidence = Column(JSON)
    status = Column(String(50), default="pending")   # pending | accepted | rejected | modified | overridden
    section_status = Column(SAEnum(PlanSectionStatus), default=PlanSectionStatus.ai_generated)
    human_note = Column(Text)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    opportunity = relationship("Opportunity", back_populates="recommendations")
    feedback_items = relationship("Feedback", back_populates="recommendation")


class AccountPlan(Base):
    __tablename__ = "account_plans"

    id = Column(String, primary_key=True, default=gen_uuid)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"))
    title = Column(String(500))
    version = Column(Integer, default=1)
    status = Column(String(50), default="draft")     # draft | active | archived
    sections = Column(JSON)                           # list of AccountPlanSection dicts
    ai_confidence = Column(Float)
    research_session_id = Column(String, ForeignKey("research_sessions.id"))
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    company = relationship("Company", back_populates="account_plans")
    created_by_user = relationship("User", back_populates="account_plans")
    versions = relationship("AccountPlanVersion", back_populates="account_plan")


class AccountPlanVersion(Base):
    __tablename__ = "account_plan_versions"

    id = Column(String, primary_key=True, default=gen_uuid)
    account_plan_id = Column(String, ForeignKey("account_plans.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    sections = Column(JSON)
    change_summary = Column(Text)
    changed_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=now)

    account_plan = relationship("AccountPlan", back_populates="versions")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"))
    recommendation_id = Column(String, ForeignKey("recommendations.id", ondelete="CASCADE"))
    feedback_type = Column(SAEnum(FeedbackType), nullable=False)
    feedback_text = Column(Text)
    original_content = Column(Text)
    modified_content = Column(Text)
    created_at = Column(DateTime, default=now)

    user = relationship("User", back_populates="feedback")
    recommendation = relationship("Recommendation", back_populates="feedback_items")


class ResearchUpdate(Base):
    __tablename__ = "research_updates"

    id = Column(String, primary_key=True, default=gen_uuid)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    previous_session_id = Column(String, ForeignKey("research_sessions.id"))
    new_session_id = Column(String, ForeignKey("research_sessions.id"))
    change_category = Column(SAEnum(ChangeCategory))
    impact_level = Column(String(20))    # high | medium | low
    previous_state = Column(JSON)
    new_state = Column(JSON)
    changes_detected = Column(JSON)      # list of change objects
    affected_sections = Column(JSON)
    recommended_action = Column(Text)
    created_at = Column(DateTime, default=now)

    company = relationship("Company", back_populates="research_updates")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"))
    research_update_id = Column(String, ForeignKey("research_updates.id"))
    title = Column(String(500))
    message = Column(Text)
    notification_type = Column(String(100))  # change_detected | research_complete | plan_update
    impact_level = Column(String(20))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)

    company = relationship("Company", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    action = Column(SAEnum(AuditAction), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(500))
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)

    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_created", "created_at"),
    )


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    evaluation_name = Column(String(200))
    system_type = Column(String(50))     # baseline | ai_rag
    company_id = Column(String, ForeignKey("companies.id"))
    research_session_id = Column(String, ForeignKey("research_sessions.id"))
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    acceptance_rate = Column(Float)
    response_time_ms = Column(Float)
    evidence_coverage = Column(Float)
    false_positive_rate = Column(Float)
    false_negative_rate = Column(Float)
    failure_rate = Column(Float)
    user_satisfaction = Column(Float)
    notes = Column(Text)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)
