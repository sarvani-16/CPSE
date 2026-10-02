"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
ML Service: FastAPI Endpoints for Model Inference, Comparison, and Attribute Extraction
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.schemas.matching import (
    CompareRequest,
    CompareResponse,
    AttributeExtractionRequest,
    AttributeExtractionResponse,
    BatchCompareRequest,
    BatchCompareResponse,
)
from app.services.matching_service import get_matching_service

router = APIRouter(prefix="/api", tags=["AI/ML Service"])
matching_service = get_matching_service()


@router.post("/match", response_model=CompareResponse)
@router.post("/matching/compare", response_model=CompareResponse)
def compare_materials(req: CompareRequest):
    """
    POST /api/match or POST /api/matching/compare
    Performs AI hybrid matching between two material descriptions.
    Enforces technical domain guardrails (e.g. SS304 vs SS316).
    """
    if not req.title_a.strip() or not req.title_b.strip():
        raise HTTPException(
            status_code=400,
            detail="Both 'title_a' and 'title_b' must be non-empty strings.",
        )
    return matching_service.compare(req.title_a, req.title_b)


@router.post("/batch-match", response_model=BatchCompareResponse)
def batch_compare(req: BatchCompareRequest):
    """
    POST /api/batch-match
    Batched comparison of multiple material pairs.
    """
    if not req.pairs:
        raise HTTPException(status_code=400, detail="Pair list cannot be empty.")
    raw_pairs = [{"title_a": p.title_a, "title_b": p.title_b} for p in req.pairs]
    results = matching_service.batch_compare(raw_pairs)
    return BatchCompareResponse(total_pairs=len(results), results=results)


@router.post("/extract-attributes", response_model=AttributeExtractionResponse)
def extract_attributes(req: AttributeExtractionRequest):
    """
    POST /api/extract-attributes
    Normalizes text and extracts dimensional/metallurgical technical tokens.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    return matching_service.extract_attributes(req.text)


@router.get("/candidates/{posting_id}")
@router.get("/matching/candidates/{posting_id}")
def get_candidates(
    posting_id: str,
    top_k: int = Query(default=5, ge=1, le=20, description="Top K candidate matches"),
):
    """
    GET /api/candidates/{posting_id}
    Retrieves top candidate matches from the benchmark dataset.
    """
    try:
        return matching_service.find_candidates(posting_id=posting_id, top_k=top_k)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candidate retrieval error: {str(e)}")


@router.get("/health")
def ml_health():
    """
    ML Service Health Check.
    """
    return {
        "status": "ok",
        "service": "SIH26099 Dedicated AI/ML Service",
        "port": 8001,
        "models": {
            "semantic": "sentence-transformers/all-MiniLM-L6-v2",
            "lexical": "TF-IDF (word 1-2, char 3-5 n-grams)",
            "fuzzy": "RapidFuzz (token_set, token_sort, partial_ratio)",
            "guardrails": "Technical token conflict detection (SS304/SS316, dimensions)",
        },
    }
