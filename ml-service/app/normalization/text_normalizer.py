"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Text Normalizer (Stage 1)
Description: Specification-preserving industrial text normalizer for product & material titles.
"""

import re
from typing import Any, Dict, List, Set, Tuple, Union
import pandas as pd

# Safe standard unit and abbreviation normalizations (without losing technical meaning)
SAFE_ABBREVIATIONS = {
    r"\bpcs\b": "pc",
    r"\bpieces\b": "pc",
    r"\bpiece\b": "pc",
    r"\bgr\b": "g",
    r"\bgram\b": "g",
    r"\bgrams\b": "g",
    r"\bkilogram\b": "kg",
    r"\bkilograms\b": "kg",
    r"\bml\b": "ml",
    r"\bmtr\b": "m",
    r"\bmeter\b": "m",
    r"\bcentimeter\b": "cm",
    r"\bmillimeter\b": "mm",
    r"\bvolt\b": "v",
    r"\bvolts\b": "v",
    r"\bwatt\b": "w",
    r"\bwatts\b": "w",
}

# Regex to capture technical tokens: grades, dimensions, bolt sizes, model numbers, values+units
TECH_TOKEN_REGEX = re.compile(
    r"""
    \b[a-z]{1,4}\d+[a-z0-9\-\.]*\b      # e.g., m10, ss304, ss316, tc11, dpt001, t5, a1
    | \b\d+(?:\.\d+)?\s*(?:mm|cm|m|kg|g|ml|l|v|w|a|kw|hz|bar|psi|gr|thn|pcs|pc)\b  # e.g., 50mm, 100ml, 12v, 5kg
    | \b\d+(?:\.\d+)?\s*[xX*]\s*\d+(?:\.\d+)?(?:\s*[xX*]\s*\d+(?:\.\d+)?)?\b       # e.g., 10x50, 18x18
    | \b(?:grade|grd)\s*\d+(?:\.\d+)?\b                                             # e.g., grade 8.8
    | \b\d+-\d+\b                                                                   # e.g., 45-84, 1-12
    """,
    re.IGNORECASE | re.VERBOSE,
)


def normalize_text(text: Union[str, float, int]) -> str:
    """
    Industrial text normalization that preserves technical tokens, specs, and numbers:
    1. Handles non-string/null values.
    2. Lowercases text.
    3. Normalizes unicode hyphens, slashes, and quotes.
    4. Normalizes dimensional multipliers (e.g., '10 x 50' -> '10x50').
    5. Normalizes consecutive repeated characters (e.g. 'cooool' -> 'cool', but leaves 'ss304').
    6. Replaces non-alphanumeric separators while preserving hyphens, slashes, and decimal points.
    7. Applies safe abbreviation mapping (e.g., 'gr' -> 'g', 'pcs' -> 'pc').
    8. Normalizes and trims excess whitespace.
    """
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""

    if not isinstance(text, str):
        text = str(text)

    # 1. Lowercase
    cleaned = text.lower()

    # 2. Normalize unicode punctuation and quotes
    cleaned = re.sub(r"[\u2010-\u2015\u2212\uFE58\uFE63\uFF0D]", "-", cleaned)
    cleaned = re.sub(r"[\u2018\u2019\u201C\u201D\u0060\u00B4]", "'", cleaned)

    # 3. Collapse 3+ consecutive duplicate letters to 2 (e.g. 'sooo' -> 'so', 'baaaanget' -> 'baanget')
    cleaned = re.sub(r"([a-z])\1{2,}", r"\1\1", cleaned)

    # 4. Standardize dimensional 'X' between numbers (e.g., '10 x 50' -> '10x50')
    cleaned = re.sub(r"(?<=\d)\s*[xX*]\s*(?=\d)", "x", cleaned)

    # 5. Clean punctuation: keep letters, digits, whitespace, '.', '-', '/', '+'
    cleaned = re.sub(r"[^a-z0-9\s\.\-\/\+]", " ", cleaned)

    # 6. Preserve decimal points between digits, replace standalone dots
    cleaned = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", cleaned)

    # 7. Collapse consecutive hyphens/slashes
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    cleaned = re.sub(r"\/{2,}", "/", cleaned)
    cleaned = re.sub(r"\s+[\-\/]\s+", " ", cleaned)

    # 8. Apply safe unit/abbreviation normalization
    for pattern, replacement in SAFE_ABBREVIATIONS.items():
        cleaned = re.sub(pattern, replacement, cleaned)

    # 9. Collapse multiple whitespaces and strip
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def extract_technical_tokens(text: str) -> Set[str]:
    """
    Extracts all distinct technical, dimensional, grade, and numeric tokens from text.
    """
    norm = normalize_text(text)
    matches = TECH_TOKEN_REGEX.findall(norm)
    tokens = set()
    for m in matches:
        token = m.strip().replace(" ", "")
        if len(token) > 1:
            tokens.add(token)
    return tokens


def compare_technical_tokens(title_a: str, title_b: str) -> Dict[str, Any]:
    """
    Compares technical tokens between two titles to provide ground-truth evidence:
    - matching_tokens: tokens present in both descriptions
    - differing_tokens_a: tokens exclusive to Material A
    - differing_tokens_b: tokens exclusive to Material B
    - has_conflicts: boolean indicating critical conflicting technical specifications
    """
    tokens_a = extract_technical_tokens(title_a)
    tokens_b = extract_technical_tokens(title_b)

    common = tokens_a.intersection(tokens_b)
    diff_a = tokens_a - common
    diff_b = tokens_b - common

    # Conflict detection: e.g., ss304 vs ss316, 50mm vs 100mm, 12v vs 24v
    conflicts = []
    for ta in diff_a:
        for tb in diff_b:
            # Check if they share the same unit or prefix category but have different values
            # e.g., both end with 'mm' or both start with 'ss' or 'm'
            unit_a = re.sub(r"^[0-9\.]+", "", ta)
            unit_b = re.sub(r"^[0-9\.]+", "", tb)
            prefix_a = re.sub(r"[0-9\.]+$", "", ta)
            prefix_b = re.sub(r"[0-9\.]+$", "", tb)

            if unit_a and unit_a == unit_b and ta != tb:
                conflicts.append(f"{ta} vs {tb}")
            elif prefix_a and prefix_a == prefix_b and ta != tb and len(prefix_a) >= 1:
                conflicts.append(f"{ta} vs {tb}")

    return {
        "matching_tokens": sorted(list(common)),
        "tokens_a": sorted(list(tokens_a)),
        "tokens_b": sorted(list(tokens_b)),
        "differing_tokens_a": sorted(list(diff_a)),
        "differing_tokens_b": sorted(list(diff_b)),
        "conflicts": conflicts,
        "has_conflicts": len(conflicts) > 0,
    }


if __name__ == "__main__":
    t1 = "M10 SS304 BOLT 50MM - Grade 8.8 (High Tensile)"
    t2 = "M10 SS316 BOLT 50MM - Grade 8.8 (High Tensile)"
    t3 = "M10 SS304 BOLT 50MM pack of 10 pcs"

    print("Title 1 Normalization:", normalize_text(t1))
    print("Title 2 Normalization:", normalize_text(t2))
    print("\nComparing T1 vs T2 (Spec Conflict SS304 vs SS316):")
    print(compare_technical_tokens(t1, t2))
    print("\nComparing T1 vs T3 (Matching Specs):")
    print(compare_technical_tokens(t1, t3))
