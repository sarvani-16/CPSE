"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Pair Generator (Stage 5)
Description: Efficient generation of controlled evaluation pairs: positives, random negatives, and hard negatives.
"""

from collections import defaultdict
from pathlib import Path
import random
from typing import Tuple
import pandas as pd
from rapidfuzz import fuzz


def generate_evaluation_pairs(
    csv_path: Path,
    output_path: Path,
    n_positive: int = 500,
    n_random_negative: int = 250,
    n_hard_negative: int = 250,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Generates balanced, controlled evaluation dataset avoiding Cartesian explosion:
    - Positives: pairs from the same label_group (label = 1)
    - Random Negatives: pairs from different label_group (label = 0)
    - Hard Negatives: pairs from different label_group with high token/lexical overlap (label = 0)
    """
    random.seed(random_seed)
    df = pd.read_csv(csv_path)

    pairs = []
    seen_pairs = set()

    # 1. Positive Pairs
    groups = df.groupby("label_group")
    multi_item_groups = [g for _, g in groups if len(g) >= 2]
    sampled_pos_groups = random.sample(
        multi_item_groups, min(n_positive, len(multi_item_groups))
    )

    for g in sampled_pos_groups:
        sampled_rows = g.sample(2, random_state=random_seed)
        r1, r2 = sampled_rows.iloc[0], sampled_rows.iloc[1]
        pair_key = tuple(sorted([r1["posting_id"], r2["posting_id"]]))
        if pair_key not in seen_pairs:
            seen_pairs.add(pair_key)
            pairs.append(
                {
                    "id1": r1["posting_id"],
                    "id2": r2["posting_id"],
                    "title1": r1["title"],
                    "title2": r2["title"],
                    "label_group1": int(r1["label_group"]),
                    "label_group2": int(r2["label_group"]),
                    "label": 1,
                    "pair_type": "positive",
                }
            )

    # 2. Hard Negative Pairs (High lexical overlap, different label_group)
    word_to_indices = defaultdict(list)
    for idx, title in enumerate(df["title"].astype(str).str.lower()):
        tokens = set(w for w in title.split() if len(w) >= 4)
        for tok in tokens:
            if len(word_to_indices[tok]) < 100:
                word_to_indices[tok].append(idx)

    hard_negs_count = 0
    words_list = list(word_to_indices.keys())
    random.shuffle(words_list)

    for word in words_list:
        indices = word_to_indices[word]
        if len(indices) < 2:
            continue
        for i in range(min(12, len(indices))):
            idx1 = indices[i]
            for j in range(i + 1, min(12, len(indices))):
                idx2 = indices[j]
                r1 = df.iloc[idx1]
                r2 = df.iloc[idx2]

                if r1["label_group"] != r2["label_group"]:
                    pair_key = tuple(sorted([r1["posting_id"], r2["posting_id"]]))
                    if pair_key not in seen_pairs:
                        # Check lexical similarity
                        score = fuzz.token_sort_ratio(r1["title"], r2["title"])
                        if 40 <= score <= 92:
                            seen_pairs.add(pair_key)
                            pairs.append(
                                {
                                    "id1": r1["posting_id"],
                                    "id2": r2["posting_id"],
                                    "title1": r1["title"],
                                    "title2": r2["title"],
                                    "label_group1": int(r1["label_group"]),
                                    "label_group2": int(r2["label_group"]),
                                    "label": 0,
                                    "pair_type": "hard_negative",
                                }
                            )
                            hard_negs_count += 1
                if hard_negs_count >= n_hard_negative:
                    break
            if hard_negs_count >= n_hard_negative:
                break
        if hard_negs_count >= n_hard_negative:
            break

    # 3. Random Negative Pairs (Different label_group)
    rand_negs_count = 0
    total_rows = len(df)
    while rand_negs_count < n_random_negative:
        idx1 = random.randint(0, total_rows - 1)
        idx2 = random.randint(0, total_rows - 1)
        if idx1 == idx2:
            continue
        r1 = df.iloc[idx1]
        r2 = df.iloc[idx2]
        if r1["label_group"] != r2["label_group"]:
            pair_key = tuple(sorted([r1["posting_id"], r2["posting_id"]]))
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                pairs.append(
                    {
                        "id1": r1["posting_id"],
                        "id2": r2["posting_id"],
                        "title1": r1["title"],
                        "title2": r2["title"],
                        "label_group1": int(r1["label_group"]),
                        "label_group2": int(r2["label_group"]),
                        "label": 0,
                        "pair_type": "random_negative",
                    }
                )
                rand_negs_count += 1

    pairs_df = pd.DataFrame(pairs)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pairs_df.to_csv(output_path, index=False)
    print(f"[+] Saved {len(pairs_df)} controlled pairs to {output_path}")
    print(f"    - Positive pairs:        {(pairs_df['label'] == 1).sum()}")
    print(f"    - Random negative pairs: {(pairs_df['pair_type'] == 'random_negative').sum()}")
    print(f"    - Hard negative pairs:   {(pairs_df['pair_type'] == 'hard_negative').sum()}")

    return pairs_df


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent.parent
    csv_file = root / "dataset" / "train.csv"
    out_file = root / "outputs" / "analysis" / "matching_pairs.csv"
    generate_evaluation_pairs(csv_file, out_file)
