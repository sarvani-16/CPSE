"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
ML Service: FastAPI Application Entrypoint
Runs on: http://127.0.0.1:8001 (or 0.0.0.0:$PORT in production on Render)
"""

import os
import sys
from pathlib import Path

# Ensure ml-service root and project root are in sys.path
ML_SERVICE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ML_SERVICE_ROOT.parent

for p in [str(ML_SERVICE_ROOT), str(PROJECT_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.endpoints import router as ml_router

app = FastAPI(
    title="SIH26099 AI/ML Harmonization Microservice",
    description="Dedicated AI/ML Service: MiniLM dense embeddings, TF-IDF lexical matching, RapidFuzz string similarity, and domain guardrails.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: Allow Spring Boot backend, local dev, and Render production domains
allowed_origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

# Add custom origins from environment if provided
custom_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "") or os.environ.get("FRONTEND_URL", "")
if custom_origins:
    for origin in custom_origins.split(","):
        cleaned = origin.strip().rstrip("/")
        if cleaned and cleaned not in allowed_origins:
            allowed_origins.append(cleaned)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://.*\.onrender\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ml_router)


@app.get("/health")
def health():
    """Simple health check endpoint for Render / monitoring."""
    return {
        "status": "ok",
        "service": "SIH26099 Dedicated AI/ML Service",
        "port": int(os.environ.get("PORT", 8001)),
    }


@app.get("/")
def root():
    return {
        "service": "SIH26099 Dedicated AI/ML Service",
        "status": "online",
        "port": int(os.environ.get("PORT", 8001)),
        "docs": "/docs",
        "endpoints": [
            "POST /api/match",
            "POST /api/batch-match",
            "POST /api/extract-attributes",
            "GET /api/candidates/{posting_id}",
            "GET /api/health",
            "GET /health",
        ],
    }


def start():
    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "0.0.0.0")
    print("=" * 70)
    print(f"Starting SIH26099 AI/ML Microservice on {host}:{port}...")
    print(f"Documentation: http://{host}:{port}/docs")
    print("=" * 70)
    uvicorn.run("app.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    start()
