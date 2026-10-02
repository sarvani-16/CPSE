"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Human-in-the-Loop Review Service
Description: Manages AI match suggestions, reviewer workflows (Approve, Reject, Needs Review),
             data governance mapping persistence, and immutable audit logging.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
import json
import sqlite3
from typing import Dict, List, Optional, Any

from backend.app.cpse.models import CREATE_TABLES_SQL
from backend.app.ml.hybrid_engine import get_hybrid_engine


DEFAULT_CANONICAL_MATERIALS = [
    {
        "national_material_code": "NMM-000001",
        "canonical_code": "NMM-000001",
        "canonical_description": "Hex Head Bolt M10 x 50mm Stainless Steel SS304 Full Thread Grade 8.8",
        "category": "Fasteners & Mechanical Hardware",
        "standard_specification": "ISO 4014 / DIN 931 / SS304 / Grade 8.8 / M10x50",
        "standard_uom": "EA",
    },
    {
        "national_material_code": "NMM-000002",
        "canonical_code": "NMM-000002",
        "canonical_description": "Hex Head Bolt M10 x 50mm Marine Grade Stainless Steel SS316 Acid Resistant",
        "category": "Fasteners & Mechanical Hardware",
        "standard_specification": "ISO 4014 / DIN 931 / SS316 / Marine Grade / M10x50",
        "standard_uom": "EA",
    },
    {
        "national_material_code": "NMM-000003",
        "canonical_code": "NMM-000003",
        "canonical_description": "Seamless Carbon Steel Pipe 2 Inch NB Schedule 40 ASTM A106 Grade B",
        "category": "Piping & Tubing",
        "standard_specification": "ASTM A106 Grade B / ASME B36.10M / 2 Inch Sch 40 / Beveled Ends",
        "standard_uom": "MTR",
    },
    {
        "national_material_code": "NMM-000004",
        "canonical_code": "NMM-000004",
        "canonical_description": "Flanged Ball Valve 2 Inch Class 150 WCB Body SS316 Trim",
        "category": "Valves & Actuators",
        "standard_specification": "ASME B16.34 / Class 150 / ASTM A216 WCB / SS316 (CF8M) Trim / 2 Inch",
        "standard_uom": "EA",
    },
    {
        "national_material_code": "NMM-000005",
        "canonical_code": "NMM-000005",
        "canonical_description": "Centrifugal Pump Impeller 250mm Diameter Closed Type Stainless Steel SS316",
        "category": "Pumps & Rotating Equipment",
        "standard_specification": "Closed Impeller 250mm Dia / Dynamic Balanced / CF8M (SS316) / Boiler & Process Service",
        "standard_uom": "EA",
    },
    {
        "national_material_code": "NMM-000006",
        "canonical_code": "NMM-000006",
        "canonical_description": "Transformer Mineral Insulating Oil High Dielectric Voltage Grade",
        "category": "Electrical & Insulating Oils",
        "standard_specification": "IEC 60296 / IS 335 / Breakdown Voltage >= 30kV / 12V Grade",
        "standard_uom": "LTR",
    },
    {
        "national_material_code": "NMM-000007",
        "canonical_code": "NMM-000007",
        "canonical_description": "Spiral Wound Gasket 2 Inch Class 150 SS304 Inner Ring Flexible Graphite Filler",
        "category": "Seals & Gaskets",
        "standard_specification": "ASME B16.20 / Class 150 / 2 Inch / SS304 Winding with Graphite",
        "standard_uom": "EA",
    },
    {
        "national_material_code": "NMM-000008",
        "canonical_code": "NMM-000008",
        "canonical_description": "Carbon Steel 90 Degree Long Radius Pipe Elbow 2 Inch Schedule 40 Butt Weld",
        "category": "Piping & Tubing Fittings",
        "standard_specification": "ASME B16.9 / ASTM A234 WPB / 2 Inch Sch 40 / Long Radius 90 Deg",
        "standard_uom": "EA",
    },
]

