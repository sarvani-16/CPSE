"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: CPSE Material Master Service
Description: SQLite data layer, CSV/XLSX file ingestion, schema validation, and governance logging.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
import io
import json
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from backend.app.cpse.models import (
    CREATE_TABLES_SQL,
    CPSE_SCHEMA_FIELDS,
    REQUIRED_FIELDS,
    UploadPreviewResponse,
)
from backend.app.cpse.schema_mapper import get_schema_mapper


class CPSEMaterialService:
    """
    Manages the enterprise material master data layer:
    - Ingests CSV/XLSX exports from any CPSE
    - Preserves immutable original material codes and enterprise audit logs
    - Manages canonical materials and cross-enterprise code mappings
    """

    def __init__(self, db_path: Optional[Any] = None):
        self.project_root = PROJECT_ROOT
        self.db_path = Path(db_path) if db_path else (
            self.project_root / "outputs" / "analysis" / "cpse_master.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.schema_mapper = get_schema_mapper()
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """
        Creates the 6 core governance tables if they do not exist.
        """
        with self._get_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)
            conn.commit()

    MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB max
    ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

    def read_tabular_file(self, file_bytes: bytes, filename: str) -> pd.DataFrame:
        """
        Reads CSV or Excel file safely from bytes with security checks:
        - Path traversal prevention (strips directory paths)
        - Extension whitelisting (.csv, .xlsx, .xls)
        - File payload size limits (50 MB)
        """
        # Security: Prevent path traversal
        clean_name = Path(filename).name
        lower_name = clean_name.lower()
        ext = Path(lower_name).suffix

        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format '{ext}'. Only {sorted(self.ALLOWED_EXTENSIONS)} are permitted for catalog ingestion."
            )

        if len(file_bytes) > self.MAX_UPLOAD_SIZE_BYTES:
            raise ValueError(
                f"File size exceeds maximum permitted limit of {self.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB."
            )

        if ext == ".csv":
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")
        elif ext in {".xlsx", ".xls"}:
            df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file format '{clean_name}'.")

        # Strip whitespace from column names
        df.columns = [str(c).strip() for c in df.columns]
        return df

    def preview_upload(
        self,
        file_bytes: bytes,
        filename: str,
        cpse_name: str,
        user_overrides: Optional[Dict[str, str]] = None,
    ) -> UploadPreviewResponse:
        """
        Dry-run file inspection: detects columns, generates mapping plan, and produces first 5 rows preview.
        """
        clean_filename = Path(filename).name
        df = self.read_tabular_file(file_bytes, clean_filename)
        raw_columns = list(df.columns)

        mapping_plan = self.schema_mapper.detect_mappings(
            raw_columns=raw_columns,
            user_overrides=user_overrides,
        )

        # Generate preview with mapped field names
        preview_slice = df.head(5).copy()
        # Clean null values for clean JSON output
        preview_slice = preview_slice.fillna("")

        preview_rows = []
        for _, row in preview_slice.iterrows():
            item_dict = {"_raw_data": dict(row)}
            # Show projected schema fields
            for raw_col, target_field in mapping_plan["suggested_mappings"].items():
                item_dict[target_field] = str(row.get(raw_col, ""))
            item_dict["cpse_name"] = cpse_name
            preview_rows.append(item_dict)

        file_type = "CSV" if clean_filename.lower().endswith(".csv") else "Excel (XLSX)"

        return UploadPreviewResponse(
            filename=clean_filename,
            file_type=file_type,
            total_rows_detected=len(df),
            detected_columns=raw_columns,
            suggested_mappings=mapping_plan["suggested_mappings"],
            unmapped_columns=mapping_plan["unmapped_columns"],
            missing_required_fields=mapping_plan["missing_required_fields"],
            preview_rows=preview_rows,
            is_valid=mapping_plan["is_valid"],
            validation_message=mapping_plan["validation_message"],
        )

    def import_materials(
        self,
        file_bytes: bytes,
        filename: str,
        cpse_name: str,
        confirmed_mappings: Dict[str, str],
        user: str = "ADMIN_PORTAL",
    ) -> Dict[str, Any]:
        """
        Ingests the materials into source_materials adhering to immutable code governance rules.
        """
        df = self.read_tabular_file(file_bytes, filename)

        # Validate that confirmed mappings cover required fields
        mapped_targets = set(confirmed_mappings.values())
        missing_req = [r for r in REQUIRED_FIELDS if r not in mapped_targets]
        if missing_req:
            raise ValueError(
                f"Cannot import: Missing required schema fields: {missing_req}"
            )

        # Inverted mapping: target_field -> source_col
        target_to_source = {target: src for src, target in confirmed_mappings.items()}

        imported_count = 0
        skipped_count = 0
        errors = []

        with self._get_connection() as conn:
            cur = conn.cursor()

            for idx, row in df.iterrows():
                row_num = idx + 1
                try:
                    # Extract required fields
                    code_col = target_to_source["material_code"]
                    desc_col = target_to_source["description"]

                    mat_code = str(row.get(code_col, "")).strip()
                    mat_desc = str(row.get(desc_col, "")).strip()

                    if not mat_code or mat_code.lower() == "nan":
                        skipped_count += 1
                        errors.append(f"Row {row_num}: Missing material code")
                        continue

                    if not mat_desc or mat_desc.lower() == "nan":
                        skipped_count += 1
                        errors.append(f"Row {row_num}: Missing material description")
                        continue

                    # Extract optional fields
                    def get_opt(field_name: str) -> Optional[str]:
                        if field_name in target_to_source:
                            val = row.get(target_to_source[field_name], None)
                            if pd.notna(val) and str(val).strip():
                                return str(val).strip()
                        return None

                    spec = get_opt("specification")
                    m_type = get_opt("material_type")
                    grade = get_opt("material_grade")
                    dim = get_opt("dimensions")
                    uom = get_opt("unit_of_measure")
                    mfg = get_opt("manufacturer")
                    part_no = get_opt("part_number")
                    cat = get_opt("category")

                    # Upsert into source_materials (preserves original CPSE code)
                    cur.execute(
                        """
                        INSERT INTO source_materials (
                            cpse_name, material_code, description, specification,
                            material_type, material_grade, dimensions, unit_of_measure,
                            manufacturer, part_number, category, source_file
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(cpse_name, material_code) DO UPDATE SET
                            description = excluded.description,
                            specification = excluded.specification,
                            material_grade = excluded.material_grade,
                            dimensions = excluded.dimensions,
                            unit_of_measure = excluded.unit_of_measure,
                            manufacturer = excluded.manufacturer,
                            part_number = excluded.part_number,
                            category = excluded.category,
                            source_file = excluded.source_file
                        """,
                        (
                            cpse_name,
                            mat_code,
                            mat_desc,
                            spec,
                            m_type,
                            grade,
                            dim,
                            uom,
                            mfg,
                            part_no,
                            cat,
                            filename,
                        ),
                    )
                    imported_count += 1

                except Exception as e:
                    skipped_count += 1
                    errors.append(f"Row {row_num}: {str(e)}")

        # Log audit trail via AuditService outside active transaction
        from backend.app.cpse.audit_service import get_audit_service
        audit_svc = get_audit_service()
        audit_svc.log_upload(
            filename=filename,
            cpse_name=cpse_name,
            rows_imported=imported_count,
            rows_skipped=skipped_count,
            mappings=confirmed_mappings,
            performed_by=user,
            reason=f"Batch catalog ingestion for {cpse_name} ({imported_count} rows imported, {skipped_count} skipped)",
        )

        # Trigger automatic candidate generation for newly uploaded items
        try:
            from backend.app.cpse.review_service import get_review_service
            get_review_service().generate_reviews(force_refresh=False)
        except Exception:
            pass

        return {
            "status": "success",
            "cpse_name": cpse_name,
            "filename": filename,
            "rows_imported": imported_count,
            "rows_skipped": skipped_count,
            "errors": errors[:10],  # sample first 10 errors
            "imported_at": datetime.now().isoformat(),
        }

    def get_source_materials(
        self,
        cpse_name: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Retrieves paginated CPSE source materials.
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        conditions = []
        params = []

        if cpse_name and cpse_name.strip():
            conditions.append("cpse_name = ?")
            params.append(cpse_name.strip())

        if search and search.strip():
            s = f"%{search.strip().lower()}%"
            conditions.append(
                "(LOWER(material_code) LIKE ? OR LOWER(description) LIKE ? OR LOWER(specification) LIKE ? OR LOWER(material_grade) LIKE ?)"
            )
            params.extend([s, s, s, s])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM source_materials {where_clause}", params)
            total = cur.fetchone()[0]

            query = f"""
                SELECT id, cpse_name, material_code, description, specification,
                       material_type, material_grade, dimensions, unit_of_measure,
                       manufacturer, part_number, category, source_file, created_at
                FROM source_materials
                {where_clause}
                ORDER BY id DESC
                LIMIT ? OFFSET ?
            """
            cur.execute(query, params + [page_size, offset])
            items = [dict(r) for r in cur.fetchall()]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items,
        }

    def get_material_mappings(
        self,
        cpse_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Retrieves data governance mapping audit records.
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        conditions = []
        params = []
        if cpse_name:
            conditions.append("cpse_name = ?")
            params.append(cpse_name)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM material_mappings {where_clause}", params)
            total = cur.fetchone()[0]

            query = f"""
                SELECT id, source_material_id, cpse_name, original_material_code,
                       original_description, canonical_material_code, canonical_description,
                       match_status, confidence, reviewer, timestamp
                FROM material_mappings
                {where_clause}
                ORDER BY id DESC
                LIMIT ? OFFSET ?
            """
            cur.execute(query, params + [page_size, offset])
            items = [dict(r) for r in cur.fetchall()]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        }

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves the latest enterprise data governance audit logs.
        """
        from backend.app.cpse.audit_service import get_audit_service
        return get_audit_service().get_audit_logs(page_size=limit)["items"]


# Singleton service instance
_cpse_service: Optional[CPSEMaterialService] = None


def get_cpse_service() -> CPSEMaterialService:
    global _cpse_service
    if _cpse_service is None:
        _cpse_service = CPSEMaterialService()
    return _cpse_service
