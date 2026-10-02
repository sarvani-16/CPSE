"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Data Analysis (Step 2)
Description: Comprehensive statistical profiling and visualization of dataset/train.csv.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from typing import Dict, Any
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.preprocessing import clean_text

REQUIRED_COLUMNS = ["posting_id", "image", "image_phash", "title", "label_group"]


def load_and_validate_dataset(csv_path: Path) -> pd.DataFrame:
    """
    Safely loads the benchmark CSV and validates structural integrity.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # Validate required columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")

    return df


def generate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes complete statistical profile of the benchmark dataset.
    """
    # Text length & word counts
    title_lengths = df["title"].astype(str).str.len()
    title_words = df["title"].astype(str).str.split().str.len()

    # Group size distribution
    group_counts = df["label_group"].value_counts()

    stats = {
        "dataset_name": "Shopee Multimodal Product Matching (Kaggle Benchmark)",
        "disclaimer": "Benchmark dataset strictly for algorithm development and testing. NOT CPSE data.",
        "number_of_rows": int(len(df)),
        "number_of_columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(count) for col, count in df.isnull().sum().items()},
        "total_missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "unique_posting_ids": int(df["posting_id"].nunique()),
        "unique_label_groups": int(df["label_group"].nunique()),
        "unique_titles": int(df["title"].nunique()),
        "group_size_stats": {
            "min": int(group_counts.min()),
            "max": int(group_counts.max()),
            "mean": round(float(group_counts.mean()), 2),
            "median": float(group_counts.median()),
            "std": round(float(group_counts.std()), 2),
            "groups_with_2_records": int((group_counts == 2).sum()),
            "groups_with_3_plus_records": int((group_counts >= 3).sum()),
            "groups_with_5_plus_records": int((group_counts >= 5).sum()),
            "groups_with_10_plus_records": int((group_counts >= 10).sum()),
        },
        "title_length_stats": {
            "char_min": int(title_lengths.min()),
            "char_max": int(title_lengths.max()),
            "char_mean": round(float(title_lengths.mean()), 2),
            "char_median": float(title_lengths.median()),
            "word_min": int(title_words.min()),
            "word_max": int(title_words.max()),
            "word_mean": round(float(title_words.mean()), 2),
            "word_median": float(title_words.median()),
        },
    }
    return stats


