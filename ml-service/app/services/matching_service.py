"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
ML Service: Matching Service Layer
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from app.normalization.text_normalizer import (
    normalize_text,
    extract_technical_tokens,
    compare_technical_tokens,
)
from app.matching.hybrid_engine import HybridMatchingEngine, get_hybrid_engine
from app.matching.candidate_finder import find_top_candidates


class MatchingService:
    def __init__(self):
        self.engine: HybridMatchingEngine = get_hybrid_engine()

    def compare(self, title_a: str, title_b: str) -> Dict[str, Any]:
        """
        Executes lexical, fuzzy, and semantic comparison with technical domain guardrails.
        """
        res = self.engine.compare(title_a, title_b)
        return {
            "title_a": title_a,
            "title_b": title_b,
            "match_decision": res["match_decision"],
            "hybrid_score": res["hybrid_score"],
            "semantic_score": res["semantic_score"],
            "lexical_score": res["lexical_score"],
            "fuzzy_score": res["fuzzy_score"],
            "explanation": res["explanation"],
            "technical_tokens": res["technical_tokens"],
            "sub_scores": res["sub_scores"],
            "weights": res["weights"],
        }

    def batch_compare(self, pairs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Processes a list of material comparison pairs in batch.
        """
        results = []
        for pair in pairs:
            title_a = pair.get("title_a", "")
            title_b = pair.get("title_b", "")
            results.append(self.compare(title_a, title_b))
        return results

    def extract_attributes(self, text: str) -> Dict[str, Any]:
        """
        Normalizes industrial text and extracts dimensional/metallurgical technical tokens.
        """
        clean = normalize_text(text)
        tokens = sorted(list(extract_technical_tokens(text)))
        return {
            "normalized_text": clean,
            "technical_tokens": tokens,
            "token_count": len(tokens),
        }

    def find_candidates(self, posting_id: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieves candidate matches from benchmark dataset.
        """
        return find_top_candidates(posting_id=posting_id, top_k=top_k)


_service_instance: Optional[MatchingService] = None


def get_matching_service() -> MatchingService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MatchingService()
    return _service_instance
