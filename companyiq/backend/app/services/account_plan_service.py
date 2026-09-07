"""
Account Plan Service — generate, version, and export account plans.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.database import AccountPlan, AccountPlanVersion, Company, ResearchSession
from app.agents.llm_provider import get_llm_provider
from app.agents.demo_data import DEMO_COMPANY_INTELLIGENCE
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("account_plan_service")


def generate_account_plan(
    db: Session,
    company_id: str,
    user_id: str,
    research_data: Dict[str, Any],
    focus: Optional[str] = None,
    research_session_id: Optional[str] = None,
) -> AccountPlan:
    """Generate an account plan from research data and persist it."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"Company {company_id} not found")

    # Use demo data sections if demo mode
    if research_data.get("data_label") == "DEMO_DATA":
        sections = DEMO_COMPANY_INTELLIGENCE["account_plan"]["sections"]
        ai_confidence = DEMO_COMPANY_INTELLIGENCE["account_plan"]["ai_confidence"]
    else:
        sections = _build_sections_from_research(research_data)
        ai_confidence = _compute_overall_confidence(research_data)

    plan = AccountPlan(
        id=str(uuid.uuid4()),
        company_id=company_id,
        created_by=user_id,
        title=f"{company.name} — Account Plan",
        version=1,
        status="draft",
        sections=sections,
        ai_confidence=ai_confidence,
        research_session_id=research_session_id,
    )
    db.add(plan)

    # Save initial version
    version = AccountPlanVersion(
        id=str(uuid.uuid4()),
        account_plan_id=plan.id,
        version=1,
        sections=sections,
        change_summary="Initial AI-generated plan",
        changed_by=user_id,
    )
    db.add(version)
    db.commit()
    db.refresh(plan)

    logger.info("account_plan_created", plan_id=plan.id, company_id=company_id)
    return plan


def update_account_plan(
    db: Session,
    plan_id: str,
    user_id: str,
    updates: Dict[str, Any],
) -> AccountPlan:
    """Update an account plan and save a new version."""
    plan = db.query(AccountPlan).filter(AccountPlan.id == plan_id).first()
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")

    old_sections = plan.sections
    if "sections" in updates:
        plan.sections = updates["sections"]
    if "title" in updates:
        plan.title = updates["title"]
    if "status" in updates:
        plan.status = updates["status"]

    plan.version += 1

    version = AccountPlanVersion(
        id=str(uuid.uuid4()),
        account_plan_id=plan.id,
        version=plan.version,
        sections=plan.sections,
        change_summary=updates.get("change_summary", "Human modification"),
        changed_by=user_id,
    )
    db.add(version)
    db.commit()
    db.refresh(plan)

    logger.info("account_plan_updated", plan_id=plan_id, version=plan.version, user_id=user_id)
    return plan


def _build_sections_from_research(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert research data into account plan sections."""
    profile = data.get("company_profile", {})
    opportunities = data.get("opportunities", [])

    def sec(id, title, stype, content, order, confidence=None):
        return {
            "id": id, "title": title, "section_type": stype,
            "status": "AI_GENERATED", "priority": "medium",
            "order": order, "content": content,
            "confidence": confidence, "evidence": [],
            "human_note": None, "recommendations": [],
        }

    sections = [
        sec("s1", "Company Overview", "overview",
            f"{profile.get('name', 'Company')}: {profile.get('description', 'No description available.')}",
            1, profile.get("confidence", {}).get("value")),
        sec("s2", "Business Goals", "goals",
            "\n".join(f"• {p}" for p in profile.get("strategic_priorities", ["No priorities identified."])),
            2),
        sec("s3", "Current Challenges", "challenges",
            "\n".join(f"• {c}" for c in profile.get("potential_challenges", ["No challenges identified."])),
            3),
        sec("s4", "Business Opportunities", "opportunities",
            _format_opportunities(opportunities), 4),
        sec("s5", "Key Stakeholders", "stakeholders",
            "\n".join(f"• {r}" for r in profile.get("decision_maker_roles", ["Roles not identified."])),
            5),
        sec("s6", "Recommended Next Actions", "actions",
            "• Schedule discovery call\n• Prepare product demo\n• Develop ROI analysis", 6),
        sec("s7", "Risks", "risks",
            "\n".join(f"• {c}" for c in profile.get("potential_challenges", [][:3])), 7),
    ]
    return sections


def _format_opportunities(opps: List[Dict]) -> str:
    if not opps:
        return "No opportunities identified."
    lines = []
    for o in opps[:3]:
        score = o.get("score_breakdown", {}).get("overall", 0)
        level = o.get("score_breakdown", {}).get("level", "")
        lines.append(f"• {o.get('title', 'Opportunity')} — Score: {score:.0f}/100 ({level})")
        lines.append(f"  {o.get('description', '')}")
    return "\n".join(lines)


def _compute_overall_confidence(data: Dict[str, Any]) -> float:
    conf = data.get("company_profile", {}).get("confidence", {}).get("value", 0.5)
    return round(conf, 2)
