"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Fuzzy Matching (Step 7)
Description: RapidFuzz multi-strategy string similarity.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.fuzzy_matcher import FuzzyMatcher, get_fuzzy_matcher

if __name__ == "__main__":
    matcher = get_fuzzy_matcher()
    t1 = "M10 SS304 BOLT 50MM"
    t2 = "M10 SS316 BOLT 50MM"
    t3 = "BOLT 50MM M10 SS304"
    print("T1 vs T2:", matcher.compute_similarity(t1, t2))
    print("T1 vs T3:", matcher.compute_similarity(t1, t3))
