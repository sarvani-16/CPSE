"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Automated Verification Test Suite for Batch Review Actions
Description:
  Validates batch review approval with strict safety guardrails:
  - TEST 1: Single eligible high-confidence item approved and mapping created
  - TEST 2: Multiple eligible candidates approved with individual APPROVE_MATCH audit events
  - TEST 3: Low-confidence candidate skipped with clear justification
  - TEST 4: High numerical score with active domain/technical conflict skipped
  - TEST 5: Idempotency & double-click safety (already-approved item skipped, 0 duplicate mappings)
  - TEST 6: Mixed batch partial success reporting (eligible approved, invalid skipped with reasons)
  - TEST 7: Audit trail verification (individual APPROVE_MATCH events, recursive secret redaction)
  - TEST 8: Full traceability and original CPSE material code/description preservation
  - TEST 9: Frontend UI verification (batch toolbar, checkboxes, count indicator, button disablement)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from fastapi.testclient import TestClient
from main import app
from backend.app.cpse.service import get_cpse_service
from backend.app.cpse.review_service import get_review_service

client = TestClient(app)
cpse_service = get_cpse_service()
review_service = get_review_service()


def setup_test_batch_records():
    """
    Sets up isolated test records in cpse_master.db for hermetic batch review testing.
    Uses codes prefixed with 'TEST-BATCH-' to avoid interfering with production records.
    """
    with cpse_service._get_connection() as conn:
        cur = conn.cursor()

        # Clean prior test artifacts
        cur.execute("DELETE FROM audit_logs WHERE reason LIKE '%TEST-BATCH%' OR performed_by LIKE '%BatchTestRunner%'")
        cur.execute("DELETE FROM material_mappings WHERE original_material_code LIKE 'TEST-BATCH-%'")
        cur.execute("DELETE FROM reviews WHERE source_material_id IN (SELECT id FROM source_materials WHERE material_code LIKE 'TEST-BATCH-%')")
        cur.execute("DELETE FROM source_materials WHERE material_code LIKE 'TEST-BATCH-%'")
        conn.commit()

        # Insert 6 test source materials
        materials = [
            # 1. Eligible high-confidence 1
            ("ONGC", "TEST-BATCH-001", "Hex Head Bolt M10 x 50mm Stainless Steel SS304 Full Thread Grade 8.8", "ISO 4014 / DIN 931", "SS304", "EA"),
            # 2. Eligible high-confidence 2
            ("BHEL", "TEST-BATCH-002", "Seamless Carbon Steel Pipe 2 inch Sch 40 ASTM A106 Grade B", "ASTM A106-B / Sch 40", "A106-B", "MTR"),
            # 3. Eligible high-confidence 3
            ("ONGC", "TEST-BATCH-003", "Spiral Wound Gasket 2 inch 150# ASME B16.20 316L with Graphite Filler", "ASME B16.20", "SS316L", "EA"),
            # 4. Low confidence
            ("BHEL", "TEST-BATCH-004", "Generic Unclassified Industrial Flange Spacer Component", "Unknown Spec", "CS", "NOS"),
            # 5. High score with technical conflict (SS304 vs SS316)
            ("ONGC", "TEST-BATCH-005", "Hex Head Bolt M10 x 50mm Marine Grade SS316", "ISO 4014 / DIN 931", "SS316", "EA"),
            # 6. Already approved
            ("BHEL", "TEST-BATCH-006", "Ball Valve 2 inch 150# Flanged WCB Body Full Bore", "ASME B16.34", "WCB", "EA"),
            # 7. Additional eligible item for mixed batch
            ("ONGC", "TEST-BATCH-007", "Transformer Insulating Oil Grade IEC 60296 Mineral Oil", "IEC 60296", "Oil", "LTR"),
        ]

        src_ids = []
        for cpse, code, desc, spec, grade, uom in materials:
            cur.execute(
                """
                INSERT INTO source_materials (cpse_name, material_code, description, specification, material_grade, unit_of_measure)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cpse, code, desc, spec, grade, uom),
            )
            src_ids.append(cur.lastrowid)

        # Insert corresponding review records
        # 1. Eligible (score = 0.92, PENDING, no conflicts)
        cur.execute(
            """
            INSERT INTO reviews (source_material_id, suggested_canonical_code, status, hybrid_score, semantic_score, fuzzy_score, lexical_score, detected_attributes, conflicts, explanation)
            VALUES (?, 'NMM-000001', 'PENDING', 0.9250, 0.95, 0.90, 0.91, ?, '[]', ?)
            """,
            (src_ids[0], json.dumps({"matching": ["bolt", "m10", "ss304"]}), json.dumps(["High confidence specification match."])),
        )
        r1_id = cur.lastrowid

        # 2. Eligible (score = 0.88, PENDING, no conflicts)
        cur.execute(
            """
            INSERT INTO reviews (source_material_id, suggested_canonical_code, status, hybrid_score, semantic_score, fuzzy_score, lexical_score, detected_attributes, conflicts, explanation)
            VALUES (?, 'NMM-000003', 'PENDING', 0.8800, 0.89, 0.87, 0.88, ?, '[]', ?)
            """,
            (src_ids[1], json.dumps({"matching": ["pipe", "2 inch", "a106-b"]}), json.dumps(["High confidence pipe match."])),
        )
        r2_id = cur.lastrowid

        # 3. Eligible (score = 0.85, PENDING, no conflicts)
        cur.execute(
            """
            INSERT INTO reviews (source_material_id, suggested_canonical_code, status, hybrid_score, semantic_score, fuzzy_score, lexical_score, detected_attributes, conflicts, explanation)
            VALUES (?, 'NMM-000007', 'PENDING', 0.8520, 0.86, 0.84, 0.85, ?, '[]', ?)
            """,
            (src_ids[2], json.dumps({"matching": ["gasket", "spiral wound"]}), json.dumps(["High confidence gasket match."])),
        )
        r3_id = cur.lastrowid

        # 4. Low-confidence (score = 0.62 < 0.80 threshold)
        cur.execute(
            """
            INSERT INTO reviews (source_material_id, suggested_canonical_code, status, hybrid_score, semantic_score, fuzzy_score, lexical_score, detected_attributes, conflicts, explanation)
            VALUES (?, 'NMM-000001', 'PENDING', 0.6200, 0.60, 0.65, 0.61, '[]', '[]', ?)
            """,
            (src_ids[3], json.dumps(["Low confidence match requiring manual engineering assessment."])),
        )
        r4_id = cur.lastrowid

        # 5. High score (0.94) but with technical conflict (suggested canonical is NMM-000001 which is SS304, but item is SS316)
        conflict_payload = [{"attribute": "material_grade", "val_a": "SS316", "val_b": "SS304"}]
        cur.execute(
            """
            INSERT INTO reviews (source_material_id, suggested_canonical_code, status, hybrid_score, semantic_score, fuzzy_score, lexical_score, detected_attributes, conflicts, explanation)
            VALUES (?, 'NMM-000001', 'PENDING', 0.9400, 0.96, 0.93, 0.92, '[]', ?, ?)
            """,
            (src_ids[4], json.dumps(conflict_payload), json.dumps(["Critical metallurgical conflict: SS316 vs SS304."])),
        )
        r5_id = cur.lastrowid

        # 6. Already approved
        cur.execute(
            """
            INSERT INTO reviews (source_material_id, suggested_canonical_code, status, hybrid_score, semantic_score, fuzzy_score, lexical_score, detected_attributes, conflicts, explanation, reviewer_name, reviewed_at)
            VALUES (?, 'NMM-000004', 'APPROVED', 0.8900, 0.90, 0.88, 0.89, '[]', '[]', ?, 'Pre-Approved Auditor', '2026-09-30T10:00:00')
            """,
            (src_ids[5], json.dumps(["Already reviewed and approved item."])),
        )
        r6_id = cur.lastrowid

        # Insert pre-existing mapping for item 6
        cur.execute(
            """
            INSERT INTO material_mappings (source_material_id, cpse_name, original_material_code, original_description, canonical_material_code, canonical_description, match_status, confidence, reviewer)
            VALUES (?, 'BHEL', 'TEST-BATCH-006', 'Ball Valve 2 inch 150# Flanged WCB Body Full Bore', 'NMM-000004', 'Ball Valve 2 inch 150# Flanged Full Bore', 'APPROVED', 0.8900, 'Pre-Approved Auditor')
            """,
            (src_ids[5],),
        )

        # 7. Additional eligible (score = 0.86, PENDING, no conflicts)
        cur.execute(
            """
            INSERT INTO reviews (source_material_id, suggested_canonical_code, status, hybrid_score, semantic_score, fuzzy_score, lexical_score, detected_attributes, conflicts, explanation)
            VALUES (?, 'NMM-000006', 'PENDING', 0.8650, 0.88, 0.85, 0.86, '[]', '[]', ?)
            """,
            (src_ids[6], json.dumps(["High confidence transformer oil match."])),
        )
        r7_id = cur.lastrowid

        conn.commit()

    return {
        "src_ids": src_ids,
        "r_ids": [r1_id, r2_id, r3_id, r4_id, r5_id, r6_id, r7_id],
    }


def teardown_test_batch_records():
    """
    Cleans up all test batch artifacts to keep the database in a pristine state.
    """
    with cpse_service._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM audit_logs WHERE reason LIKE '%TEST-BATCH%' OR performed_by LIKE '%BatchTestRunner%'")
        cur.execute("DELETE FROM material_mappings WHERE original_material_code LIKE 'TEST-BATCH-%'")
        cur.execute("DELETE FROM reviews WHERE source_material_id IN (SELECT id FROM source_materials WHERE material_code LIKE 'TEST-BATCH-%')")
        cur.execute("DELETE FROM source_materials WHERE material_code LIKE 'TEST-BATCH-%'")
        conn.commit()


def test_batch_review_pipeline():
    print("=" * 80)
    print("RUNNING BATCH REVIEW ACTIONS VERIFICATION TEST SUITE (SECTIONS 1-15)")
    print("=" * 80)

    fixtures = setup_test_batch_records()
    r_ids = fixtures["r_ids"]
    src_ids = fixtures["src_ids"]

    try:
        # ------------------------------------------------------------------
        # TEST 1 — Single eligible item
        # ------------------------------------------------------------------
        print("\n[1/9] TEST 1: Single eligible high-confidence item approval ...")
        payload1 = {
            "review_ids": [r_ids[0]],
            "reviewer_name": "BatchTestRunner (Auditor)",
            "comment": "TEST-BATCH: Single candidate verification",
        }
        res1 = client.post("/api/reviews/batch-approve", json=payload1)
        assert res1.status_code == 200, f"Expected 200, got {res1.status_code}: {res1.text}"
        data1 = res1.json()
        assert data1["status"] == "success"
        assert data1["total_requested"] == 1
        assert data1["approved_count"] == 1
        assert data1["skipped_count"] == 0
        assert len(data1["approved"]) == 1
        assert data1["approved"][0]["review_id"] == r_ids[0]
        assert data1["approved"][0]["canonical_code"] == "NMM-000001"
        assert data1["approved"][0]["status"] == "APPROVED"

        # Verify DB state for item 1
        with cpse_service._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM reviews WHERE id = ?", (r_ids[0],))
            assert cur.fetchone()[0] == "APPROVED"
            cur.execute("SELECT canonical_material_code, match_status FROM material_mappings WHERE source_material_id = ?", (src_ids[0],))
            m_row = cur.fetchone()
            assert m_row is not None
            assert m_row[0] == "NMM-000001"
            assert m_row[1] == "APPROVED"
        print(f"      [OK] Review #{r_ids[0]} approved, mapping created successfully.")

        # ------------------------------------------------------------------
        # TEST 2 — Multiple eligible items
        # ------------------------------------------------------------------
        print("\n[2/9] TEST 2: Multiple eligible candidates batch approval ...")
        payload2 = {
            "review_ids": [r_ids[1], r_ids[2]],
            "reviewer_name": "BatchTestRunner (Auditor)",
            "comment": "TEST-BATCH: Multi-candidate batch approval",
        }
        res2 = client.post("/api/reviews/batch-approve", json=payload2)
        assert res2.status_code == 200, f"Expected 200, got {res2.status_code}: {res2.text}"
        data2 = res2.json()
        assert data2["total_requested"] == 2
        assert data2["approved_count"] == 2
        assert data2["skipped_count"] == 0
        assert len(data2["approved"]) == 2

        # Verify DB and individual audit events
        with cpse_service._get_connection() as conn:
            cur = conn.cursor()
            for rid in [r_ids[1], r_ids[2]]:
                cur.execute("SELECT status FROM reviews WHERE id = ?", (rid,))
                assert cur.fetchone()[0] == "APPROVED"
                cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'APPROVE_MATCH' AND entity_id = ?", (str(rid),))
                assert cur.fetchone()[0] >= 1, f"Missing individual APPROVE_MATCH audit event for review #{rid}"
        print(f"      [OK] Reviews #{r_ids[1]} & #{r_ids[2]} approved with distinct APPROVE_MATCH audit logs.")

        # ------------------------------------------------------------------
        # TEST 3 — Low-confidence item
        # ------------------------------------------------------------------
        print("\n[3/9] TEST 3: Low-confidence candidate skipped (below threshold) ...")
        payload3 = {
            "review_ids": [r_ids[3]],
            "reviewer_name": "BatchTestRunner (Auditor)",
            "comment": "TEST-BATCH: Low confidence should be rejected",
        }
        res3 = client.post("/api/reviews/batch-approve", json=payload3)
        assert res3.status_code == 200
        data3 = res3.json()
        assert data3["approved_count"] == 0
        assert data3["skipped_count"] == 1
        assert len(data3["skipped"]) == 1
        assert data3["skipped"][0]["review_id"] == r_ids[3]
        assert "below" in data3["skipped"][0]["reason"].lower() or "threshold" in data3["skipped"][0]["reason"].lower()

        # Verify DB state: review must remain PENDING
        with cpse_service._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM reviews WHERE id = ?", (r_ids[3],))
            assert cur.fetchone()[0] == "PENDING"
            cur.execute("SELECT COUNT(*) FROM material_mappings WHERE source_material_id = ?", (src_ids[3],))
            assert cur.fetchone()[0] == 0, "Mapping must NOT be created for low-confidence item"
        print(f"      [OK] Low-confidence review #{r_ids[3]} safely skipped: {data3['skipped'][0]['reason']}")

        # ------------------------------------------------------------------
        # TEST 4 — Technical conflict safety
        # ------------------------------------------------------------------
        print("\n[4/9] TEST 4: High numerical score with active domain conflict blocked ...")
        payload4 = {
            "review_ids": [r_ids[4]],
            "reviewer_name": "BatchTestRunner (Auditor)",
            "comment": "TEST-BATCH: Technical conflict check",
        }
        res4 = client.post("/api/reviews/batch-approve", json=payload4)
        assert res4.status_code == 200
        data4 = res4.json()
        assert data4["approved_count"] == 0
        assert data4["skipped_count"] == 1
        assert data4["skipped"][0]["review_id"] == r_ids[4]
        assert "conflict" in data4["skipped"][0]["reason"].lower() or "specification" in data4["skipped"][0]["reason"].lower()

        # Verify DB state: review must remain PENDING for manual review
        with cpse_service._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM reviews WHERE id = ?", (r_ids[4],))
            assert cur.fetchone()[0] == "PENDING"
            cur.execute("SELECT COUNT(*) FROM material_mappings WHERE source_material_id = ?", (src_ids[4],))
            assert cur.fetchone()[0] == 0, "Mapping must NOT be created for conflicted item"
        print(f"      [OK] Conflicted review #{r_ids[4]} safely blocked: {data4['skipped'][0]['reason']}")

        # ------------------------------------------------------------------
        # TEST 5 — Already approved (Idempotency & Double-Click Safety)
        # ------------------------------------------------------------------
        print("\n[5/9] TEST 5: Already approved review skipped (idempotent, 0 duplicate mappings) ...")
        # Submit review 1 which was approved in TEST 1, and review 6 which was pre-approved
        payload5 = {
            "review_ids": [r_ids[0], r_ids[5]],
            "reviewer_name": "BatchTestRunner (Auditor)",
            "comment": "TEST-BATCH: Double-click simulation",
        }
        res5 = client.post("/api/reviews/batch-approve", json=payload5)
        assert res5.status_code == 200
        data5 = res5.json()
        assert data5["approved_count"] == 0
        assert data5["skipped_count"] == 2
        for sk in data5["skipped"]:
            assert "already approved" in sk["reason"].lower()

        # Ensure no duplicate mappings exist in DB
        with cpse_service._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM material_mappings WHERE source_material_id = ?", (src_ids[0],))
            assert cur.fetchone()[0] == 1, "Duplicate mapping created for source item 1!"
            cur.execute("SELECT COUNT(*) FROM material_mappings WHERE source_material_id = ?", (src_ids[5],))
            assert cur.fetchone()[0] == 1, "Duplicate mapping created for source item 6!"
        print(f"      [OK] Idempotency confirmed: already-approved items skipped without duplicate mappings.")

        # ------------------------------------------------------------------
        # TEST 6 — Mixed batch
        # ------------------------------------------------------------------
        print("\n[6/9] TEST 6: Mixed batch partial success reporting ...")
        # 1 eligible (r_ids[6]), 1 low-confidence (r_ids[3]), 1 conflict (r_ids[4]), 1 already approved (r_ids[0])
        mixed_ids = [r_ids[6], r_ids[3], r_ids[4], r_ids[0]]
        payload6 = {
            "review_ids": mixed_ids,
            "reviewer_name": "BatchTestRunner (Auditor)",
            "comment": "TEST-BATCH: Mixed batch validation",
        }
        res6 = client.post("/api/reviews/batch-approve", json=payload6)
        assert res6.status_code == 200
        data6 = res6.json()
        assert data6["total_requested"] == 4
        assert data6["approved_count"] == 1
        assert data6["skipped_count"] == 3
        assert data6["approved"][0]["review_id"] == r_ids[6]

        skipped_map = {s["review_id"]: s["reason"] for s in data6["skipped"]}
        assert r_ids[3] in skipped_map
        assert "below" in skipped_map[r_ids[3]].lower() or "threshold" in skipped_map[r_ids[3]].lower()
        assert r_ids[4] in skipped_map
        assert "conflict" in skipped_map[r_ids[4]].lower() or "specification" in skipped_map[r_ids[4]].lower()
        assert r_ids[0] in skipped_map
        assert "already approved" in skipped_map[r_ids[0]].lower()
        print(f"      [OK] Mixed batch: 1 approved, 3 skipped with granular explanations.")

        # ------------------------------------------------------------------
        # TEST 7 — Audit Trail Integrity
        # ------------------------------------------------------------------
        print("\n[7/9] TEST 7: Audit trail verification (individual APPROVE_MATCH events & zero secrets) ...")
        with cpse_service._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, action, entity_type, entity_id, performed_by, reason, details
                FROM audit_logs
                WHERE action = 'APPROVE_MATCH' AND performed_by LIKE '%BatchTestRunner%'
                """
            )
            audit_rows = cur.fetchall()
            assert len(audit_rows) >= 4, f"Expected at least 4 individual APPROVE_MATCH logs, got {len(audit_rows)}"

            # Verify no secrets in audit logs
            for r in audit_rows:
                row_str = f"{r[0]} {r[1]} {r[2]} {r[3]} {r[4]} {r[5]} {r[6]}"
                for secret_kw in ["password", "token", "secret", "private_key", "bearer"]:
                    assert secret_kw not in row_str.lower() or "[REDACTED" in row_str, f"Potential credential leak: {secret_kw}"
        print(f"      [OK] {len(audit_rows)} distinct APPROVE_MATCH audit logs verified with zero secrets.")

        # ------------------------------------------------------------------
        # TEST 8 — Traceability & Original Code Preservation
        # ------------------------------------------------------------------
        print("\n[8/9] TEST 8: Traceability & Original CPSE code preservation ...")
        with cpse_service._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT m.cpse_name, m.original_material_code, m.original_description,
                       m.canonical_material_code, s.material_code, s.description
                FROM material_mappings m
                JOIN source_materials s ON m.source_material_id = s.id
                WHERE m.original_material_code LIKE 'TEST-BATCH-%'
                """
            )
            mapping_rows = cur.fetchall()
            assert len(mapping_rows) >= 4

            for row in mapping_rows:
                m_cpse, m_orig_code, m_orig_desc, m_can_code, s_code, s_desc = row
                assert m_orig_code == s_code, f"Original material code corrupted! {m_orig_code} != {s_code}"
                assert m_orig_desc == s_desc, f"Original description corrupted! {m_orig_desc} != {s_desc}"
                assert m_can_code.startswith("NMM-"), f"Invalid canonical code: {m_can_code}"
                assert m_cpse in ["ONGC", "BHEL"], f"Unexpected enterprise: {m_cpse}"
        print(f"      [OK] Source codes, descriptions, and CPSE identifiers 100% preserved.")

        # ------------------------------------------------------------------
        # TEST 9 — Frontend UI Markup Verification
        # ------------------------------------------------------------------
        print("\n[9/9] TEST 9: Frontend UI markup verification ...")
        index_html_path = PROJECT_ROOT / "frontend" / "index.html"
        assert index_html_path.exists(), "frontend/index.html not found!"
        content = index_html_path.read_text(encoding="utf-8")

        # Check for batch review controls
        assert "batch-action-toolbar" in content, "Missing batch-action-toolbar in frontend/index.html"
        assert "select-all-eligible" in content, "Missing 'Select All Eligible' checkbox"
        assert "batch-selection-indicator" in content, "Missing batch selection count indicator"
        assert "btn-batch-approve" in content, "Missing batch approval button"
        assert "Approve Selected" in content, "Missing 'Approve Selected' button label"
        assert "review-batch-checkbox" in content, "Missing 'review-batch-checkbox' class"
        assert "/api/reviews/batch-approve" in content, "Missing API endpoint call in frontend JavaScript"
        assert "batchApproveSelected" in content, "Missing batchApproveSelected function"
        assert "High Confidence" in content, "Missing High Confidence indicator in frontend"
        assert "Manual Review Required" in content, "Missing Manual Review Required indicator in frontend"
        print("      [OK] Frontend Review Center markup, checkboxes, and batch toolbar verified.")

        print("\n" + "=" * 80)
        print("ALL 9 BATCH REVIEW TEST CASES PASSED SUCCESSFULLY!")
        print("=" * 80)

    finally:
        # Hermetic cleanup
        teardown_test_batch_records()


if __name__ == "__main__":
    test_batch_review_pipeline()
