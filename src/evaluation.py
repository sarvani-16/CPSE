"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Model Evaluation (Step 9)
Description: Unified benchmarking table comparing Lexical, Fuzzy, Semantic, and Hybrid models.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.evaluator import run_evaluation

if __name__ == "__main__":
    run_evaluation()
