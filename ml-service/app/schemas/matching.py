"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
ML Service: Pydantic Schemas for AI/ML Matching & Attribute Extraction
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CompareRequest(BaseModel):
    title_a: str = Field(..., description="First material description/title")
    title_b: str = Field(..., description="Second material description/title")


class TechnicalTokensInfo(BaseModel):
    matching: List[str] = Field(default_factory=list)
    differing_a: List[str] = Field(default_factory=list)
    differing_b: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    has_conflicts: bool = False


class CompareResponse(BaseModel):
    title_a: str
    title_b: str
    match_decision: str = Field(..., description="MATCH, REVIEW, or NOT_MATCH")
    hybrid_score: float
    semantic_score: float
    lexical_score: float
    fuzzy_score: float
    explanation: List[str]
    technical_tokens: TechnicalTokensInfo
    sub_scores: Dict[str, float]
    weights: Dict[str, float]


class AttributeExtractionRequest(BaseModel):
    text: str = Field(..., description="Raw material description text")


class AttributeExtractionResponse(BaseModel):
    normalized_text: str
    technical_tokens: List[str]
    token_count: int


class BatchCompareRequest(BaseModel):
    pairs: List[CompareRequest]


class BatchCompareResponse(BaseModel):
    total_pairs: int
    results: List[CompareResponse]