DEMO_REVIEWER_DEFAULT = "Govt Reviewer (Demo Auditor: audit.officer@cpse.gov.in)"


class ReviewService:
    """
    Core service for Human-in-the-Loop review lifecycle:
    - Generates candidate suggestions using Hybrid AI Engine
    - Serves paginated reviews with source, AI comparison, and canonical items
    - Handles approval (linking codes in material_mappings without altering source data)
    - Handles rejection and further review requests
    - Maintains immutable data governance audit trail
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.project_root = PROJECT_ROOT
        self.db_path = db_path or (
            self.project_root / "outputs" / "analysis" / "cpse_master.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.hybrid_engine = get_hybrid_engine()
        self._init_database()
        self.seed_canonical_materials()
        self._ensure_initial_reviews()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self) -> None:
        """
        Ensures tables exist.
        """
        with self._get_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)
            conn.commit()

    def seed_canonical_materials(self) -> int:
        """
        Seeds national canonical material standards into canonical_materials table.
        """
        seeded = 0
        with self._get_connection() as conn:
            cur = conn.cursor()
            for mat in DEFAULT_CANONICAL_MATERIALS:
                cur.execute(
                    """
                    INSERT INTO canonical_materials (
                        national_material_code, canonical_code, standardized_description,
                        canonical_description, category, standard_specification, standard_uom
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(national_material_code) DO UPDATE SET
                        canonical_code = excluded.canonical_code,
                        standardized_description = excluded.standardized_description,
                        canonical_description = excluded.canonical_description,
                        category = excluded.category,
                        standard_specification = excluded.standard_specification,
                        standard_uom = excluded.standard_uom
                    """,
                    (
                        mat["national_material_code"],
                        mat["canonical_code"],
                        mat["canonical_description"],
                        mat["canonical_description"],
                        mat["category"],
                        mat["standard_specification"],
                        mat["standard_uom"],
                    ),
                )
                seeded += 1
            conn.commit()
        return seeded

    def _ensure_initial_reviews(self) -> None:
        """
        Checks if reviews table is empty or references orphaned/outdated canonical codes;
        if so, regenerates candidate reviews for existing source materials.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM reviews r
                WHERE r.suggested_canonical_code NOT IN (
                    SELECT national_material_code FROM canonical_materials
                    UNION
                    SELECT canonical_code FROM canonical_materials
                )
            """)
            orphaned = cur.fetchone()[0]
            if orphaned > 0:
                cur.execute("DELETE FROM reviews")
                conn.commit()

            cur.execute("SELECT COUNT(*) FROM reviews")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute("SELECT COUNT(*) FROM source_materials")
                sources_count = cur.fetchone()[0]
                if sources_count > 0:
                    self.generate_reviews(force_refresh=True)

    def generate_reviews(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Runs the Hybrid AI Matching Engine to pair source materials with canonical materials.
        Populates candidate matches into reviews table.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()

            if force_refresh:
                cur.execute("DELETE FROM reviews WHERE status = 'PENDING'")
                conn.commit()

            # Fetch canonical materials (supports both national_material_code and canonical_code)
            cur.execute(
                """
                SELECT national_material_code, canonical_code,
                       COALESCE(canonical_description, standardized_description) as canonical_description,
                       category, standard_specification, standard_uom
                FROM canonical_materials
                """
            )
            canonicals = [dict(r) for r in cur.fetchall()]

            if not canonicals:
                return {"status": "error", "message": "No canonical materials available."}

            # Fetch source materials that don't yet have an active review
            cur.execute(
                """
                SELECT id, cpse_name, material_code, description, specification, material_grade, dimensions, unit_of_measure
                FROM source_materials
                WHERE id NOT IN (SELECT source_material_id FROM reviews)
                """
            )
            sources = [dict(r) for r in cur.fetchall()]

            generated_count = 0

            for src in sources:
                src_text = src["description"]
                if src["specification"]:
                    src_text += f" {src['specification']}"
                if src["material_grade"]:
                    src_text += f" {src['material_grade']}"

                best_match = None
                best_score = -1.0
                best_details = None

                # Find best matching canonical item using hybrid engine
                for can in canonicals:
                    can_text = can["canonical_description"]
                    if can["standard_specification"]:
                        can_text += f" {can['standard_specification']}"

                    res = self.hybrid_engine.compare(src_text, can_text)
                    if res["hybrid_score"] > best_score:
                        best_score = res["hybrid_score"]
                        best_match = can
                        best_details = res

                is_unseen = (
                    best_match is None
                    or best_score < self.hybrid_engine.threshold_review
                    or (best_details and best_details.get("match_decision") == "NOT_MATCH")
                )

                if is_unseen:
                    from backend.app.cpse.canonical_service import CanonicalMaterialService
                    can_service = CanonicalMaterialService(self.db_path)
                    new_can = can_service.create_prototype_canonical(
                        src,
                        performed_by="AI_STANDARDIZATION_ENGINE",
                        reason=f"Unseen material with no existing canonical match (best similarity: {max(best_score, 0.0):.2%} < {self.hybrid_engine.threshold_review:.0%})",
                    )
                    target_code = new_can["national_material_code"]
                    status = "NEEDS_REVIEW"

                    # Add newly generated prototype canonical to in-memory list for subsequent items
                    canonicals.append({
                        "national_material_code": new_can["national_material_code"],
                        "canonical_code": new_can["national_material_code"],
                        "canonical_description": new_can["standardized_description"],
                        "category": new_can["category"],
                        "standard_specification": new_can.get("standard_specification", ""),
                        "standard_uom": new_can.get("standard_uom", "EA"),
                    })

                    explanation_items = [
                        f"Unseen material detected. Highest existing canonical similarity was {max(best_score, 0.0):.2%}, below review threshold {self.hybrid_engine.threshold_review:.0%}.",
                        f"Generated prototype canonical material code {target_code} with standardized description.",
                        "Flagged for human expert validation in Review Center.",
                    ]
                    cur.execute(
                        """
                        INSERT INTO reviews (
                            source_material_id, suggested_canonical_code, status,
                            semantic_score, fuzzy_score, lexical_score, hybrid_score,
                            detected_attributes, conflicts, explanation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            src["id"],
                            target_code,
                            status,
                            best_details["semantic_score"] if best_details else 0.0,
                            best_details["fuzzy_score"] if best_details else 0.0,
                            best_details["lexical_score"] if best_details else 0.0,
                            best_score if best_score > 0 else 0.0,
                            json.dumps({"unseen_material": True, "created_prototype": target_code}),
                            json.dumps([]),
                            json.dumps(explanation_items),
                        ),
                    )
                    generated_count += 1
                elif best_match and best_details:
                    # Decide initial review status
                    has_conflicts = best_details["technical_tokens"]["has_conflicts"]
                    if has_conflicts or best_details["match_decision"] == "REVIEW":
                        status = "NEEDS_REVIEW"
                    else:
                        status = "PENDING"

                    target_code = best_match.get("national_material_code") or best_match.get("canonical_code")
                    cur.execute(
                        """
                        INSERT INTO reviews (
                            source_material_id, suggested_canonical_code, status,
                            semantic_score, fuzzy_score, lexical_score, hybrid_score,
                            detected_attributes, conflicts, explanation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            src["id"],
                            target_code,
                            status,
                            best_details["semantic_score"],
                            best_details["fuzzy_score"],
                            best_details["lexical_score"],
                            best_details["hybrid_score"],
                            json.dumps(
                                {
                                    "matching": best_details["technical_tokens"]["matching"],
                                    "differing_source": best_details["technical_tokens"]["differing_a"],
                                    "differing_canonical": best_details["technical_tokens"]["differing_b"],
                                }
                            ),
                            json.dumps(best_details["technical_tokens"]["conflicts"]),
                            json.dumps(best_details["explanation"]),
                        ),
                    )
                    generated_count += 1

            conn.commit()

        return {
            "status": "success",
            "reviews_generated": generated_count,
            "timestamp": datetime.now().isoformat(),
        }

    def get_reviews(
        self,
        status: Optional[str] = None,
        search: Optional[str] = None,
        cpse_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Retrieves paginated review items with 3-column view details:
        Source, AI comparison metrics/evidence, and Recommended Canonical item.
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        offset = (page - 1) * page_size

        conditions = []
        params = []

        if status and status.upper() not in ["ALL", ""]:
            conditions.append("r.status = ?")
            params.append(status.upper())

        if cpse_name and cpse_name.strip():
            conditions.append("s.cpse_name = ?")
            params.append(cpse_name.strip())

        if search and search.strip():
            s = f"%{search.strip().lower()}%"
            conditions.append(
                "(LOWER(s.material_code) LIKE ? OR LOWER(s.description) LIKE ? OR LOWER(c.canonical_code) LIKE ? OR LOWER(c.canonical_description) LIKE ?)"
            )
            params.extend([s, s, s, s])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with self._get_connection() as conn:
            cur = conn.cursor()

            # Total counts by status for dashboard tabs
            cur.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_cnt,
                    SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved_cnt,
                    SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_cnt,
                    SUM(CASE WHEN status = 'NEEDS_REVIEW' THEN 1 ELSE 0 END) as needs_review_cnt
                FROM reviews
                """
            )
            summary_row = cur.fetchone()
            status_counts = {
                "ALL": summary_row[0] or 0,
                "PENDING": summary_row[1] or 0,
                "APPROVED": summary_row[2] or 0,
                "REJECTED": summary_row[3] or 0,
                "NEEDS_REVIEW": summary_row[4] or 0,
            }

            # Filtered total count
            count_query = f"""
                SELECT COUNT(*)
                FROM reviews r
                JOIN source_materials s ON r.source_material_id = s.id
                JOIN canonical_materials c ON (
                    r.suggested_canonical_code = c.national_material_code
                    OR r.suggested_canonical_code = c.canonical_code
                )
                {where_clause}
            """
            cur.execute(count_query, params)
            total = cur.fetchone()[0]

            # Fetch paginated items
            query = f"""
                SELECT
                    r.id, r.source_material_id, r.suggested_canonical_code, r.status,
                    r.semantic_score, r.fuzzy_score, r.lexical_score, r.hybrid_score,
                    r.detected_attributes, r.conflicts, r.explanation,
                    r.reviewer_name, r.comments, r.reviewed_at, r.created_at,
                    s.cpse_name, s.material_code as source_code, s.description as source_desc,
                    s.specification as source_spec, s.material_type as source_type,
                    s.material_grade as source_grade, s.dimensions as source_dimensions,
                    s.unit_of_measure as source_uom, s.manufacturer as source_mfg,
                    s.part_number as source_part_no, s.category as source_cat,
                    c.national_material_code, c.canonical_code,
                    COALESCE(c.standardized_description, c.canonical_description) as canon_desc,
                    c.category as canon_cat, c.standard_specification as canon_spec,
                    c.standard_uom as canon_uom
                FROM reviews r
                JOIN source_materials s ON r.source_material_id = s.id
                JOIN canonical_materials c ON (
                    r.suggested_canonical_code = c.national_material_code
                    OR r.suggested_canonical_code = c.canonical_code
                )
                {where_clause}
                ORDER BY
                    CASE r.status
                        WHEN 'NEEDS_REVIEW' THEN 1
                        WHEN 'PENDING' THEN 2
                        WHEN 'APPROVED' THEN 3
                        WHEN 'REJECTED' THEN 4
                        ELSE 5
                    END,
                    r.hybrid_score DESC,
                    r.id DESC
                LIMIT ? OFFSET ?
            """
            cur.execute(query, params + [page_size, offset])
            rows = cur.fetchall()

            items = []
            for r in rows:
                # Safe JSON decoders
                try:
                    detected_attrs = json.loads(r["detected_attributes"]) if r["detected_attributes"] else {}
                except Exception:
                    detected_attrs = {}

                try:
                    conflicts_list = json.loads(r["conflicts"]) if r["conflicts"] else []
                except Exception:
                    conflicts_list = []

                try:
                    explanation_list = json.loads(r["explanation"]) if r["explanation"] else []
                except Exception:
                    explanation_list = []

                can_code = r["national_material_code"] if "national_material_code" in r.keys() and r["national_material_code"] else r["canonical_code"]

                items.append(
                    {
                        "id": r["id"],
                        "status": r["status"],
                        "source": {
                            "id": r["source_material_id"],
                            "cpse_name": r["cpse_name"],
                            "material_code": r["source_code"],
                            "description": r["source_desc"],
                            "specification": r["source_spec"] or "N/A",
                            "material_grade": r["source_grade"] or "N/A",
                            "dimensions": r["source_dimensions"] or "N/A",
                            "unit_of_measure": r["source_uom"] or "N/A",
                            "material_type": r["source_type"] or "Standard Material",
                            "category": r["source_cat"] or "General Equipment",
                            "manufacturer": r["source_mfg"] or "N/A",
                            "part_number": r["source_part_no"] or "N/A",
                        },
                        "ai_comparison": {
                            "hybrid_score": r["hybrid_score"],
                            "semantic_score": r["semantic_score"],
                            "fuzzy_score": r["fuzzy_score"],
                            "lexical_score": r["lexical_score"],
                            "detected_attributes": detected_attrs,
                            "conflicts": conflicts_list,
                            "explanation": explanation_list,
                        },
                        "canonical": {
                            "national_material_code": can_code,
                            "canonical_code": can_code,
                            "canonical_description": r["canon_desc"],
                            "category": r["canon_cat"] or "Standard Mechanical / Process Component",
                            "standard_specification": r["canon_spec"] or "National Standard Specification",
                            "standard_uom": r["canon_uom"] or "EA",
                        },
                        "reviewer_name": r["reviewer_name"],
                        "comments": r["comments"],
                        "reviewed_at": r["reviewed_at"],
                        "created_at": r["created_at"],
                    }
                )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return {
            "total": total,
            "counts": status_counts,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items,
        }

    def approve_review(
        self,
        review_id: int,
        reviewer_name: str = DEMO_REVIEWER_DEFAULT,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Approves an AI match recommendation:
        - Sets review status to 'APPROVED'
        - Creates / updates persistent material_mappings entry
        - Preserves original CPSE code and description intact (zero data destruction)
        - Records immutable entry in audit_logs
        """
        reviewer = reviewer_name.strip() if reviewer_name else DEMO_REVIEWER_DEFAULT
        timestamp_now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cur = conn.cursor()

            # Fetch the review and associated source & canonical details
            cur.execute(
                """
                SELECT
                    r.id, r.source_material_id, r.suggested_canonical_code, r.status, r.hybrid_score,
                    s.cpse_name, s.material_code, s.description as source_desc,
                    COALESCE(c.national_material_code, c.canonical_code) as canonical_code,
                    COALESCE(c.standardized_description, c.canonical_description) as canon_desc
                FROM reviews r
                JOIN source_materials s ON r.source_material_id = s.id
                JOIN canonical_materials c ON (
                    r.suggested_canonical_code = c.national_material_code
                    OR r.suggested_canonical_code = c.canonical_code
                )
                WHERE r.id = ?
                """,
                (review_id,),
            )
            review = cur.fetchone()

            if not review:
                raise ValueError(f"Review item with ID {review_id} not found.")

            prev_status = review["status"]

            # 1. Update review record
            cur.execute(
                """
                UPDATE reviews
                SET status = 'APPROVED',
                    reviewer_name = ?,
                    comments = ?,
                    reviewed_at = ?
                WHERE id = ?
                """,
                (reviewer, comment, timestamp_now, review_id),
            )

            # 2. Upsert into material_mappings (Preserving original CPSE code and description)
            cur.execute(
                "SELECT id FROM material_mappings WHERE source_material_id = ?",
                (review["source_material_id"],),
            )
            existing_mapping = cur.fetchone()

            if existing_mapping:
                cur.execute(
                    """
                    UPDATE material_mappings
                    SET canonical_material_code = ?,
                        canonical_description = ?,
                        match_status = 'APPROVED',
                        confidence = ?,
                        reviewer = ?,
                        timestamp = ?
                    WHERE id = ?
                    """,
                    (
                        review["canonical_code"],
                        review["canon_desc"],
                        review["hybrid_score"],
                        reviewer,
                        timestamp_now,
                        existing_mapping["id"],
                    ),
                )
                mapping_id = existing_mapping["id"]
            else:
                cur.execute(
                    """
                    INSERT INTO material_mappings (
                        source_material_id, cpse_name, original_material_code,
                        original_description, canonical_material_code, canonical_description,
                        match_status, confidence, reviewer, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, 'APPROVED', ?, ?, ?)
                    """,
                    (
                        review["source_material_id"],
                        review["cpse_name"],
                        review["material_code"],
                        review["source_desc"],
                        review["canonical_code"],
                        review["canon_desc"],
                        review["hybrid_score"],
                        reviewer,
                        timestamp_now,
                    ),
                )
                mapping_id = cur.lastrowid

            # 3. Graduate pending prototype canonical material to APPROVED if applicable
            cur.execute(
                """
                UPDATE canonical_materials
                SET approval_status = 'APPROVED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE (national_material_code = ? OR canonical_code = ?)
                  AND approval_status = 'PENDING'
                """,
                (review["canonical_code"], review["canonical_code"]),
            )

            conn.commit()

        # 3. Write immutable audit log outside active write transaction
        from backend.app.cpse.audit_service import get_audit_service
        audit_svc = get_audit_service()
        audit_svc.log_approval(
            review_id=review_id,
            mapping_id=mapping_id,
            source_code=review["material_code"],
            canonical_code=review["canonical_code"],
            performed_by=reviewer,
            reason=comment or "Match verified and approved by authority.",
            old_status=prev_status,
        )
        audit_svc.log_mapping_change(
            mapping_id=mapping_id,
            cpse_name=review["cpse_name"],
            source_code=review["material_code"],
            canonical_code=review["canonical_code"],
            old_canonical_code=None if not existing_mapping else "PREVIOUS_MAPPING",
            performed_by=reviewer,
            reason=f"Approved cross-catalog mapping for {review['material_code']} -> {review['canonical_code']}",
        )

        return {
            "status": "success",
            "action": "APPROVED",
            "review_id": review_id,
            "mapping_id": mapping_id,
            "source_code": review["material_code"],
            "canonical_code": review["canonical_code"],
            "reviewer": reviewer,
            "timestamp": timestamp_now,
        }

    def reject_review(
        self,
        review_id: int,
        reviewer_name: str = DEMO_REVIEWER_DEFAULT,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rejects an AI match recommendation:
        - Sets review status to 'REJECTED'
        - Flags any associated material mapping as 'REJECTED'
        - Records immutable entry in audit_logs
        """
        reviewer = reviewer_name.strip() if reviewer_name else DEMO_REVIEWER_DEFAULT
        timestamp_now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cur = conn.cursor()

            cur.execute(
                """
                SELECT
                    r.id, r.source_material_id, r.suggested_canonical_code, r.status,
                    s.cpse_name, s.material_code,
                    COALESCE(c.national_material_code, c.canonical_code) as canonical_code
                FROM reviews r
                JOIN source_materials s ON r.source_material_id = s.id
                JOIN canonical_materials c ON (
                    r.suggested_canonical_code = c.national_material_code
                    OR r.suggested_canonical_code = c.canonical_code
                )
                WHERE r.id = ?
                """,
                (review_id,),
            )
            review = cur.fetchone()

            if not review:
                raise ValueError(f"Review item with ID {review_id} not found.")

            prev_status = review["status"]

            # Update review record
            cur.execute(
                """
                UPDATE reviews
                SET status = 'REJECTED',
                    reviewer_name = ?,
                    comments = ?,
                    reviewed_at = ?
                WHERE id = ?
                """,
                (reviewer, comment, timestamp_now, review_id),
            )

            # Update existing mapping if any
            cur.execute(
                """
                UPDATE material_mappings
                SET match_status = 'REJECTED',
                    reviewer = ?,
                    timestamp = ?
                WHERE source_material_id = ?
                """,
                (reviewer, timestamp_now, review["source_material_id"]),
            )

            conn.commit()

        # Immutable audit log outside active write transaction
        from backend.app.cpse.audit_service import get_audit_service
        audit_svc = get_audit_service()
        audit_svc.log_rejection(
            review_id=review_id,
            source_code=review["material_code"],
            canonical_code=review["canonical_code"],
            performed_by=reviewer,
            reason=comment or "Match recommendation rejected by reviewer.",
            old_status=prev_status,
        )

        return {
            "status": "success",
            "action": "REJECTED",
            "review_id": review_id,
            "source_code": review["material_code"],
            "canonical_code": review["canonical_code"],
            "reviewer": reviewer,
            "timestamp": timestamp_now,
        }

    def request_further_review(
        self,
        review_id: int,
        reviewer_name: str = DEMO_REVIEWER_DEFAULT,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Marks item as needing further technical clarification or senior audit:
        - Sets review status to 'NEEDS_REVIEW'
        - Records immutable entry in audit_logs
        """
        reviewer = reviewer_name.strip() if reviewer_name else DEMO_REVIEWER_DEFAULT
        timestamp_now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cur = conn.cursor()

            cur.execute(
                """
                SELECT
                    r.id, r.source_material_id, r.suggested_canonical_code, r.status,
                    s.cpse_name, s.material_code,
                    COALESCE(c.national_material_code, c.canonical_code) as canonical_code
                FROM reviews r
                JOIN source_materials s ON r.source_material_id = s.id
                JOIN canonical_materials c ON (
                    r.suggested_canonical_code = c.national_material_code
                    OR r.suggested_canonical_code = c.canonical_code
                )
                WHERE r.id = ?
                """,
                (review_id,),
            )
            review = cur.fetchone()

            if not review:
                raise ValueError(f"Review item with ID {review_id} not found.")

            prev_status = review["status"]

            # Update review record
            cur.execute(
                """
                UPDATE reviews
                SET status = 'NEEDS_REVIEW',
                    reviewer_name = ?,
                    comments = ?,
                    reviewed_at = ?
                WHERE id = ?
                """,
                (reviewer, comment, timestamp_now, review_id),
            )

            conn.commit()

        # Immutable audit log outside active write transaction
        from backend.app.cpse.audit_service import get_audit_service
        audit_svc = get_audit_service()
        audit_svc.record_log(
            action="REQUEST_FURTHER_REVIEW",
            entity_type="reviews",
            entity_id=str(review_id),
            old_value=f"Review Status: {prev_status}",
            new_value="Review Status: NEEDS_REVIEW",
            performed_by=reviewer,
            reason=comment or "Requires senior engineering committee / technical clarification.",
            details={
                "review_id": review_id,
                "cpse_name": review["cpse_name"],
                "source_code": review["material_code"],
                "canonical_code": review["canonical_code"],
            },
        )

        return {
            "status": "success",
            "action": "NEEDS_REVIEW",
            "review_id": review_id,
            "source_code": review["material_code"],
            "canonical_code": review["canonical_code"],
            "reviewer": reviewer,
            "timestamp": timestamp_now,
        }

    def batch_approve_reviews(
        self,
        review_ids: List[int],
        reviewer_name: str = DEMO_REVIEWER_DEFAULT,
        comment: Optional[str] = None,
        min_confidence: float = 0.80,
    ) -> Dict[str, Any]:
        """
        Batch-approves multiple candidate matches subject to strict safety guardrails:
        1. Review item existence and non-approved status.
        2. High-confidence eligibility (hybrid_score >= min_confidence, default 0.80).
        3. Zero domain/technical conflicts (conflicts list must be empty).
        4. Reuses individual approve_review() logic:
           - Updates reviews table
           - Upserts material_mappings (strictly preserving original CPSE code & desc)
           - Graduates pending prototype canonicals to APPROVED
           - Creates individual APPROVE_MATCH and MAPPING_UPDATED audit logs
        5. Reports granular results: approved list and skipped list with specific reasons.
        6. Idempotency & double-click protection: already-approved items are safely skipped.
        """
        reviewer = reviewer_name.strip() if reviewer_name else DEMO_REVIEWER_DEFAULT
        batch_comment = comment.strip() if comment else "Batch approval of high-confidence matches by authorized reviewer"

        approved = []
        skipped = []

        # Deduplicate review_ids while preserving order
        unique_ids = list(dict.fromkeys(review_ids))

        for r_id in unique_ids:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, status, hybrid_score, conflicts, suggested_canonical_code
                    FROM reviews
                    WHERE id = ?
                    """,
                    (r_id,),
                )
                row = cur.fetchone()

            if not row:
                skipped.append({
                    "review_id": r_id,
                    "reason": f"Review item with ID {r_id} not found",
                })
                continue

            current_status = row["status"]
            score = row["hybrid_score"] or 0.0

            # 1. Idempotency / Double-click safety: Skip already approved
            if current_status == "APPROVED":
                skipped.append({
                    "review_id": r_id,
                    "reason": "Review item is already approved",
                })
                continue

            # Skip rejected items
            if current_status == "REJECTED":
                skipped.append({
                    "review_id": r_id,
                    "reason": "Review item has already been rejected",
                })
                continue

            # 2. Check high-confidence threshold
            if score < min_confidence:
                skipped.append({
                    "review_id": r_id,
                    "reason": f"Confidence score ({score:.4f}) is below the required high-confidence threshold ({min_confidence:.2f})",
                })
                continue

            # 3. Check domain/technical conflicts
            conflicts_list = []
            if row["conflicts"]:
                try:
                    conflicts_list = json.loads(row["conflicts"])
                except Exception:
                    conflicts_list = [row["conflicts"]]

            if conflicts_list and len(conflicts_list) > 0:
                conflict_summary = []
                for c in conflicts_list:
                    if isinstance(c, dict):
                        attr = c.get("attribute", "attribute")
                        va = c.get("val_a", "val_a")
                        vb = c.get("val_b", "val_b")
                        conflict_summary.append(f"{attr} ({va} vs {vb})")
                    else:
                        conflict_summary.append(str(c))
                skipped.append({
                    "review_id": r_id,
                    "reason": f"Unresolved technical specification conflict: {', '.join(conflict_summary)}",
                })
                continue

            # 4. Execute individual approval (reusing approve_review)
            try:
                res = self.approve_review(
                    review_id=r_id,
                    reviewer_name=reviewer,
                    comment=batch_comment,
                )
                approved.append({
                    "review_id": r_id,
                    "source_code": res["source_code"],
                    "canonical_code": res["canonical_code"],
                    "mapping_id": res["mapping_id"],
                    "status": "APPROVED",
                })
            except Exception as e:
                skipped.append({
                    "review_id": r_id,
                    "reason": f"Approval execution failed: {str(e)}",
                })

        return {
            "status": "success",
            "total_requested": len(review_ids),
            "approved_count": len(approved),
            "skipped_count": len(skipped),
            "approved": approved,
            "skipped": skipped,
        }


# Singleton instance
_review_service: Optional[ReviewService] = None


def get_review_service() -> ReviewService:
    global _review_service
    if _review_service is None:
        _review_service = ReviewService()
    return _review_service
