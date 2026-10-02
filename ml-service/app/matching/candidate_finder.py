"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Candidate Retrieval & Match Finder
Description: Fast retrieval of top candidate matches for any material code/posting_id.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re
import sqlite3
from typing import Dict, List, Any, Optional

try:
    from app.normalization.text_normalizer import normalize_text
    from app.matching.hybrid_engine import get_hybrid_engine
except ImportError:
    from backend.app.ml.text_normalizer import normalize_text
    from backend.app.ml.hybrid_engine import get_hybrid_engine


def find_top_candidates(
    posting_id: str,
    top_k: int = 5,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Retrieves the query material, extracts candidate matches from SQLite,
    evaluates hybrid similarity, and returns ranked candidates with explanations.
    """
    if db_path is None:
        db_path = PROJECT_ROOT / "outputs" / "analysis" / "materials.db"

    if not db_path.exists():
        raise FileNotFoundError(f"Material database not found at {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Fetch query item
    cur.execute("SELECT * FROM materials WHERE posting_id = ?", (posting_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Material with posting_id '{posting_id}' not found.")

    query_item = dict(row)
    query_title = query_item["title"]
    query_clean = query_item["clean_title"]
    query_group = query_item["label_group"]

    # 2. Extract salient tokens for candidate retrieval (tokens with length >= 3)
    tokens = [w for w in re.findall(r"\b[a-zA-Z0-9_\-\.]{3,}\b", query_clean)]
    # Pick distinctive tokens (skip very common noise like 'dan', 'untuk', 'yang')
    stopwords = {"dan", "untuk", "yang", "dengan", "dari", "bisa", "atau", "original"}
    meaningful_tokens = [w for w in tokens if w not in stopwords]
    if not meaningful_tokens:
        meaningful_tokens = tokens[:3]
    else:
        # Sort by length descending to prioritize distinctive model numbers/specs
        meaningful_tokens = sorted(meaningful_tokens, key=len, reverse=True)[:5]

    # 3. Retrieve candidates from SQLite
    # A) Guaranteed same-group cluster candidates
    cur.execute(
        """
        SELECT posting_id, title, clean_title, label_group, group_size, image, title_length
        FROM materials
        WHERE posting_id != ? AND label_group = ?
        """,
        (posting_id, query_group),
    )
    group_candidates = [dict(r) for r in cur.fetchall()]

    # B) Lexical candidate search from other clusters
    clauses = []
    params = [posting_id, query_group]
    for tok in meaningful_tokens:
        clauses.append("clean_title LIKE ?")
        params.append(f"%{tok}%")

    sql_filter = " OR ".join(clauses)
    other_sql = f"""
        SELECT posting_id, title, clean_title, label_group, group_size, image, title_length
        FROM materials
        WHERE posting_id != ? AND label_group != ? AND ({sql_filter})
        LIMIT 40
    """
    cur.execute(other_sql, params)
    lexical_candidates = [dict(r) for r in cur.fetchall()]
    conn.close()

    raw_candidates = group_candidates + lexical_candidates

    # 4. Score candidates with hybrid engine
    engine = get_hybrid_engine()
    scored_candidates = []

    for cand in raw_candidates:
        cand_title = cand["title"]
        comp = engine.compare(query_title, cand_title)

        scored_candidates.append(
            {
                "posting_id": cand["posting_id"],
                "title": cand_title,
                "clean_title": cand["clean_title"],
                "label_group": cand["label_group"],
                "is_true_benchmark_match": cand["label_group"] == query_group,
                "hybrid_score": comp["hybrid_score"],
                "semantic_score": comp["semantic_score"],
                "lexical_score": comp["lexical_score"],
                "fuzzy_score": comp["fuzzy_score"],
                "match_decision": comp["match_decision"],
                "explanation": comp["explanation"],
                "technical_tokens": comp["technical_tokens"],
            }
        )

    # Sort descending by hybrid_score
    scored_candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
    top_candidates = scored_candidates[:top_k]

    return {
        "query_item": {
            "posting_id": query_item["posting_id"],
            "title": query_item["title"],
            "clean_title": query_item["clean_title"],
            "label_group": query_item["label_group"],
            "group_size": query_item["group_size"],
        },
        "candidate_count_evaluated": len(scored_candidates),
        "top_candidates": top_candidates,
    }


if __name__ == "__main__":
    res = find_top_candidates("train_129225211", top_k=3)
    print("Query:", res["query_item"])
    print(f"Top candidates ({len(res['top_candidates'])}):")
    for c in res["top_candidates"]:
        print(f"- [{c['posting_id']}] {c['title']} | Hybrid: {c['hybrid_score']} | Decision: {c['match_decision']}")
