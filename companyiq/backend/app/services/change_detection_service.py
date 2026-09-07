"""
Change Detection Service — compares new research to previous research.
Categorizes changes and generates notifications.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.database import ResearchUpdate, Notification, ChangeCategory
from app.utils.logger import get_logger

logger = get_logger("change_detection")

IMPACT_KEYWORDS = {
    "high": ["major", "significant", "critical", "breakthrough", "launch", "investment", "acquisition"],
    "medium": ["expand", "partner", "announce", "plan", "increase", "improve"],
    "low": ["minor", "update", "adjust", "review"],
}


def detect_changes(
    db: Session,
    company_id: str,
    previous_data: Dict[str, Any],
    new_data: Dict[str, Any],
    previous_session_id: Optional[str],
    new_session_id: Optional[str],
    user_id: Optional[str] = None,
) -> ResearchUpdate:
    """Compare two research snapshots and store detected changes."""

    changes = []
    prev_profile = previous_data.get("company_profile", {})
    new_profile = new_data.get("company_profile", {})

    # Compare key fields
    fields_to_compare = [
        ("strategic_priorities", "Strategic Priorities"),
        ("recent_developments", "Recent Developments"),
        ("potential_challenges", "Potential Challenges"),
        ("business_signals", "Business Signals"),
        ("technologies", "Technologies"),
    ]

    for field, label in fields_to_compare:
        prev_val = prev_profile.get(field) or []
        new_val = new_profile.get(field) or []
        change = _compare_list_field(field, label, prev_val, new_val)
        if change:
            changes.append(change)

    # Compare opportunities
    prev_opps = {o.get("title"): o for o in (previous_data.get("opportunities") or [])}
    new_opps = {o.get("title"): o for o in (new_data.get("opportunities") or [])}

    for title in new_opps:
        if title not in prev_opps:
            changes.append({
                "field": "opportunities",
                "previous_value": None,
                "new_value": title,
                "change_category": ChangeCategory.new_information.value,
                "impact": "high",
                "description": f"New opportunity detected: {title}",
            })
        else:
            prev_score = (prev_opps[title].get("score_breakdown") or {}).get("overall", 0)
            new_score = (new_opps[title].get("score_breakdown") or {}).get("overall", 0)
            if abs(new_score - prev_score) > 5:
                changes.append({
                    "field": f"opportunity_score:{title}",
                    "previous_value": prev_score,
                    "new_value": new_score,
                    "change_category": ChangeCategory.updated_information.value,
                    "impact": "medium" if abs(new_score - prev_score) < 15 else "high",
                    "description": f"Opportunity '{title}' score changed: {prev_score:.0f} → {new_score:.0f}",
                })

    # Determine overall category and impact
    if not changes:
        category = ChangeCategory.no_significant_change
        impact = "low"
    elif any(c["change_category"] == ChangeCategory.conflicting_information.value for c in changes):
        category = ChangeCategory.conflicting_information
        impact = "high"
    elif any(c["change_category"] == ChangeCategory.new_information.value for c in changes):
        category = ChangeCategory.new_information
        impact = max((c["impact"] for c in changes), key=lambda x: {"high": 2, "medium": 1, "low": 0}.get(x, 0))
    else:
        category = ChangeCategory.updated_information
        impact = "medium"

    affected_sections = list({
        _get_affected_section(c["field"]) for c in changes
    })

    recommended_action = _build_recommendation(changes, impact)

    update = ResearchUpdate(
        id=str(uuid.uuid4()),
        company_id=company_id,
        previous_session_id=previous_session_id,
        new_session_id=new_session_id,
        change_category=category,
        impact_level=impact,
        previous_state=prev_profile,
        new_state=new_profile,
        changes_detected=changes,
        affected_sections=affected_sections,
        recommended_action=recommended_action,
    )
    db.add(update)

    # Create notification if significant
    if category != ChangeCategory.no_significant_change:
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            company_id=company_id,
            research_update_id=update.id,
            title=f"Research Update: {category.value.replace('_', ' ').title()}",
            message=f"{len(changes)} change(s) detected. Impact: {impact.upper()}. {recommended_action}",
            notification_type="change_detected",
            impact_level=impact,
            is_read=False,
        )
        db.add(notif)

    db.commit()
    db.refresh(update)

    logger.info(
        "change_detection_complete",
        company_id=company_id,
        category=category.value,
        impact=impact,
        changes_count=len(changes),
    )
    return update


def _compare_list_field(field: str, label: str, prev: List, new: List) -> Optional[Dict]:
    prev_set = set(str(x) for x in prev)
    new_set = set(str(x) for x in new)
    added = new_set - prev_set
    removed = prev_set - new_set

    if not added and not removed:
        return None

    if added and removed:
        category = ChangeCategory.conflicting_information.value
        desc = f"{label}: {len(added)} items added, {len(removed)} removed"
        impact = "high"
    elif added:
        category = ChangeCategory.new_information.value
        desc = f"{label}: {len(added)} new items detected"
        impact = "medium"
    else:
        category = ChangeCategory.updated_information.value
        desc = f"{label}: {len(removed)} items no longer referenced"
        impact = "low"

    return {
        "field": field,
        "previous_value": list(prev_set),
        "new_value": list(new_set),
        "change_category": category,
        "impact": impact,
        "description": desc,
    }


def _get_affected_section(field: str) -> str:
    mapping = {
        "strategic_priorities": "Business Goals",
        "recent_developments": "Recent Developments",
        "potential_challenges": "Current Challenges",
        "business_signals": "Business Signals",
        "technologies": "Technology Focus",
        "opportunities": "Opportunity Analysis",
    }
    for key, section in mapping.items():
        if key in field:
            return section
    return "Company Overview"


def _build_recommendation(changes: List[Dict], impact: str) -> str:
    if not changes:
        return "No action required — no significant changes detected."
    high_impact = [c for c in changes if c.get("impact") == "high"]
    if high_impact:
        return f"URGENT: {high_impact[0]['description']}. Review and update account plan immediately."
    return f"{len(changes)} updates detected. Review account plan sections: " + ", ".join(
        set(_get_affected_section(c["field"]) for c in changes)
    )
