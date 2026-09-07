"""Auth API routes."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import authenticate_user, register_user, create_access_token
from app.schemas.schemas import UserCreate, UserLogin, TokenResponse, UserOut, SuccessResponse
from app.api.deps import get_current_user
from app.models.database import User, AuditLog, AuditAction
from app.config import settings
from app.utils.logger import get_logger
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger("auth_api")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = register_user(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        logger.warning("login_failed", email=data.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action=AuditAction.login,
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )
    db.add(audit)
    db.commit()

    logger.info("login_success", user_id=user.id, role=user.role.value)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", response_model=SuccessResponse)
def logout(current_user: User = Depends(get_current_user)):
    # JWT is stateless — client drops the token
    logger.info("logout", user_id=current_user.id)
    return SuccessResponse(message="Logged out successfully")
