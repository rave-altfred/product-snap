"""ProductSnap Backend API - Main Application Entry Point"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid
import time
import logging

# Register HEIF plugin for Pillow
from pillow_heif import register_heif_opener
register_heif_opener()

from app.core.config import settings
from app.core.logging import setup_logging, set_request_id
from app.core.redis_client import get_redis_client, close_redis_client
from app.core.database import Base, engine
from app.routers import auth, jobs, subscriptions, users, admin, health, webhooks, preview, branding, contact

# Setup logging
logger = setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware - Environment-aware origins
# Only allow frontend from same environment + localhost for local dev
allowed_origins = [
    settings.FRONTEND_URL,  # Environment-specific frontend
    "http://localhost:3000",  # Local dev
    "http://localhost:5173",  # Local dev (Vite)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_id(request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request details
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "full_url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host if request.client else None
        }
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s"
        }
    )
    
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Database tables created via Base.metadata.create_all() for now
    # TODO: Re-enable migrations after initial deployment
    logger.info("Using Base.metadata.create_all for table creation")
    try:
        from app import models  # Import all models to register them
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready")
    except Exception as e:
        logger.error(f"Database table creation failed: {e}")
        # Don't fail startup
    
    # Initialize Redis
    await get_redis_client()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")
    await close_redis_client()


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(branding.router, prefix="/api", tags=["Branding"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(preview.router, prefix="/api/preview", tags=["Preview"])
app.include_router(contact.router, prefix="/api", tags=["Contact"])


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }
