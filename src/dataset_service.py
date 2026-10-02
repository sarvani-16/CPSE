"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Dataset Service
Description: Ingestion, SQLite persistence, querying, and statistics calculation for the benchmark dataset.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
import json
import sqlite3
from typing import Dict, Any, List, Optional
import pandas as pd

from src.preprocessing import clean_text

REQUIRED_COLUMNS = ["posting_id", "image", "image_phash", "title", "label_group"]


class DatasetService:
    """
    Manages loading, validating, indexing, and querying the benchmark dataset.
    Backed by SQLite for high-speed indexed search and pagination.
    """

    def __init__(
        self,
        csv_path: Optional[Path] = None,
        db_path: Optional[Path] = None,
    ):
        self.project_root = Path(__file__).resolve().parent.parent
        self.csv_path = csv_path or (self.project_root / "dataset" / "train.csv")
        self.db_path = db_path or (self.project_root / "outputs" / "analysis" / "materials.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._summary_cache: Optional[Dict[str, Any]] = None
        self._is_loaded = False
        self._last_loaded_at: Optional[str] = None

        # Automatically ensure database is ready
        self.ensure_initialized()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_initialized(self, force_reload: bool = False) -> None:
        """
        Initializes the SQLite database from CSV if it does not already exist.
        """
        if not force_reload and self.db_path.exists():
            try:
                with self._get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM materials")
                    row_count = cur.fetchone()[0]
                    if row_count > 0:
                        self._is_loaded = True
                        self._last_loaded_at = datetime.now().isoformat()
                        return
            except Exception:
                # Corrupted or incomplete table, reload
                pass

        self.ingest_csv()

    def ingest_csv(self) -> Dict[str, Any]:
        """
        Safely loads train.csv, validates columns, cleans titles, and saves into SQLite.
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Benchmark dataset not found at: {self.csv_path}")

        print(f"[*] Ingesting dataset from: {self.csv_path}")
        df = pd.read_csv(self.csv_path)

        # 1. Column validation
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"train.csv is missing required columns: {missing}")

        # 2. Missing values handling
        null_counts = df[REQUIRED_COLUMNS].isnull().sum().to_dict()
        df["title"] = df["title"].fillna("")
        df["image"] = df["image"].fillna("")
        df["image_phash"] = df["image_phash"].fillna("")

        # 3. Clean titles and calculate metrics
        df["clean_title"] = df["title"].apply(clean_text)
        df["title_length"] = df["title"].str.len()

        # Group sizes
        group_counts = df["label_group"].value_counts()
        df["group_size"] = df["label_group"].map(group_counts)

        # 4. Save to SQLite
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS materials")
            cur.execute("DROP TABLE IF EXISTS dataset_meta")

            cur.execute(
                """
                CREATE TABLE materials (
                    posting_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    clean_title TEXT NOT NULL,
                    label_group INTEGER NOT NULL,
                    group_size INTEGER NOT NULL,
                    image TEXT,
                    image_phash TEXT,
                    title_length INTEGER NOT NULL
                )
                """
            )

            # Insert batch converting all pandas/numpy types to native python objects
            insert_cols = [
                "posting_id",
                "title",
                "clean_title",
                "label_group",
                "group_size",
                "image",
                "image_phash",
                "title_length",
            ]
            records = [
                (
                    str(r.posting_id),
                    str(r.title),
                    str(r.clean_title),
                    int(r.label_group),
                    int(r.group_size),
                    str(r.image),
                    str(r.image_phash),
                    int(r.title_length),
                )
                for r in df[insert_cols].itertuples(index=False)
            ]

            cur.executemany(
                """
                INSERT INTO materials (
                    posting_id, title, clean_title, label_group,
                    group_size, image, image_phash, title_length
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                records,
            )

            # Create indices for fast filtering and search
            cur.execute("CREATE INDEX idx_materials_label_group ON materials(label_group)")
            cur.execute("CREATE INDEX idx_materials_clean_title ON materials(clean_title)")
            cur.execute("CREATE INDEX idx_materials_title ON materials(title)")

            # Compute and persist summary
            total_records = len(df)
            total_groups = int(df["label_group"].nunique())
            unique_titles = int(df["title"].nunique())
            total_missing = int(sum(null_counts.values()))
            duplicate_records = int(df.duplicated(subset=["posting_id"]).sum())
            avg_title_len = round(float(df["title_length"].mean()), 2)
            min_group_size = int(group_counts.min())
            max_group_size = int(group_counts.max())
            median_group_size = float(group_counts.median())

            summary_dict = {
                "total_records": total_records,
                "total_groups": total_groups,
                "unique_titles": unique_titles,
                "missing_values": total_missing,
                "duplicate_records": duplicate_records,
                "average_title_length": avg_title_len,
                "minimum_group_size": min_group_size,
                "maximum_group_size": max_group_size,
                "median_group_size": median_group_size,
                "groups_size_2": int((group_counts == 2).sum()),
                "groups_size_3_plus": int((group_counts >= 3).sum()),
                "groups_size_5_plus": int((group_counts >= 5).sum()),
                "groups_size_10_plus": int((group_counts >= 10).sum()),
            }

            cur.execute("CREATE TABLE dataset_meta (key TEXT PRIMARY KEY, value TEXT)")
            for k, v in summary_dict.items():
                cur.execute("INSERT INTO dataset_meta VALUES (?, ?)", (k, json.dumps(v)))

            conn.commit()

        self._summary_cache = summary_dict
        self._is_loaded = True
        self._last_loaded_at = datetime.now().isoformat()
        print(f"[+] Successfully loaded {total_records:,} records into SQLite database.")
        return summary_dict

    def get_status(self) -> Dict[str, Any]:
        """
        Returns dataset load status and metadata disclaimer.
        """
        return {
            "loaded": self._is_loaded,
            "dataset_path": str(self.csv_path.name),
            "database_path": str(self.db_path.name),
            "is_benchmark": True,
            "dataset_label": "Development Benchmark Dataset (Kaggle Multimodal Product Matching)",
            "disclaimer": "Development & Benchmarking Dataset only. NOT real CPSE data.",
            "total_records": self.get_summary()["total_records"] if self._is_loaded else 0,
            "last_loaded_at": self._last_loaded_at,
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        Returns aggregated dataset summary statistics.
        """
        if self._summary_cache is not None:
            return self._summary_cache

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM dataset_meta")
            rows = cur.fetchall()
            if rows:
                self._summary_cache = {row["key"]: json.loads(row["value"]) for row in rows}
                return self._summary_cache

        # If cache empty, re-ingest
        return self.ingest_csv()

    def get_preview(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str = "",
    ) -> Dict[str, Any]:
        """
        Returns paginated, searchable preview of materials.
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        search_term = search.strip().lower()

        with self._get_connection() as conn:
            cur = conn.cursor()

            if search_term:
                param = f"%{search_term}%"
                count_query = """
                    SELECT COUNT(*) FROM materials
                    WHERE clean_title LIKE ? OR title LIKE ? OR posting_id LIKE ? OR CAST(label_group AS TEXT) LIKE ?
                """
                cur.execute(count_query, (param, param, param, param))
                total_records = cur.fetchone()[0]

                data_query = """
                    SELECT posting_id, title, clean_title, label_group, group_size, image, image_phash, title_length
                    FROM materials
                    WHERE clean_title LIKE ? OR title LIKE ? OR posting_id LIKE ? OR CAST(label_group AS TEXT) LIKE ?
                    ORDER BY label_group ASC, posting_id ASC
                    LIMIT ? OFFSET ?
                """
                cur.execute(data_query, (param, param, param, param, page_size, offset))
            else:
                cur.execute("SELECT COUNT(*) FROM materials")
                total_records = cur.fetchone()[0]

                data_query = """
                    SELECT posting_id, title, clean_title, label_group, group_size, image, image_phash, title_length
                    FROM materials
                    ORDER BY label_group ASC, posting_id ASC
                    LIMIT ? OFFSET ?
                """
                cur.execute(data_query, (page_size, offset))

            rows = cur.fetchall()
            items = [dict(row) for row in rows]

        total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1

        return {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages,
            "search": search_term,
            "items": items,
        }

    def get_groups(self) -> Dict[str, Any]:
        """
        Returns distribution of group sizes and top 10 largest product groups.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()

            # Distribution categories
            cur.execute(
                """
                SELECT
                    SUM(CASE WHEN group_size = 2 THEN 1 ELSE 0 END) AS size_2,
                    SUM(CASE WHEN group_size BETWEEN 3 AND 4 THEN 1 ELSE 0 END) AS size_3_4,
                    SUM(CASE WHEN group_size BETWEEN 5 AND 9 THEN 1 ELSE 0 END) AS size_5_9,
                    SUM(CASE WHEN group_size >= 10 THEN 1 ELSE 0 END) AS size_10_plus
                FROM (SELECT label_group, group_size FROM materials GROUP BY label_group)
                """
            )
            cat_row = cur.fetchone()
            s2 = cat_row["size_2"] or 0
            s34 = cat_row["size_3_4"] or 0
            s59 = cat_row["size_5_9"] or 0
            s10p = cat_row["size_10_plus"] or 0
            total_unique_groups = s2 + s34 + s59 + s10p

            distribution = [
                {
                    "category": "2 items",
                    "count": s2,
                    "percentage": round((s2 / total_unique_groups * 100), 2) if total_unique_groups else 0,
                    "color": "#3B82F6",
                },
                {
                    "category": "3-4 items",
                    "count": s34,
                    "percentage": round((s34 / total_unique_groups * 100), 2) if total_unique_groups else 0,
                    "color": "#10B981",
                },
                {
                    "category": "5-9 items",
                    "count": s59,
                    "percentage": round((s59 / total_unique_groups * 100), 2) if total_unique_groups else 0,
                    "color": "#F59E0B",
                },
                {
                    "category": "10+ items",
                    "count": s10p,
                    "percentage": round((s10p / total_unique_groups * 100), 2) if total_unique_groups else 0,
                    "color": "#8B5CF6",
                },
            ]

            # Top 10 largest groups
            cur.execute(
                """
                SELECT label_group, group_size, MIN(title) AS sample_title
                FROM materials
                GROUP BY label_group
                ORDER BY group_size DESC, label_group ASC
                LIMIT 10
                """
            )
            top_groups = [dict(row) for row in cur.fetchall()]

        return {
            "total_groups": total_unique_groups,
            "distribution": distribution,
            "top_groups": top_groups,
        }


# Singleton service instance
service_instance: Optional[DatasetService] = None


def get_dataset_service() -> DatasetService:
    global service_instance
    if service_instance is None:
        service_instance = DatasetService()
    return service_instance


if __name__ == "__main__":
    service = get_dataset_service()
    print("\n--- STATUS ---")
    print(json.dumps(service.get_status(), indent=2))
    print("\n--- SUMMARY ---")
    print(json.dumps(service.get_summary(), indent=2))
    print("\n--- PREVIEW (First 2 items) ---")
    print(json.dumps(service.get_preview(page=1, page_size=2), indent=2))
    print("\n--- GROUPS ---")
    print(json.dumps(service.get_groups(), indent=2))