def generate_charts(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Generates 3 matplotlib charts in outputs/analysis/ without seaborn.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    group_counts = df["label_group"].value_counts()
    title_lengths = df["title"].astype(str).str.len()

    # Chart 1: Group Size Distribution
    plt.figure(figsize=(9, 5))
    bins = [2, 3, 5, 10, 20, 55]
    labels = ["2 items", "3-4 items", "5-9 items", "10-19 items", "20+ items"]
    cats = pd.cut(group_counts, bins=bins, labels=labels, right=False)
    cat_counts = cats.value_counts(sort=False)

    bars = plt.bar(labels, cat_counts.values, color="#1E3A8A", edgecolor="#0F172A", width=0.55)
    plt.title("Distribution of Records per Product Group (label_group)\n[Development Benchmark Dataset]", fontsize=12, pad=15)
    plt.xlabel("Group Size Category", fontsize=10, labelpad=10)
    plt.ylabel("Number of Distinct Groups", fontsize=10)
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for bar in bars:
        h = bar.get_height()
        pct = (h / len(group_counts)) * 100
        plt.text(bar.get_x() + bar.get_width() / 2, h + 50, f"{h:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=8)

    plt.ylim(0, max(cat_counts.values) * 1.15)
    plt.tight_layout()
    chart1_path = output_dir / "label_group_distribution.png"
    plt.savefig(chart1_path, dpi=200)
    plt.close()
    print(f"[+] Saved chart: {chart1_path}")

    # Chart 2: Title Character Length Distribution
    plt.figure(figsize=(9, 5))
    plt.hist(title_lengths, bins=40, color="#0D9488", edgecolor="#134E4A", alpha=0.85)
    plt.axvline(title_lengths.mean(), color="#DC2626", linestyle="dashed", linewidth=1.5, label=f"Mean: {title_lengths.mean():.1f} chars")
    plt.axvline(title_lengths.median(), color="#F59E0B", linestyle="dotted", linewidth=1.5, label=f"Median: {title_lengths.median():.0f} chars")
    plt.title("Title Character Length Distribution\n[Development Benchmark Dataset]", fontsize=12, pad=15)
    plt.xlabel("Title Character Length", fontsize=10, labelpad=10)
    plt.ylabel("Frequency", fontsize=10)
    plt.legend(frameon=True)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    chart2_path = output_dir / "title_length_distribution.png"
    plt.savefig(chart2_path, dpi=200)
    plt.close()
    print(f"[+] Saved chart: {chart2_path}")

    # Chart 3: Top 10 Repeated Titles
    plt.figure(figsize=(10, 6))
    top_repeated = df["title"].value_counts().head(10)
    shortened_labels = [t[:45] + "..." if len(t) > 45 else t for t in top_repeated.index]
    y_pos = np.arange(len(top_repeated))

    bars = plt.barh(y_pos, top_repeated.values, color="#4F46E5", edgecolor="#312E81", height=0.6)
    plt.yticks(y_pos, shortened_labels, fontsize=9)
    plt.gca().invert_yaxis()
    plt.title("Top 10 Repeated Exact Product Titles\n[Development Benchmark Dataset]", fontsize=12, pad=15)
    plt.xlabel("Occurrences Count", fontsize=10, labelpad=10)
    plt.grid(axis="x", linestyle="--", alpha=0.6)

    for bar in bars:
        w = bar.get_width()
        plt.text(w + 0.1, bar.get_y() + bar.get_height() / 2, f"{int(w)}", va="center", ha="left", fontsize=9, fontweight="bold")

    plt.xlim(0, max(top_repeated.values) + 1.5)
    plt.tight_layout()
    chart3_path = output_dir / "top_repeated_titles.png"
    plt.savefig(chart3_path, dpi=200)
    plt.close()
    print(f"[+] Saved chart: {chart3_path}")


def save_samples_and_reports(df: pd.DataFrame, stats: Dict[str, Any], output_dir: Path) -> None:
    """
    Saves analysis_summary.json and sample group comparisons to outputs/analysis/.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save summary JSON
    summary_path = output_dir / "analysis_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"[+] Saved summary JSON: {summary_path}")

    # 2. Extract 20 example product groups with multiple records
    group_sizes = df["label_group"].value_counts()
    multi_item_groups = group_sizes[group_counts_filter := (group_sizes >= 2)].index[:20]

    sample_groups_df = df[df["label_group"].isin(multi_item_groups)][
        ["label_group", "posting_id", "title"]
    ].copy()
    sample_groups_df["clean_title"] = sample_groups_df["title"].apply(clean_text)

    samples_path = output_dir / "group_samples.csv"
    sample_groups_df.to_csv(samples_path, index=False)
    print(f"[+] Saved group samples CSV: {samples_path}")


def print_analysis_report(stats: Dict[str, Any], df: pd.DataFrame) -> None:
    """
    Prints structured terminal report matching Step 2 specification.
    """
    print("\n" + "=" * 75)
    print("SIH26099 - STEP 2: DATASET INGESTION & STATISTICAL ANALYSIS REPORT")
    print("=" * 75)
    print(f"NOTICE: {stats['disclaimer']}")
    print("-" * 75)

    print("\n1. OVERVIEW & INTEGRITY:")
    print(f"   * Total Records (Rows)   : {stats['number_of_rows']:,}")
    print(f"   * Number of Columns      : {stats['number_of_columns']}")
    print(f"   * Column Names           : {', '.join(stats['column_names'])}")
    print(f"   * Data Types             : {stats['data_types']}")
    print(f"   * Total Missing Values   : {stats['total_missing_values']}")
    print(f"   * Duplicate Rows         : {stats['duplicate_rows']}")
    print(f"   * Unique Posting IDs     : {stats['unique_posting_ids']:,}")
    print(f"   * Unique Label Groups    : {stats['unique_label_groups']:,}")
    print(f"   * Unique Titles          : {stats['unique_titles']:,}")

    print("\n2. GROUP SIZE DISTRIBUTION (label_group):")
    g = stats["group_size_stats"]
    print(f"   * Minimum Group Size     : {g['min']}")
    print(f"   * Maximum Group Size     : {g['max']}")
    print(f"   * Average Group Size     : {g['mean']}")
    print(f"   * Median Group Size      : {g['median']}")
    print(f"   * Groups with 2 records  : {g['groups_with_2_records']:,} ({(g['groups_with_2_records']/stats['unique_label_groups'])*100:.1f}%)")
    print(f"   * Groups with 3+ records : {g['groups_with_3_plus_records']:,} ({(g['groups_with_3_plus_records']/stats['unique_label_groups'])*100:.1f}%)")
    print(f"   * Groups with 5+ records : {g['groups_with_5_plus_records']:,} ({(g['groups_with_5_plus_records']/stats['unique_label_groups'])*100:.1f}%)")
    print(f"   * Groups with 10+ records: {g['groups_with_10_plus_records']:,} ({(g['groups_with_10_plus_records']/stats['unique_label_groups'])*100:.1f}%)")

    print("\n3. TITLE TEXT STATISTICS:")
    t = stats["title_length_stats"]
    print(f"   * Character Length       : Min={t['char_min']}, Max={t['char_max']}, Mean={t['char_mean']}, Median={t['char_median']}")
    print(f"   * Word Count             : Min={t['word_min']}, Max={t['word_max']}, Mean={t['word_mean']}, Median={t['word_median']}")

    print("\n4. 20 SAMPLE ROWS FROM DATASET:")
    print("-" * 75)
    sample_display = df[["posting_id", "title", "label_group"]].head(20)
    for idx, row in sample_display.iterrows():
        print(f"   [{row['posting_id']}] Group {row['label_group']}: {row['title'][:70]}")

    print("\n5. 5 SAMPLE PRODUCT GROUPS (SHOWING MATCHING VARIANTS):")
    print("-" * 75)
    sample_group_ids = df["label_group"].value_counts()[lambda x: (x >= 2) & (x <= 4)].index[:5]
    for gid in sample_group_ids:
        group_items = df[df["label_group"] == gid]["title"].tolist()
        print(f"   * Group ID [{gid}] ({len(group_items)} items):")
        for item in group_items:
            print(f"       -> {item}")
    print("=" * 75 + "\n")


def run_analysis(csv_path: Path = None, output_dir: Path = None) -> Dict[str, Any]:
    """
    Main orchestration entry point for dataset analysis.
    """
    project_root = Path(__file__).resolve().parent.parent
    if csv_path is None:
        csv_path = project_root / "dataset" / "train.csv"
    if output_dir is None:
        output_dir = project_root / "outputs" / "analysis"

    df = load_and_validate_dataset(csv_path)
    stats = generate_statistics(df)
    generate_charts(df, output_dir)
    save_samples_and_reports(df, stats, output_dir)
    print_analysis_report(stats, df)
    return stats


if __name__ == "__main__":
    run_analysis()
