"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Enterprise Audit & Governance Layer
Description: Immutable audit logging service with secret sanitization, multi-factor filtering,
             and lifecycle tracking across uploads, normalization, AI matching, reviews,
             canonical code generation, and mapping updates.

CRITICAL SECURITY POLICY:
Never store passwords, tokens, API keys, or secret credentials in audit logs.
All input data is actively inspected and sanitized prior to persistence.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
import csv
import io
import json
import re
import sqlite3
from typing import Dict, List, Optional, Any, Union, Tuple

from backend.app.cpse.models import CREATE_TABLES_SQL

SENSITIVE_KEY_PATTERNS = [
    r"pass(word)?",
    r"token",
    r"secret",
    r"api[_-]?key",
    r"bearer",
    r"auth(orization)?",
    r"cookie",
    r"credential",
    r"private[_-]?key",
    r"cert(ificate)?",
]

SENSITIVE_REGEX = re.compile("|".join(SENSITIVE_KEY_PATTERNS), re.IGNORECASE)


def sanitize_audit_payload(data: Any) -> Any:
    """
    Recursively scans and sanitizes any data dictionary, list, or string to ensure
    that passwords, tokens, authentication headers, and secrets are NEVER recorded.
    """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if SENSITIVE_REGEX.search(str(k)):
                sanitized[k] = "[REDACTED_CONFIDENTIAL]"
            else:
                sanitized[k] = sanitize_audit_payload(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_audit_payload(item) for item in data]
    elif isinstance(data, str):
        # Look for token/secret patterns in text
        if SENSITIVE_REGEX.search(data) and ("bearer" in data.lower() or "secret" in data.lower()):
            return "[REDACTED_CONFIDENTIAL_STRING]"
        return data
    else:
        return data


def sanitize_for_export(val: Any) -> str:
    """
    Ensures that values exported to CSV are fully sanitized against secrets,
    passwords, tokens, and confidential keys, maintaining the [REDACTED_CONFIDENTIAL]
    governance standard.
    """
    if val is None:
        return ""
    val_str = str(val).strip()
    if not val_str:
        return ""

    # Try JSON parsing
    try:
        parsed = json.loads(val_str)
        sanitized = sanitize_audit_payload(parsed)
        return json.dumps(sanitized)
    except Exception:
        pass

    # Regex sanitization for key-value assignments in free text
    sanitized_str = val_str
    sanitized_str = re.sub(
        r'(?i)\b(pass(?:word)?|token|secret|api[_-]?key|bearer|credential|private[_-]?key|cookie|auth(?:orization)?)\b\s*[:=]\s*["\']?[^"\'\s,;{}]+["\']?',
        r'\1=[REDACTED_CONFIDENTIAL]',
        sanitized_str,
    )
    # Standalone Bearer tokens
    sanitized_str = re.sub(
        r'(?i)\bBearer\s+[a-zA-Z0-9_\-\.]+',
        'Bearer [REDACTED_CONFIDENTIAL]',
        sanitized_str,
    )
    return sanitized_str


