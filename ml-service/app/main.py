"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
ML Service: FastAPI Application Entrypoint
Runs on: http://127.0.0.1:8001
"""

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

# CORS: Allow Spring Boot backend and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ml_router)


@app.get("/")
def root():
    return {
        "service": "SIH26099 Dedicated AI/ML Service",
        "status": "online",
        "port": 8001,
        "docs": "/docs",
        "endpoints": [
            "POST /api/match",
            "POST /api/batch-match",
            "POST /api/extract-attributes",
            "GET /api/candidates/{posting_id}",
            "GET /api/health",
        ],
    }


def start():
    print("=" * 70)
    print("Starting SIH26099 AI/ML Microservice on port 8001...")
    print("Documentation: http://127.0.0.1:8001/docs")
    print("=" * 70)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=False)


if __name__ == "__main__":
    start()
