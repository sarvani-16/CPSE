"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Model Evaluation (Stage 8)
Description: Benchmarking and metric calculation for Lexical, Fuzzy, Semantic, and Hybrid models on controlled pairs.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Dict, List, Any
import numpy as np
import pandas as pd

try:
    from app.matching.tfidf_matcher import get_tfidf_matcher
    from app.matching.fuzzy_matcher import get_fuzzy_matcher
    from app.matching.semantic_matcher import get_semantic_matcher
    from app.matching.hybrid_engine import get_hybrid_engine
except ImportError:
    from backend.app.ml.tfidf_matcher import get_tfidf_matcher
    from backend.app.ml.fuzzy_matcher import get_fuzzy_matcher
    from backend.app.ml.semantic_matcher import get_semantic_matcher
    from backend.app.ml.hybrid_engine import get_hybrid_engine


def calculate_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, Any]:
    """
    Computes precision, recall, F1, accuracy, and confusion matrix counts.
    """
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    total = len(y_true)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0

    return {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "accuracy": round(float(accuracy), 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "confusion_matrix": {
            "tp": int(tp),
            "fp": int(fp),
            "tn": int(tn),
            "fn": int(fn),
        },
    }


def run_evaluation(
    pairs_csv: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    threshold: float = 0.55,
) -> Dict[str, Any]:
    """
    Evaluates all 4 matching strategies on the controlled pairs dataset:
    1. TF-IDF baseline (Lexical)
    2. Fuzzy matching (RapidFuzz)
    3. Semantic matching (SentenceTransformer)
    4. Hybrid model (Ensemble)
    """
    if pairs_csv is None:
        pairs_csv = PROJECT_ROOT / "outputs" / "analysis" / "matching_pairs.csv"
    if output_dir is None:
        output_dir = PROJECT_ROOT / "outputs" / "results"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not pairs_csv.exists():
        raise FileNotFoundError(f"Evaluation pairs not found at {pairs_csv}")

    pairs_df = pd.read_csv(pairs_csv)
    print(f"[*] Loaded {len(pairs_df)} evaluation pairs for benchmarking...")

    tfidf_matcher = get_tfidf_matcher()
    fuzzy_matcher = get_fuzzy_matcher()
    semantic_matcher = get_semantic_matcher()
    hybrid_engine = get_hybrid_engine()

    # Pre-encode unique titles in batch for high-speed evaluation
    unique_titles = list(set(pairs_df["title1"].tolist() + pairs_df["title2"].tolist()))
    print(f"[*] Pre-encoding {len(unique_titles)} distinct titles for semantic matching...")
    semantic_matcher.encode_batch(unique_titles)
    semantic_matcher.save_cache()

    y_true = pairs_df["label"].tolist()

    tfidf_scores = []
    fuzzy_scores = []
    semantic_scores = []
    hybrid_scores = []
    decisions = []

    print("[*] Evaluating pairs across all matching engines...")
    for _, row in pairs_df.iterrows():
        t1, t2 = row["title1"], row["title2"]

        # 1. TF-IDF
        l_res = tfidf_matcher.compute_similarity(t1, t2)
        tfidf_scores.append(l_res["lexical_score"])

        # 2. Fuzzy
        f_res = fuzzy_matcher.compute_similarity(t1, t2)
        fuzzy_scores.append(f_res["fuzzy_score"])

        # 3. Semantic
        s_res = semantic_matcher.compute_similarity(t1, t2)
        semantic_scores.append(s_res["semantic_score"])

        # 4. Hybrid
        h_res = hybrid_engine.compare(t1, t2)
        hybrid_scores.append(h_res["hybrid_score"])
        decisions.append(h_res["match_decision"])

    pairs_df["tfidf_score"] = tfidf_scores
    pairs_df["fuzzy_score"] = fuzzy_scores
    pairs_df["semantic_score"] = semantic_scores
    pairs_df["hybrid_score"] = hybrid_scores
    pairs_df["decision"] = decisions

    # Compute metrics for each model
    pred_tfidf = [1 if s >= threshold else 0 for s in tfidf_scores]
    pred_fuzzy = [1 if s >= threshold else 0 for s in fuzzy_scores]
    pred_semantic = [1 if s >= threshold else 0 for s in semantic_scores]
    # For hybrid, positive prediction corresponds to MATCH decision (or MATCH/REVIEW above threshold)
    pred_hybrid = [1 if s >= threshold and d != "NOT_MATCH" else 0 for s, d in zip(hybrid_scores, decisions)]

    metrics_tfidf = calculate_metrics(y_true, pred_tfidf)
    metrics_fuzzy = calculate_metrics(y_true, pred_fuzzy)
    metrics_semantic = calculate_metrics(y_true, pred_semantic)
    metrics_hybrid = calculate_metrics(y_true, pred_hybrid)

    models_data = {
        "TF-IDF Baseline (Lexical)": metrics_tfidf,
        "RapidFuzz (Fuzzy)": metrics_fuzzy,
        "Sentence Transformer (Semantic)": metrics_semantic,
        "Hybrid Matching Engine (Ensemble)": metrics_hybrid,
    }

    comparison_table = [
        {
            "model": name,
            "precision": m["precision"],
            "recall": m["recall"],
            "f1": m["f1"],
            "accuracy": m["accuracy"],
            "false_positives": m["false_positives"],
            "false_negatives": m["false_negatives"],
            "true_positives": m["true_positives"],
            "true_negatives": m["true_negatives"],
        }
        for name, m in models_data.items()
    ]

    evaluation_payload = {
        "benchmark_dataset": "Kaggle Multimodal Product Matching (Development Benchmark)",
        "disclaimer": "Metrics calculated on controlled benchmark pairs. NOT real CPSE performance.",
        "total_evaluation_pairs": len(pairs_df),
        "positive_pairs": int((pairs_df["label"] == 1).sum()),
        "random_negative_pairs": int((pairs_df["pair_type"] == "random_negative").sum()),
        "hard_negative_pairs": int((pairs_df["pair_type"] == "hard_negative").sum()),
        "threshold_used": threshold,
        "models": models_data,
        "comparison_table": comparison_table,
    }

    # Save outputs
    json_path = output_dir / "evaluation_metrics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_payload, f, indent=2)

    csv_path = output_dir / "evaluation_comparison.csv"
    pd.DataFrame(comparison_table).to_csv(csv_path, index=False)

    scored_pairs_path = output_dir / "scored_evaluation_pairs.csv"
    pairs_df.to_csv(scored_pairs_path, index=False)

    print(f"[+] Evaluation completed and saved to {json_path} and {csv_path}")
    return evaluation_payload


if __name__ == "__main__":
    payload = run_evaluation()
    print("\n" + "=" * 80)
    print("SIH26099 - MODEL BENCHMARK COMPARISON TABLE")
    print("=" * 80)
    print(f"{'Model':<36} | {'Precision':<9} | {'Recall':<6} | {'F1':<6} | {'Accuracy':<8} | {'FP':<5} | {'FN':<5}")
    print("-" * 80)
    for row in payload["comparison_table"]:
        print(
            f"{row['model']:<36} | {row['precision']:<9.4f} | {row['recall']:<6.4f} | "
            f"{row['f1']:<6.4f} | {row['accuracy']:<8.4f} | {row['false_positives']:<5} | {row['false_negatives']:<5}"
        )
    print("=" * 80)
