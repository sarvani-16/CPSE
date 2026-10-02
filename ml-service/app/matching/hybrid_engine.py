"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Hybrid Matching Engine (Stages 6, 7 & 9)
Description: Lexical + Fuzzy + Semantic ensemble with evidence-based explainability and domain guardrails.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

try:
    from app.normalization.text_normalizer import (
        normalize_text,
        extract_technical_tokens,
        compare_technical_tokens,
    )
    from app.matching.tfidf_matcher import get_tfidf_matcher
    from app.matching.fuzzy_matcher import get_fuzzy_matcher
    from app.matching.semantic_matcher import get_semantic_matcher
except ImportError:
    from backend.app.ml.text_normalizer import (
        normalize_text,
        extract_technical_tokens,
        compare_technical_tokens,
    )
    from backend.app.ml.tfidf_matcher import get_tfidf_matcher
    from backend.app.ml.fuzzy_matcher import get_fuzzy_matcher
    from backend.app.ml.semantic_matcher import get_semantic_matcher


class HybridMatchingEngine:
    """
    Ensemble Matching Engine combining:
    1. Lexical Similarity (TF-IDF word & character n-grams)
    2. Fuzzy Similarity (RapidFuzz token set, sort, ratio)
    3. Semantic Similarity (SentenceTransformer dense embeddings)

    Features:
    - Configurable weights (experimental default: 0.30 lexical, 0.30 fuzzy, 0.40 semantic)
    - 3-State Decision Model: MATCH, REVIEW, NOT_MATCH
    - Domain Guardrails: Blocks automatic MATCH if critical technical specifications conflict
    - Evidence-Based Explainability for government procurement & material master reviewers
    """

    def __init__(
        self,
        weight_lexical: float = 0.30,
        weight_fuzzy: float = 0.30,
        weight_semantic: float = 0.40,
        threshold_match: float = 0.78,
        threshold_review: float = 0.52,
    ):
        # Normalize weights to sum to 1.0
        total_w = weight_lexical + weight_fuzzy + weight_semantic
        self.w_lex = weight_lexical / total_w
        self.w_fuzz = weight_fuzzy / total_w
        self.w_sem = weight_semantic / total_w

        self.threshold_match = threshold_match
        self.threshold_review = threshold_review

        self.tfidf_matcher = get_tfidf_matcher()
        self.fuzzy_matcher = get_fuzzy_matcher()
        self.semantic_matcher = get_semantic_matcher()

    def compare(
        self, title_a: str, title_b: str
    ) -> Dict[str, Any]:
        """
        Calculates lexical, fuzzy, and semantic similarity scores,
        evaluates technical specifications, and determines match decision and explanation.
        """
        # 1. Component scores
        lex_res = self.tfidf_matcher.compute_similarity(title_a, title_b)
        fuzz_res = self.fuzzy_matcher.compute_similarity(title_a, title_b)
        sem_res = self.semantic_matcher.compute_similarity(title_a, title_b)

        lex_score = lex_res["lexical_score"]
        fuzz_score = fuzz_res["fuzzy_score"]
        sem_score = sem_res["semantic_score"]

        # 2. Hybrid score calculation
        hybrid_score = (
            (self.w_lex * lex_score)
            + (self.w_fuzz * fuzz_score)
            + (self.w_sem * sem_score)
        )
        hybrid_score = round(max(0.0, min(1.0, hybrid_score)), 4)

        # 3. Technical specification evidence analysis
        spec_evidence = compare_technical_tokens(title_a, title_b)
        has_conflicts = spec_evidence["has_conflicts"]
        conflicts = spec_evidence["conflicts"]
        matching_tokens = spec_evidence["matching_tokens"]

        # 4. Decision determination with domain guardrail
        # Guardrail: Never auto-MATCH if critical specifications conflict (e.g., SS304 vs SS316)
        if hybrid_score >= self.threshold_match:
            if has_conflicts:
                decision = "REVIEW"  # Demote due to conflicting specs
            else:
                decision = "MATCH"
        elif hybrid_score >= self.threshold_review:
            decision = "REVIEW"
        else:
            decision = "NOT_MATCH"

        # 5. Evidence-based explanation generation
        explanations = self._generate_explanations(
            hybrid_score=hybrid_score,
            sem_score=sem_score,
            lex_score=lex_score,
            fuzz_score=fuzz_score,
            decision=decision,
            spec_evidence=spec_evidence,
        )

        return {
            "match_decision": decision,
            "hybrid_score": hybrid_score,
            "semantic_score": sem_score,
            "lexical_score": lex_score,
            "fuzzy_score": fuzz_score,
            "explanation": explanations,
            "technical_tokens": {
                "matching": matching_tokens,
                "differing_a": spec_evidence["differing_tokens_a"],
                "differing_b": spec_evidence["differing_tokens_b"],
                "conflicts": conflicts,
                "has_conflicts": has_conflicts,
            },
            "sub_scores": {
                "tfidf_word": lex_res["word_sim"],
                "tfidf_char": lex_res["char_sim"],
                "fuzzy_token_set": fuzz_res["token_set_ratio"],
                "fuzzy_token_sort": fuzz_res["token_sort_ratio"],
                "fuzzy_ratio": fuzz_res["ratio"],
            },
            "weights": {
                "lexical": round(self.w_lex, 2),
                "fuzzy": round(self.w_fuzz, 2),
                "semantic": round(self.w_sem, 2),
            },
        }

    def _generate_explanations(
        self,
        hybrid_score: float,
        sem_score: float,
        lex_score: float,
        fuzz_score: float,
        decision: str,
        spec_evidence: Dict[str, Any],
    ) -> List[str]:
        """
        Constructs factual explanations strictly supported by computed metrics.
        """
        notes = []

        # Conflict notes
        if spec_evidence["has_conflicts"]:
            conflict_str = ", ".join(spec_evidence["conflicts"])
            notes.append(
                f"Conflicting technical specification detected ({conflict_str}). Cannot auto-merge — requires manual engineering review."
            )

        # Semantic notes
        if sem_score >= 0.82:
            notes.append(
                f"High semantic similarity ({sem_score:.2f}) indicates equivalent product taxonomy and functional purpose."
            )
        elif sem_score >= 0.55:
            notes.append(
                f"Moderate semantic similarity ({sem_score:.2f}) indicates related product categories with descriptive variations."
            )
        else:
            notes.append(
                f"Low semantic similarity ({sem_score:.2f}) indicates distinct or unrelated material categories."
            )

        # Matching tokens
        matching = spec_evidence["matching_tokens"]
        if matching:
            sample_m = ", ".join(matching[:5])
            notes.append(
                f"Matching technical and dimensional tokens verified: [{sample_m}]."
            )

        # String alignment
        if fuzz_score >= 0.80:
            notes.append(
                f"High lexical token alignment ({fuzz_score:.2f}) across title descriptions."
            )
        elif fuzz_score < 0.40 and sem_score >= 0.70:
            notes.append(
                "Significant lexical variation observed, but semantic embeddings preserve contextual equivalence."
            )

        # Overall summary statement
        if decision == "MATCH":
            notes.append(
                "High confidence recommendation: Items are standardized variants suitable for harmonization under a common item code."
            )
        elif decision == "REVIEW":
            if not spec_evidence["has_conflicts"]:
                notes.append(
                    "Borderline confidence: Manual review recommended by technical authority before establishing code linkage."
                )
        else:
            notes.append(
                "Disparate items: Material attributes and similarity metrics indicate distinct non-interchangeable materials."
            )

        return notes


# Singleton engine instance
_engine_instance: Optional[HybridMatchingEngine] = None


def get_hybrid_engine() -> HybridMatchingEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = HybridMatchingEngine()
    return _engine_instance


if __name__ == "__main__":
    engine = get_hybrid_engine()
    print("--- Test 1: Identical variants ---")
    t1 = "M10 SS304 BOLT 50MM - Grade 8.8 (High Tensile)"
    t2 = "M10 SS304 BOLT 50MM pack of 10 pcs"
    res1 = engine.compare(t1, t2)
    print("Decision:", res1["match_decision"], "| Hybrid:", res1["hybrid_score"])
    print("Explanations:", res1["explanation"])

    print("\n--- Test 2: Specification Conflict (SS304 vs SS316) ---")
    t3 = "M10 SS316 BOLT 50MM - Grade 8.8 (High Tensile)"
    res2 = engine.compare(t1, t3)
    print("Decision:", res2["match_decision"], "| Hybrid:", res2["hybrid_score"])
    print("Explanations:", res2["explanation"])
