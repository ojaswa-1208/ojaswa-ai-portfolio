
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router

from app.config import settings
from app.api.health import router as health_router
from app.api.resume import router as resume_router
from app.core.logging import configure_logging, logger
from app.core.exceptions import register_exception_handlers
from app.core.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    logger.info(
        "application_starting",
        environment=settings.ENVIRONMENT,
        version=settings.APP_VERSION,
    )

    yield

    logger.info("application_stopping")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade AI-powered personal portfolio assistant.",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

# Rate limiter
app.state.limiter = limiter

# Centralized exception handlers
register_exception_handlers(app)

# Register API routers
app.include_router(
    health_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    resume_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    chat_router,
    prefix=settings.API_PREFIX,
)

# Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


@app.get("/")
async def home(request: Request):
    return {
        "success": True,
        "message": "Welcome to Ojaswa AI Portfolio Assistant",
        "status": "running",
        "version": settings.APP_VERSION,
        "request_id": getattr(
            request.state,
            "request_id",
            None,
        ),
    }
