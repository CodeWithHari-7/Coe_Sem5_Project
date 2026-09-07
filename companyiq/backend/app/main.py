"""
CompanyIQ FastAPI Application Entry Point.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import create_tables, SessionLocal
from app.utils.logger import configure_logging, get_logger, set_request_context
from app.api.auth import router as auth_router
from app.api.companies import router as companies_router, _seed_demo_companies
from app.api.research import router as research_router
from app.api.plans import plans_router, feedback_router, notif_router, eval_router, dashboard_router
from app.services.auth_service import create_demo_users
import uuid
import time

configure_logging()
logger = get_logger("app")

os.makedirs(settings.upload_dir, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", app=settings.app_name, env=settings.app_env, demo_mode=settings.demo_mode)
    create_tables()
    db = SessionLocal()
    try:
        create_demo_users(db)
        _seed_demo_companies(db)
    finally:
        db.close()
    yield
    logger.info("shutdown", app=settings.app_name)


app = FastAPI(
    title="CompanyIQ API",
    description="AI-Powered Company Research & Account Planning Assistant",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    set_request_context(request_id=request_id)
    start = time.time()
    response = await call_next(request)
    latency = round((time.time() - start) * 1000, 1)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=latency,
    )
    response.headers["X-Request-ID"] = request_id
    return response


# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    logger.warning("validation_error", errors=str(exc.errors())[:200])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": "Validation error", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal server error", "error_type": type(exc).__name__},
    )


# Register routers
app.include_router(auth_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(research_router, prefix="/api")
app.include_router(plans_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(notif_router, prefix="/api")
app.include_router(eval_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "demo_mode": settings.demo_mode,
        "llm_provider": settings.llm_provider,
    }


# ── Single Localhost URL: Serve Frontend SPA from frontend/dist ──────────────
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Do not catch unresolved /api calls with HTML
        if full_path.startswith("api"):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "API endpoint not found"}
            )
        # Check if direct static file exists in dist (e.g., favicon.svg, icons.svg)
        static_file = frontend_dist / full_path
        if full_path and static_file.is_file():
            return FileResponse(str(static_file))
        # Fallback to index.html for React Router SPA routes
        return FileResponse(str(frontend_dist / "index.html"))

