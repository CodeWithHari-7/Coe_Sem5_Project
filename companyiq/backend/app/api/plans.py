"""Account Plans, Feedback, Notifications, Evaluation APIs."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.database import (
    AccountPlan, AccountPlanVersion, Feedback, FeedbackType,
    Notification, EvaluationResult, User, Company
)
from app.schemas.schemas import (
    AccountPlanCreate, AccountPlanUpdate, AccountPlanOut,
    FeedbackCreate, FeedbackOut, NotificationOut, SuccessResponse
)
from app.services.account_plan_service import generate_account_plan, update_account_plan
from app.evaluation.evaluator import Evaluator
from app.utils.logger import get_logger

logger = get_logger("plans_api")

# ─── Account Plans ──────────────────────────────────────
plans_router = APIRouter(prefix="/account-plans", tags=["Account Plans"])


@plans_router.post("", response_model=AccountPlanOut, status_code=201)
def create_plan(
    data: AccountPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")

    research_data = company.intelligence or {"data_label": "DEMO_DATA"}
    plan = generate_account_plan(
        db=db,
        company_id=data.company_id,
        user_id=current_user.id,
        research_data=research_data,
        focus=data.focus,
        research_session_id=data.research_session_id,
    )
    return plan


@plans_router.get("/{plan_id}", response_model=AccountPlanOut)
def get_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.query(AccountPlan).filter(AccountPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Account plan not found")
    return plan


@plans_router.put("/{plan_id}", response_model=AccountPlanOut)
def update_plan(
    plan_id: str,
    data: AccountPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = update_account_plan(db, plan_id, current_user.id, data.model_dump(exclude_none=True))
    return plan


@plans_router.get("/{plan_id}/versions")
def get_plan_versions(
    plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    versions = db.query(AccountPlanVersion).filter(
        AccountPlanVersion.account_plan_id == plan_id
    ).order_by(AccountPlanVersion.version.desc()).all()
    return versions


# ─── Feedback ───────────────────────────────────────────
feedback_router = APIRouter(prefix="/recommendations", tags=["Feedback"])


@feedback_router.post("/{recommendation_id}/feedback", response_model=FeedbackOut, status_code=201)
def submit_feedback(
    recommendation_id: str,
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fb_type = data.feedback_type
    if fb_type not in [t.value for t in FeedbackType]:
        raise HTTPException(400, f"Invalid feedback type. Must be one of: {[t.value for t in FeedbackType]}")

    feedback = Feedback(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        company_id=data.company_id,
        recommendation_id=recommendation_id,
        feedback_type=FeedbackType(fb_type),
        feedback_text=data.feedback_text,
        modified_content=data.modified_content,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    logger.info("feedback_stored", recommendation_id=recommendation_id, type=fb_type)
    return feedback


# ─── Notifications ──────────────────────────────────────
notif_router = APIRouter(prefix="/notifications", tags=["Notifications"])


@notif_router.get("", response_model=List[NotificationOut])
def get_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    return q.order_by(Notification.created_at.desc()).limit(50).all()


@notif_router.post("/{notif_id}/read", response_model=SuccessResponse)
def mark_read(
    notif_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    notif.is_read = True
    db.commit()
    return SuccessResponse(message="Marked as read")


# ─── Evaluation ─────────────────────────────────────────
eval_router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@eval_router.get("")
def get_evaluation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    evaluator = Evaluator()
    return evaluator.get_demo_evaluation()


# ─── Dashboard Stats ────────────────────────────────────
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.database import ResearchSession, ResearchStatus
    total_companies = db.query(Company).count()
    active_plans = db.query(AccountPlan).filter(AccountPlan.status == "active").count()
    total_plans = db.query(AccountPlan).count()
    recent_sessions = db.query(ResearchSession).order_by(
        ResearchSession.created_at.desc()
    ).limit(5).all()

    # Feedback acceptance rate
    total_fb = db.query(Feedback).count()
    accepted_fb = db.query(Feedback).filter(Feedback.feedback_type == FeedbackType.accept).count()
    acceptance_rate = round(accepted_fb / total_fb * 100, 1) if total_fb > 0 else 0

    # Average latency from messages
    from app.models.database import Message
    msgs = db.query(Message).filter(Message.latency_ms != None).limit(100).all()
    avg_latency = round(sum(m.latency_ms for m in msgs) / len(msgs), 0) if msgs else 0

    recent_companies = db.query(Company).order_by(
        Company.last_researched_at.desc().nullslast()
    ).limit(5).all()

    unread_notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    return {
        "total_companies": total_companies,
        "active_plans": active_plans,
        "total_plans": total_plans,
        "acceptance_rate": acceptance_rate,
        "avg_response_time_ms": avg_latency,
        "unread_notifications": unread_notifs,
        "recent_sessions": [
            {
                "id": s.id,
                "company_id": s.company_id,
                "status": s.status.value,
                "created_at": s.created_at.isoformat(),
            }
            for s in recent_sessions
        ],
        "recent_companies": [
            {"id": c.id, "name": c.name, "industry": c.industry, "is_demo": c.is_demo}
            for c in recent_companies
        ],
    }
