"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Text Preprocessing
Description: Specification-preserving cleaning and normalization for material and product titles.
Re-exports normalize_text from backend.app.ml.text_normalizer for backward compatibility.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.ml.text_normalizer import (
    normalize_text,
    extract_technical_tokens,
    compare_technical_tokens,
)


def clean_text(text) -> str:
    """
    Main clean_text wrapper ensuring full compatibility with earlier steps.
    """
    return normalize_text(text)


if __name__ == "__main__":
    t = "M10 SS304 BOLT 50MM - Grade 8.8"
    print("Cleaned:", clean_text(t))
    print("Technical tokens:", extract_technical_tokens(t))
