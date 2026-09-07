"""
CompanyIQ — Structured Logging
All logs are emitted as JSON with consistent fields.
Never log secrets or sensitive credentials.
"""
import sys
import uuid
import structlog
from contextvars import ContextVar
from app.config import settings

# Context variables for request-scoped metadata
_request_id: ContextVar[str] = ContextVar("request_id", default="")
_user_id: ContextVar[str] = ContextVar("user_id", default="")
_company_id: ContextVar[str] = ContextVar("company_id", default="")


def set_request_context(request_id: str = "", user_id: str = "", company_id: str = "") -> None:
    _request_id.set(request_id or str(uuid.uuid4()))
    _user_id.set(user_id)
    _company_id.set(company_id)


def add_request_context(logger, method, event_dict):
    event_dict["request_id"] = _request_id.get("")
    event_dict["user_id"] = _user_id.get("")
    event_dict["company_id"] = _company_id.get("")
    return event_dict


def configure_logging() -> None:
    log_level = settings.log_level.upper()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_request_context,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(__import__("logging"), log_level, 20)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "companyiq") -> structlog.BoundLogger:
    return structlog.get_logger(name)
