"""Companies API — CRUD + research trigger."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.database import Company, ResearchSession, ResearchStatus, User, AuditLog, AuditAction
from app.schemas.schemas import CompanyCreate, CompanyOut, ResearchSessionOut, SuccessResponse
from app.agents.research_agent import ResearchAgent
from app.agents.demo_data import DEMO_COMPANIES
from app.services.account_plan_service import generate_account_plan
from app.utils.logger import get_logger
import time

router = APIRouter(prefix="/companies", tags=["Companies"])
logger = get_logger("companies_api")
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = ResearchAgent()
    return _agent


@router.get("", response_model=List[CompanyOut])
def list_companies(
    search: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Company)
    if search:
        q = q.filter(Company.name.ilike(f"%{search}%"))
    if industry:
        q = q.filter(Company.industry.ilike(f"%{industry}%"))
    total = q.count()
    companies = q.offset((page - 1) * page_size).limit(page_size).all()
    return companies


@router.post("", response_model=CompanyOut, status_code=201)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = Company(id=str(uuid.uuid4()), **data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    _audit(db, current_user.id, AuditAction.create, "company", company.id)
    logger.info("company_created", company_id=company.id, name=company.name)
    return company


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")
    return company


@router.get("/{company_id}/research", response_model=List[ResearchSessionOut])
def get_company_research(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = db.query(ResearchSession).filter(
        ResearchSession.company_id == company_id
    ).order_by(ResearchSession.created_at.desc()).limit(20).all()
    return sessions


@router.post("/{company_id}/refresh", response_model=ResearchSessionOut)
def refresh_company_research(
    company_id: str,
    focus_area: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
):
    """Re-run research for a company and detect changes."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(404, "Company not found")

    session = ResearchSession(
        id=str(uuid.uuid4()),
        company_id=company_id,
        user_id=current_user.id,
        status=ResearchStatus.running,
        focus_area=focus_area,
        is_demo=company.is_demo,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Run research synchronously for MVP (use background_tasks for production)
    start = time.time()
    agent = get_agent()
    result = agent.research_company(company.name, focus_area, session.id)

    session.status = ResearchStatus.completed if result.get("success") else ResearchStatus.failed
    session.duration_seconds = time.time() - start
    session.sources_count = result.get("sources_count", 0)
    session.chunks_count = result.get("chunks_count", 0)
    session.research_result = result
    if not result.get("success"):
        session.error_message = result.get("error")

    # Update company intelligence cache
    if result.get("success"):
        company.intelligence = result
        company.last_researched_at = __import__("datetime").datetime.utcnow()

    db.commit()
    db.refresh(session)

    logger.info("research_session_complete", session_id=session.id, status=session.status.value)
    return session


@router.get("/{company_id}/opportunities")
def get_company_opportunities(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.database import Opportunity
    opps = db.query(Opportunity).filter(
        Opportunity.company_id == company_id,
        Opportunity.is_active == True,
    ).order_by(Opportunity.overall_score.desc()).all()
    return opps


@router.get("/{company_id}/updates")
def get_company_updates(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.database import ResearchUpdate
    updates = db.query(ResearchUpdate).filter(
        ResearchUpdate.company_id == company_id
    ).order_by(ResearchUpdate.created_at.desc()).limit(20).all()
    return updates


def _seed_demo_companies(db: Session) -> None:
    """Seed demo companies on startup."""
    for demo in DEMO_COMPANIES:
        existing = db.query(Company).filter(Company.name == demo["name"]).first()
        if not existing:
            c = Company(id=str(uuid.uuid4()), **demo)
            db.add(c)
    db.commit()


def _audit(db: Session, user_id: str, action: AuditAction, resource_type: str, resource_id: str):
    log = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        success=True,
    )
    db.add(log)
    db.commit()