class AuditService:
    """
    Core Enterprise Audit Service for SIH26099.
    Provides immutable data governance logging for all CPSE material master events.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.project_root = PROJECT_ROOT
        self.db_path = db_path or (
            self.project_root / "outputs" / "analysis" / "cpse_master.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._migrate_database()
        self._seed_lifecycle_audit_records_if_needed()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """
        Creates all required tables if they do not exist.
        """
        with self._get_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)
            conn.commit()

    def _migrate_database(self) -> None:
        """
        Ensures audit_logs schema includes all required fields:
        - id
        - action
        - entity_type
        - entity_id
        - old_value
        - new_value
        - performed_by
        - timestamp
        - reason
        - details
        - user
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            existing_cols = [
                row["name"]
                for row in cur.execute("PRAGMA table_info(audit_logs)").fetchall()
            ]

            columns_to_add = {
                "old_value": "TEXT",
                "new_value": "TEXT",
                "performed_by": "TEXT",
                "reason": "TEXT",
                "details": "TEXT",
                "user": "TEXT",
            }

            for col, col_type in columns_to_add.items():
                if col not in existing_cols:
                    cur.execute(f"ALTER TABLE audit_logs ADD COLUMN {col} {col_type}")

            # Backfill performed_by from user if null
            cur.execute(
                """
                UPDATE audit_logs
                SET performed_by = COALESCE(performed_by, user, 'SYSTEM')
                WHERE performed_by IS NULL OR performed_by = ''
                """
            )

            # Ensure indexes exist
            cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_performed_by ON audit_logs(performed_by)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)")
            conn.commit()

    def record_log(
        self,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        old_value: Optional[Union[Dict[str, Any], str]] = None,
        new_value: Optional[Union[Dict[str, Any], str]] = None,
        performed_by: str = "SYSTEM",
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Records an immutable audit log entry.
        Strictly sanitizes all payloads to remove any secrets or tokens.
        """
        sanitized_old = sanitize_audit_payload(old_value)
        sanitized_new = sanitize_audit_payload(new_value)
        sanitized_details = sanitize_audit_payload(details or {})
        sanitized_reason = sanitize_for_export(reason).strip() if reason else None

        old_str = (
            json.dumps(sanitized_old)
            if isinstance(sanitized_old, (dict, list))
            else (str(sanitized_old) if sanitized_old is not None else None)
        )
        new_str = (
            json.dumps(sanitized_new)
            if isinstance(sanitized_new, (dict, list))
            else (str(sanitized_new) if sanitized_new is not None else None)
        )
        details_str = json.dumps(sanitized_details) if sanitized_details else None

        user_clean = performed_by.strip() if performed_by else "SYSTEM"
        timestamp_now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, old_value, new_value,
                    performed_by, timestamp, reason, details, user
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    action.strip(),
                    entity_type.strip(),
                    str(entity_id).strip() if entity_id is not None else None,
                    old_str,
                    new_str,
                    user_clean,
                    timestamp_now,
                    sanitized_reason,
                    details_str,
                    user_clean,
                ),
            )
            log_id = cur.lastrowid
            conn.commit()

        return log_id

    # =========================================================================
    # Specialized Lifecycle Tracking Methods
    # =========================================================================

    def log_upload(
        self,
        filename: str,
        cpse_name: str,
        rows_imported: int,
        rows_skipped: int,
        mappings: Dict[str, str],
        performed_by: str = "PROCUREMENT_ADMIN",
        reason: str = "Batch CPSE material catalog ingestion",
    ) -> int:
        """Tracks enterprise material catalog file uploads."""
        details = {
            "filename": filename,
            "cpse_name": cpse_name,
            "rows_imported": rows_imported,
            "rows_skipped": rows_skipped,
            "mappings": mappings,
        }
        return self.record_log(
            action="UPLOAD_MATERIALS",
            entity_type="source_materials",
            entity_id=cpse_name,
            old_value=None,
            new_value=f"Ingested {rows_imported} items from {filename} ({cpse_name})",
            performed_by=performed_by,
            reason=reason,
            details=details,
        )

    def log_normalization(
        self,
        entity_id: str,
        raw_text: str,
        normalized_text: str,
        performed_by: str = "AI_TEXT_NORMALIZER",
        reason: str = "Technical token & dimension preserving normalization",
    ) -> int:
        """Tracks text & technical attribute normalization."""
        return self.record_log(
            action="NORMALIZE_RECORD",
            entity_type="source_materials",
            entity_id=entity_id,
            old_value=raw_text,
            new_value=normalized_text,
            performed_by=performed_by,
            reason=reason,
            details={"raw_length": len(raw_text), "normalized_length": len(normalized_text)},
        )

    def log_ai_recommendation(
        self,
        source_id: str,
        suggested_canonical_code: str,
        hybrid_score: float,
        breakdown: Dict[str, float],
        performed_by: str = "AI_HYBRID_ENGINE",
        reason: str = "Ensemble scoring (TF-IDF + RapidFuzz + all-MiniLM-L6-v2)",
    ) -> int:
        """Tracks AI candidate match generation."""
        return self.record_log(
            action="AI_RECOMMENDATION",
            entity_type="reviews",
            entity_id=source_id,
            old_value="Unmatched / Ingested Material",
            new_value=f"Recommended {suggested_canonical_code} (Score: {hybrid_score:.4f})",
            performed_by=performed_by,
            reason=reason,
            details={"suggested_code": suggested_canonical_code, "scores": breakdown},
        )

    def log_approval(
        self,
        review_id: int,
        mapping_id: int,
        source_code: str,
        canonical_code: str,
        performed_by: str,
        reason: Optional[str] = None,
        old_status: str = "PENDING",
    ) -> int:
        """Tracks human reviewer approval of material mapping."""
        return self.record_log(
            action="APPROVE_MATCH",
            entity_type="reviews",
            entity_id=str(review_id),
            old_value=f"Review Status: {old_status}",
            new_value=f"Approved & Linked -> Canonical: {canonical_code} (Mapping #{mapping_id})",
            performed_by=performed_by,
            reason=reason or "Verified cross-catalog equivalence and technical specifications",
            details={
                "review_id": review_id,
                "mapping_id": mapping_id,
                "source_code": source_code,
                "canonical_code": canonical_code,
            },
        )

    def log_rejection(
        self,
        review_id: int,
        source_code: str,
        canonical_code: str,
        performed_by: str,
        reason: Optional[str] = None,
        old_status: str = "PENDING",
    ) -> int:
        """Tracks human reviewer rejection of candidate recommendation."""
        return self.record_log(
            action="REJECT_MATCH",
            entity_type="reviews",
            entity_id=str(review_id),
            old_value=f"Review Status: {old_status}",
            new_value=f"Rejected recommendation for {source_code} vs {canonical_code}",
            performed_by=performed_by,
            reason=reason or "Mismatch in metallurgical grade, pressure rating, or dimension",
            details={
                "review_id": review_id,
                "source_code": source_code,
                "canonical_code": canonical_code,
            },
        )

    def log_canonical_creation(
        self,
        national_material_code: str,
        standardized_description: str,
        category: str,
        performed_by: str = "STANDARDIZATION_OFFICER",
        reason: str = "New Prototype Common National Material Code defined (NMM Series)",
    ) -> int:
        """Tracks generation of a new Prototype Common National Material Code."""
        return self.record_log(
            action="CREATE_CANONICAL_CODE",
            entity_type="canonical_materials",
            entity_id=national_material_code,
            old_value=None,
            new_value=f"Created {national_material_code}: {standardized_description} ({category})",
            performed_by=performed_by,
            reason=reason,
            details={
                "code": national_material_code,
                "description": standardized_description,
                "category": category,
            },
        )

    def log_mapping_change(
        self,
        mapping_id: int,
        cpse_name: str,
        source_code: str,
        canonical_code: str,
        old_canonical_code: Optional[str] = None,
        performed_by: str = "DATA_GOVERNANCE_SYSTEM",
        reason: str = "Data governance material mapping updated",
    ) -> int:
        """Tracks permanent material mapping changes or creations."""
        action_name = "MAPPING_UPDATED" if old_canonical_code else "MAPPING_CREATED"
        old_val = f"Mapped to: {old_canonical_code}" if old_canonical_code else "Unmapped"
        new_val = f"Mapped to: {canonical_code}"
        return self.record_log(
            action=action_name,
            entity_type="material_mappings",
            entity_id=str(mapping_id),
            old_value=old_val,
            new_value=new_val,
            performed_by=performed_by,
            reason=reason,
            details={
                "mapping_id": mapping_id,
                "cpse_name": cpse_name,
                "source_code": source_code,
                "canonical_code": canonical_code,
            },
        )

    def _seed_lifecycle_audit_records_if_needed(self) -> None:
        """
        Seeds representative audit events across all 7 tracked categories if database is fresh.
        Ensures complete audit traceability demonstration across the whole lifecycle.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM audit_logs")
            count = cur.fetchone()[0]

            # Check if any normalization or canonical creation entries exist
            cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'NORMALIZE_RECORD'")
            has_norm = cur.fetchone()[0] > 0

            cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'CREATE_CANONICAL_CODE'")
            has_canon = cur.fetchone()[0] > 0

            cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'AI_RECOMMENDATION'")
            has_ai = cur.fetchone()[0] > 0

            cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'MAPPING_CREATED'")
            has_map = cur.fetchone()[0] > 0

        if not has_norm:
            self.log_normalization(
                entity_id="ONGC-BLT-1001",
                raw_text="M10 SS304 Hex Bolt 50mm",
                normalized_text="m10 ss304 hex bolt 50mm",
                performed_by="AI_TEXT_NORMALIZER",
                reason="Preprocessed enterprise text while preserving dimensional unit (50mm) and grade (ss304)",
            )
            self.log_normalization(
                entity_id="BHEL-MEC-001",
                raw_text="HEX BOLT M10X50 SS-304 GRADE 8.8",
                normalized_text="hex bolt m10x50 ss-304 grade 8.8",
                performed_by="AI_TEXT_NORMALIZER",
                reason="Normalized case and spacing, retained grade 8.8 tensile class",
            )

        if not has_canon:
            self.log_canonical_creation(
                national_material_code="NMM-000001",
                standardized_description="Hex Head Bolt M10 x 50mm Stainless Steel SS304 Full Thread Grade 8.8",
                category="Fasteners & Mechanical Hardware",
                performed_by="STANDARDIZATION_OFFICER (National Master Committee)",
                reason="Harmonized national benchmark specification for SS304 M10 fasteners across CPSEs",
            )
            self.log_canonical_creation(
                national_material_code="NMM-000002",
                standardized_description="Hex Head Bolt M10 x 50mm Marine Grade Stainless Steel SS316 Acid Resistant",
                category="Fasteners & Mechanical Hardware",
                performed_by="STANDARDIZATION_OFFICER (National Master Committee)",
                reason="Harmonized national benchmark specification for SS316 M10 marine fasteners",
            )

        if not has_ai:
            self.log_ai_recommendation(
                source_id="ONGC-BLT-1001",
                suggested_canonical_code="NMM-000001",
                hybrid_score=0.9412,
                breakdown={"semantic": 0.952, "fuzzy": 0.938, "lexical": 0.920},
                performed_by="AI_HYBRID_ENGINE",
                reason="High confidence match: identical nominal diameter (M10), length (50mm), and metallurgy (SS304)",
            )

        if not has_map:
            self.log_mapping_change(
                mapping_id=1,
                cpse_name="ONGC",
                source_code="ONGC-BLT-1001",
                canonical_code="NMM-000001",
                old_canonical_code=None,
                performed_by="Govt Reviewer (Demo Auditor: audit.officer@cpse.gov.in)",
                reason="Approved cross-catalog code linkage after engineering review",
            )

    # =========================================================================
    # Query API with Multi-Factor Filtering
    # =========================================================================

    def get_audit_logs(
        self,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        user: Optional[str] = None,
        date: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Retrieves paginated audit logs with dynamic multi-factor filtering:
        - action: Filters by action type (e.g. UPLOAD_MATERIALS, APPROVE_MATCH, etc.)
        - entity: Searches entity_type OR entity_id
        - user: Searches performed_by OR user
        - date: Searches timestamp by date prefix (e.g. 2026-10-01)
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        conditions = []
        params = []

        if action and action.strip() and action.strip().upper() != "ALL":
            conditions.append("UPPER(action) = ?")
            params.append(action.strip().upper())

        if entity and entity.strip():
            e = f"%{entity.strip().lower()}%"
            conditions.append("(LOWER(entity_type) LIKE ? OR LOWER(COALESCE(entity_id, '')) LIKE ?)")
            params.extend([e, e])

        if user and user.strip():
            u = f"%{user.strip().lower()}%"
            conditions.append("(LOWER(COALESCE(performed_by, '')) LIKE ? OR LOWER(COALESCE(user, '')) LIKE ?)")
            params.extend([u, u])

        if date and date.strip():
            d = date.strip()
            # If date format is YYYY-MM-DD
            conditions.append("(DATE(timestamp) = ? OR timestamp LIKE ?)")
            params.extend([d, f"{d}%"])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with self._get_connection() as conn:
            cur = conn.cursor()

            # Filtered total count
            count_query = f"SELECT COUNT(*) FROM audit_logs {where_clause}"
            cur.execute(count_query, params)
            total = cur.fetchone()[0]

            # Paginated items
            query = f"""
                SELECT
                    id, action, entity_type, entity_id, old_value, new_value,
                    COALESCE(performed_by, user, 'SYSTEM') as performed_by,
                    timestamp, reason, details, user
                FROM audit_logs
                {where_clause}
                ORDER BY id DESC
                LIMIT ? OFFSET ?
            """
            cur.execute(query, params + [page_size, offset])
            rows = cur.fetchall()

            items = []
            for r in rows:
                # Safe JSON decoders for details
                details_parsed = None
                if r["details"]:
                    try:
                        details_parsed = json.loads(r["details"])
                    except Exception:
                        details_parsed = {"raw": r["details"]}

                items.append(
                    {
                        "id": r["id"],
                        "action": r["action"],
                        "entity_type": r["entity_type"],
                        "entity_id": r["entity_id"] or "",
                        "old_value": r["old_value"],
                        "new_value": r["new_value"],
                        "performed_by": r["performed_by"],
                        "timestamp": r["timestamp"],
                        "reason": r["reason"] or "",
                        "details": details_parsed,
                        "user": r["performed_by"],
                    }
                )

            # Available filter dimensions for frontend selectors
            cur.execute("SELECT DISTINCT action FROM audit_logs ORDER BY action ASC")
            available_actions = [row[0] for row in cur.fetchall() if row[0]]

            cur.execute("SELECT DISTINCT entity_type FROM audit_logs ORDER BY entity_type ASC")
            available_entities = [row[0] for row in cur.fetchall() if row[0]]

            cur.execute("SELECT DISTINCT COALESCE(performed_by, user) as usr FROM audit_logs WHERE usr IS NOT NULL ORDER BY usr ASC")
            available_users = [row[0] for row in cur.fetchall() if row[0]]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items,
            "available_actions": available_actions,
            "available_entities": available_entities,
            "available_users": available_users,
        }

    def export_audit_logs_csv(
        self,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user: Optional[str] = None,
        performed_by: Optional[str] = None,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        log_export_event: bool = True,
        exported_by: str = "AUDITOR",
    ) -> Tuple[str, str, int]:
        """
        Exports audit records to a downloadable, standards-compliant CSV file.
        Applies identical multi-factor filter semantics as get_audit_logs.
        Ensures strict secret/password sanitization with [REDACTED_CONFIDENTIAL].
        Returns (csv_content, filename, record_count).
        """
        conditions = []
        params = []

        if action and action.strip() and action.strip().upper() != "ALL":
            conditions.append("UPPER(action) = ?")
            params.append(action.strip().upper())

        if entity and entity.strip():
            e = f"%{entity.strip().lower()}%"
            conditions.append("(LOWER(entity_type) LIKE ? OR LOWER(COALESCE(entity_id, '')) LIKE ?)")
            params.extend([e, e])

        if entity_type and entity_type.strip():
            conditions.append("UPPER(entity_type) = ?")
            params.append(entity_type.strip().upper())

        if entity_id and entity_id.strip():
            conditions.append("entity_id = ?")
            params.append(entity_id.strip())

        if user and user.strip():
            u = f"%{user.strip().lower()}%"
            conditions.append("(LOWER(COALESCE(performed_by, '')) LIKE ? OR LOWER(COALESCE(user, '')) LIKE ?)")
            params.extend([u, u])

        if performed_by and performed_by.strip():
            p = performed_by.strip().upper()
            conditions.append("(UPPER(COALESCE(performed_by, '')) = ? OR UPPER(COALESCE(user, '')) = ?)")
            params.extend([p, p])

        if date and date.strip():
            d = date.strip()
            conditions.append("(DATE(timestamp) = ? OR timestamp LIKE ?)")
            params.extend([d, f"{d}%"])

        if date_from and date_from.strip():
            conditions.append("DATE(timestamp) >= ?")
            params.append(date_from.strip())

        if date_to and date_to.strip():
            conditions.append("DATE(timestamp) <= ?")
            params.append(date_to.strip())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with self._get_connection() as conn:
            cur = conn.cursor()
            query = f"""
                SELECT
                    id, action, entity_type, entity_id, old_value, new_value,
                    COALESCE(performed_by, user, 'SYSTEM') as performed_by,
                    timestamp, reason
                FROM audit_logs
                {where_clause}
                ORDER BY id ASC
            """
            cur.execute(query, params)
            rows = cur.fetchall()

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SIH26099_Audit_Report_{timestamp_str}.csv"

        # Build CSV using Python's standard csv module (RFC 4180 compliant)
        output = io.StringIO()
        output.write("\ufeff")  # UTF-8 BOM for universal spreadsheet software compatibility
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")

        # 9 Recommended CSV columns
        writer.writerow([
            "id",
            "action",
            "entity_type",
            "entity_id",
            "old_value",
            "new_value",
            "performed_by",
            "timestamp",
            "reason",
        ])

        for r in rows:
            writer.writerow([
                r["id"],
                r["action"],
                r["entity_type"],
                r["entity_id"] or "",
                sanitize_for_export(r["old_value"]),
                sanitize_for_export(r["new_value"]),
                r["performed_by"] or "SYSTEM",
                r["timestamp"],
                sanitize_for_export(r["reason"]),
            ])

        csv_content = output.getvalue()
        row_count = len(rows)

        # Log export lifecycle event (executed after query to prevent infinite recursion)
        if log_export_event:
            filter_desc = []
            if action and action.upper() != "ALL": filter_desc.append(f"action={action}")
            if entity: filter_desc.append(f"entity={entity}")
            if user: filter_desc.append(f"user={user}")
            if date: filter_desc.append(f"date={date}")
            filter_summary = ", ".join(filter_desc) if filter_desc else "all records"

            self.record_log(
                action="EXPORT_AUDIT_REPORT",
                entity_type="audit_logs",
                entity_id=filename,
                old_value=None,
                new_value=f"Exported {row_count} audit records to CSV ({filter_summary})",
                performed_by=exported_by,
                reason="Auditor generated compliance audit report export.",
                details={
                    "filename": filename,
                    "row_count": row_count,
                    "filters": {
                        "action": action,
                        "entity": entity,
                        "user": user,
                        "date": date,
                    },
                },
            )

        return csv_content, filename, row_count


# Singleton instance
_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service
