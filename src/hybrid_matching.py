"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Hybrid Matching Engine (Steps 10 & 11)
Description: Lexical + Fuzzy + Semantic ensemble with evidence-based explainability.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.hybrid_engine import HybridMatchingEngine, get_hybrid_engine

if __name__ == "__main__":
    engine = get_hybrid_engine()
    t1 = "M10 SS304 BOLT 50MM - Grade 8.8 (High Tensile)"
    t2 = "M10 SS316 BOLT 50MM - Grade 8.8 (High Tensile)"
    res = engine.compare(t1, t2)
    print("Compare result:")
    print("Hybrid score:", res["hybrid_score"])
    print("Decision:", res["match_decision"])
    print("Explanations:", res["explanation"])
