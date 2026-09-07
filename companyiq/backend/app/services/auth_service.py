"""Auth service — JWT creation, password hashing, token verification."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("about", (), {"__version__": getattr(bcrypt, "__version__", "4.0.0")})
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.models.database import User, UserRole, AuditLog, AuditAction
from app.schemas.schemas import UserCreate
from app.utils.logger import get_logger

logger = get_logger("auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    password_safe = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password_safe)


def verify_password(plain: str, hashed: str) -> bool:
    plain_safe = plain.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.verify(plain_safe, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def register_user(db: Session, data: UserCreate) -> User:
    if get_user_by_email(db, data.email):
        raise ValueError("Email already registered")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole(data.role) if data.role in [r.value for r in UserRole] else UserRole.analyst,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("user_registered", email=data.email, role=user.role.value)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_demo_users(db: Session) -> None:
    """Seed demo users if they don't exist."""
    demos = [
        {"email": "admin@companyiq.demo", "password": "Admin@1234", "full_name": "Demo Admin", "role": "admin"},
        {"email": "manager@companyiq.demo", "password": "Manager@1234", "full_name": "Demo Manager", "role": "manager"},
        {"email": "analyst@companyiq.demo", "password": "Analyst@1234", "full_name": "Demo Analyst", "role": "analyst"},
    ]
    for d in demos:
        if not get_user_by_email(db, d["email"]):
            register_user(db, UserCreate(**d))
            logger.info("demo_user_seeded", email=d["email"])
