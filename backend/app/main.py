from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.endpoints import health, claims, gcp_fhir_ingest, hospital_appeal


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
app.include_router(gcp_fhir_ingest.router, prefix=settings.API_V1_PREFIX)
app.include_router(hospital_appeal.router, prefix=settings.API_V1_PREFIX)

# Mount built frontend static files if dist directory exists (Unified Docker Container)
import os
from fastapi.staticfiles import StaticFiles

possible_dist_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist"),
    "/app/frontend/dist"
]

frontend_dist = next((p for p in possible_dist_paths if os.path.isdir(p)), None)
if frontend_dist:
    logger.info(f"Serving built frontend static assets from: {frontend_dist}")
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


