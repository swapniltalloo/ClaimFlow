from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.endpoints import health, claims


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ClaimFlow API Engine starting up...")
    yield
    logger.info("ClaimFlow API Engine shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-Time Insurance Claim Settlement & Fraud Defense Clearinghouse",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, tags=["Health"])
app.include_router(claims.router, prefix=settings.API_V1_PREFIX)

