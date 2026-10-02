"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Fuzzy Matcher (Stage 3)
Description: RapidFuzz multi-metric string similarity calculator.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, Optional
from rapidfuzz import fuzz
from backend.app.ml.text_normalizer import normalize_text


class FuzzyMatcher:
    """
    Computes fuzzy string similarity using RapidFuzz algorithms:
    - ratio: overall Levenshtein character distance
    - partial_ratio: substring similarity (handles truncated or extra words)
    - token_sort_ratio: word-order invariant similarity
    - token_set_ratio: set-based similarity (handles duplicate words and subsets)
    """

    def __init__(
        self,
        weight_token_set: float = 0.40,
        weight_token_sort: float = 0.30,
        weight_partial: float = 0.15,
        weight_ratio: float = 0.15,
    ):
        self.w_set = weight_token_set
        self.w_sort = weight_token_sort
        self.w_partial = weight_partial
        self.w_ratio = weight_ratio

    def compute_similarity(self, text_a: str, text_b: str) -> Dict[str, float]:
        norm_a = normalize_text(text_a)
        norm_b = normalize_text(text_b)

        if not norm_a or not norm_b:
            return {
                "ratio": 0.0,
                "partial_ratio": 0.0,
                "token_sort_ratio": 0.0,
                "token_set_ratio": 0.0,
                "fuzzy_score": 0.0,
            }

        score_ratio = fuzz.ratio(norm_a, norm_b) / 100.0
        score_partial = fuzz.partial_ratio(norm_a, norm_b) / 100.0
        score_sort = fuzz.token_sort_ratio(norm_a, norm_b) / 100.0
        score_set = fuzz.token_set_ratio(norm_a, norm_b) / 100.0

        fuzzy_score = (
            (self.w_set * score_set)
            + (self.w_sort * score_sort)
            + (self.w_partial * score_partial)
            + (self.w_ratio * score_ratio)
        )
        fuzzy_score = max(0.0, min(1.0, fuzzy_score))

        return {
            "ratio": round(score_ratio, 4),
            "partial_ratio": round(score_partial, 4),
            "token_sort_ratio": round(score_sort, 4),
            "token_set_ratio": round(score_set, 4),
            "fuzzy_score": round(fuzzy_score, 4),
        }


# Singleton instance
_fuzzy_instance: Optional[FuzzyMatcher] = None


def get_fuzzy_matcher() -> FuzzyMatcher:
    global _fuzzy_instance
    if _fuzzy_instance is None:
        _fuzzy_instance = FuzzyMatcher()
    return _fuzzy_instance
