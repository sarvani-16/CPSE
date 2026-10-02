"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Semantic Matching (Step 8)
Description: Sentence Transformers dense embeddings & cached cosine similarity.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.semantic_matcher import SemanticMatcher, get_semantic_matcher

if __name__ == "__main__":
    matcher = get_semantic_matcher()
    t1 = "M10 SS304 BOLT 50MM"
    t2 = "M10 SS316 BOLT 50MM"
    t3 = "CELANA WANITA KULOT"
    print("T1 vs T2 Semantic Similarity:", matcher.compute_similarity(t1, t2))
    print("T1 vs T3 Semantic Similarity:", matcher.compute_similarity(t1, t3))
    matcher.save_cache()
