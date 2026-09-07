"""Research / Conversation API — chat interface."""
import uuid, time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.database import (
    Company, ResearchSession, ResearchStatus, Conversation, Message, User
)
from app.schemas.schemas import ConversationRequest, ConversationResponse, ResearchRequest
from app.agents.research_agent import ResearchAgent
from app.utils.logger import get_logger

router = APIRouter(prefix="/research", tags=["Research"])
logger = get_logger("research_api")
_agent = None

def get_agent() -> ResearchAgent:
    global _agent
    if _agent is None:
        _agent = ResearchAgent()
    return _agent


@router.post("/chat", response_model=ConversationResponse)
def chat(
    req: ConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Main conversational research endpoint."""
    start = time.time()
    agent = get_agent()

    # Classify intent
    intent_data = agent.classify_intent(req.message)
    intent = intent_data.get("intent", "research")
    company_name = intent_data.get("company_name") or (req.context or {}).get("company_name")

    # Get or create conversation
    conversation_id = req.conversation_id or str(uuid.uuid4())
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        # Find or create company
        company = None
        if company_name:
            company = db.query(Company).filter(Company.name.ilike(f"%{company_name}%")).first()
            if not company:
                company = Company(
                    id=str(uuid.uuid4()),
                    name=company_name,
                    is_demo=True,
                )
                db.add(company)
                db.flush()

        conversation = Conversation(
            id=conversation_id,
            company_id=company.id if company else None,
            user_id=current_user.id,
            title=f"Research: {company_name or 'General'}",
        )
        db.add(conversation)

    # Store user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="user",
        content=req.message,
        intent=intent,
    )
    db.add(user_msg)

    # Get conversation history for context
    history = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.role.in_(["user", "assistant"]),
    ).order_by(Message.created_at.desc()).limit(10).all()
    history_dicts = [{"role": m.role, "content": m.content} for m in reversed(history)]

    # Route by intent
    structured_data = None
    if intent in ("research", "opportunity", "account_plan") and company_name:
        company = db.query(Company).filter(
            Company.name.ilike(f"%{company_name}%")
        ).first()
        company_id = company.id if company else None

        result = agent.research_company(
            company_name=company_name,
            focus_area=intent_data.get("focus"),
            session_id=conversation_id,
        )
        structured_data = result
        content = _format_research_response(result, intent)
        retrieval_count = result.get("sources_count", 0)

    elif intent == "followup" and company_name:
        content = agent.answer_followup(req.message, company_name, history_dicts)
        retrieval_count = 5
    elif intent == "unsupported":
        content = "I'm specialized for company research and account planning. Please ask me to research a company, identify opportunities, or create an account plan."
        retrieval_count = 0
    else:
        content = agent.answer_followup(req.message, company_name or "", history_dicts)
        retrieval_count = 0

    latency = (time.time() - start) * 1000

    # Store assistant message
    asst_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="assistant",
        content=content,
        intent=intent,
        structured_data=structured_data,
        retrieval_count=retrieval_count,
        latency_ms=latency,
        model_used="demo" if not structured_data else "gpt-4o-mini",
    )
    db.add(asst_msg)
    db.commit()

    return ConversationResponse(
        conversation_id=conversation_id,
        message_id=asst_msg.id,
        content=content,
        intent=intent,
        structured_data=structured_data,
        retrieval_count=retrieval_count,
        latency_ms=round(latency, 1),
        model_used=asst_msg.model_used,
        insufficient_evidence=bool(structured_data and structured_data.get("insufficient_evidence")),
    )


def _format_research_response(result: dict, intent: str) -> str:
    if not result.get("success"):
        return f"Research failed: {result.get('error', 'Unknown error')}"
    if result.get("insufficient_evidence"):
        return result.get("message", "Insufficient evidence available.")
    company_name = result.get("company_name", "the company")
    opps = result.get("opportunities", [])
    opp_summary = ""
    if opps:
        scores = [f"• **{o.get('title')}** — {o.get('score_breakdown', {}).get('level', 'HIGH')} ({o.get('score_breakdown', {}).get('overall', 85):.0f}/100)" for o in opps[:3]]
        opp_summary = "\n\n**Top Opportunities Identified:**\n" + "\n".join(scores)
    return f"Research complete for **{company_name}**.\n\nI've analyzed market signals and generated structured company intelligence with {len(opps)} opportunities identified.{opp_summary}\n\nSee the structured intelligence panels for details."
