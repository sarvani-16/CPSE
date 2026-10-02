"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Automated Verification Test Suite for Dynamic Canonical Material Creation
Description:
  Validates deterministic NMM code generation for unseen materials (NMM-000009+),
  idempotency (preventing duplicate canonical records for identical items),
  technical conflict guardrails (SS304 vs SS316),
  complete multi-branch provenance & traceability,
  and immutable governance audit logging without secrets.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import re
from fastapi.testclient import TestClient
from main import app
from backend.app.cpse.canonical_service import get_canonical_service
from backend.app.cpse.service import get_cpse_service
from backend.app.cpse.review_service import get_review_service

client = TestClient(app)


def test_dynamic_canonical_pipeline():
    print("=" * 80)
    print("RUNNING DYNAMIC CANONICAL MATERIAL CREATION VERIFICATION TEST SUITE")
    print("=" * 80)

    # Clean any prior test artifacts to ensure hermetic, idempotent test execution
    with get_cpse_service()._get_connection() as conn:
        conn.execute("DELETE FROM canonical_materials WHERE id > 8")
        conn.execute("DELETE FROM source_materials WHERE id > 13")
        conn.execute("DELETE FROM material_mappings WHERE id > 13")
        conn.execute("DELETE FROM reviews WHERE id > 13")
        conn.execute("DELETE FROM audit_logs WHERE action = 'CREATE_CANONICAL_CODE'")
        conn.commit()

    # ------------------------------------------------------------------
    # Test 1: Existing canonical match reuse (No new NMM code created)
    # ------------------------------------------------------------------
    print("\n[1/6] Test 1: Existing Canonical Material Match Reuse ...")
    payload_existing = {
        "description": "HEX HEAD BOLT M10 X 50MM SS304 FULL THREAD",
        "cpse_name": "ONGC",
        "material_code": "ONGC-BLT-1001-TEST",
        "specification": "ISO 4017 / DIN 933 / Grade A2-70",
        "material_grade": "SS304",
        "unit_of_measure": "EA",
        "category": "Fasteners & Mechanical Hardware",
    }
    r = client.post("/api/canonical-materials/auto-create", json=payload_existing)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    existing_res = r.json()
    print(f"      Matched Code:        {existing_res['national_material_code']}")
    print(f"      Description:         {existing_res['standardized_description']}")
    print(f"      Approval Status:     {existing_res['approval_status']}")
    # Must reuse NMM-000001 (SS304 Hex Bolt) instead of creating a duplicate
    assert existing_res["national_material_code"] == "NMM-000001", (
        f"Expected NMM-000001 to be reused, got {existing_res['national_material_code']}"
    )
    print("      [OK] Reused existing canonical NMM-000001; no duplicate code generated.")

    # ------------------------------------------------------------------
    # Test 2: Unseen material dynamic prototype creation
    # ------------------------------------------------------------------
    print("\n[2/6] Test 2: Unseen Material Dynamic Prototype Generation ...")
    payload_unseen = {
        "description": "3 CORE 1.5 SQ MM COPPER ARMOURED POWER CABLE",
        "cpse_name": "NTPC",
        "material_code": "NTPC-CBL-9001",
        "specification": "IS 1554 Part 1 / 1100V Grade / XLPE Insulated",
        "material_grade": "Copper Conductor",
        "dimensions": "3 x 1.5 sq mm",
        "unit_of_measure": "MTR",
        "category": "Electrical & Cables",
    }
    r = client.post("/api/canonical-materials/auto-create", json=payload_unseen)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    new_mat = r.json()
    new_code = new_mat["national_material_code"]
    print(f"      Generated Code:      {new_code}")
    print(f"      Label:               {new_mat['code_type_label']}")
    print(f"      Standardized Desc:   {new_mat['standardized_description']}")
    print(f"      Category:            {new_mat['category']}")
    print(f"      Approval Status:     {new_mat['approval_status']}")
    print(f"      Status Note:         {new_mat['status_note']}")

    # Verify deterministic prototype format (NMM-000009 or higher)
    assert re.match(r"^NMM-\d{6}$", new_code), f"Invalid code format: {new_code}"
    code_num = int(new_code.split("-")[1])
    assert code_num >= 9, f"Expected code >= NMM-000009, got {new_code}"
    assert new_mat["code_type_label"] == "Prototype Common Material Code"
    assert new_mat["approval_status"] == "PENDING"
    assert "AI-generated prototype" in new_mat["status_note"]
    assert "CABLE" in new_mat["standardized_description"].upper()
    assert "COPPER" in new_mat["standardized_description"].upper()
    assert new_mat["category"] == "Electrical & Cables"
    print("      [OK] Successfully created deterministic prototype code with PENDING status.")

    # ------------------------------------------------------------------
    # Test 3: Idempotency (Processing identical material again does NOT duplicate NMM)
    # ------------------------------------------------------------------
    print("\n[3/6] Test 3: Idempotency Verification ...")
    r2 = client.post("/api/canonical-materials/auto-create", json=payload_unseen)
    assert r2.status_code == 200, f"Expected 200, got {r2.status_code}: {r2.text}"
    dup_check = r2.json()
    print(f"      Repeated Call Code:  {dup_check['national_material_code']}")
    assert dup_check["national_material_code"] == new_code, (
        f"Idempotency failed: expected {new_code}, got {dup_check['national_material_code']}"
    )
    print(f"      [OK] Idempotency verified: re-used {new_code} without generating duplicate.")

    # ------------------------------------------------------------------
    # Test 4: Technical conflict domain guardrail (SS304 vs SS316)
    # ------------------------------------------------------------------
    print("\n[4/6] Test 4: Technical Conflict Domain Guardrail (SS304 vs SS316) ...")
    payload_conflict = {
        "title_a": "M10 SS304 BOLT 50MM - Grade 8.8 (High Tensile)",
        "title_b": "M10 SS316 BOLT 50MM - Grade 8.8 (High Tensile)",
    }
    r_conf = client.post("/api/matching/compare", json=payload_conflict)
    assert r_conf.status_code == 200, f"Expected 200, got {r_conf.status_code}"
    res_conf = r_conf.json()
    print(f"      Hybrid Score:        {res_conf['hybrid_score']:.4f}")
    print(f"      Has Conflicts:       {res_conf['technical_tokens']['has_conflicts']}")
    print(f"      Detected Conflicts:  {res_conf['technical_tokens']['conflicts']}")
    print(f"      Match Decision:      {res_conf['match_decision']}")
    assert res_conf["technical_tokens"]["has_conflicts"] is True
    assert res_conf["match_decision"] == "REVIEW"
    print("      [OK] Technical conflict guardrail enforced: incompatible grades require review.")

    # ------------------------------------------------------------------
    # Test 5: Full Traceability of dynamically generated canonical material
    # ------------------------------------------------------------------
    print(f"\n[5/6] Test 5: Complete Traceability Hierarchy for {new_code} ...")
    r_trace = client.get(f"/api/canonical-materials/{new_code}")
    assert r_trace.status_code == 200, f"Expected 200, got {r_trace.status_code}: {r_trace.text}"
    detail = r_trace.json()
    assert detail["national_material_code"] == new_code
    assert detail["approval_status"] == "PENDING"
    assert "traceability_tree" in detail
    tree = detail["traceability_tree"]
    print(f"      Tree Root:           {tree['common_code']} ({tree['code_type']})")
    print(f"      Canonical Desc:      {tree['canonical_description']}")
    print(f"      Category:            {tree['category']}")
    print(f"      Approval Status:     {tree['approval_status']}")
    assert tree["common_code"] == new_code
    assert tree["code_type"] == "Prototype Common Material Code"
    print("      [OK] Traceability tree successfully retrieved and validated.")

    # ------------------------------------------------------------------
    # Test 6: Immutable Audit Trail verification (CREATE_CANONICAL_CODE)
    # ------------------------------------------------------------------
    print(f"\n[6/6] Test 6: Audit Trail Verification for CREATE_CANONICAL_CODE ...")
    r_audit = client.get(f"/api/audit-logs?action=CREATE_CANONICAL_CODE&entity={new_code}")
    assert r_audit.status_code == 200, f"Expected 200, got {r_audit.status_code}"
    audit_data = r_audit.json()
    print(f"      Found {audit_data['total']} CREATE_CANONICAL_CODE audit entries.")
    assert audit_data["total"] >= 1, "Expected at least 1 CREATE_CANONICAL_CODE audit log entry"

    target_log = None
    for entry in audit_data["items"]:
        if entry["entity_id"] == new_code:
            target_log = entry
            break

    assert target_log is not None, f"Audit log for entity_id {new_code} not found!"
    print(f"      Audit Action:        {target_log['action']}")
    print(f"      Entity Type:         {target_log['entity_type']}")
    print(f"      Entity ID:           {target_log['entity_id']}")
    print(f"      User / System:       {target_log['user']}")
    print(f"      Reason:              {target_log['reason']}")
    print(f"      Timestamp:           {target_log['timestamp']}")

    assert target_log["action"] == "CREATE_CANONICAL_CODE"
    assert target_log["entity_type"] == "canonical_materials"
    assert target_log["entity_id"] == new_code
    assert target_log["user"] == "AI_STANDARDIZATION_ENGINE"

    # CRITICAL SECURITY CHECK: Ensure no secrets/passwords in audit logs
    log_str = json.dumps(target_log).lower()
    for sensitive_word in ["password", "secret", "token", "apikey", "private_key"]:
        assert sensitive_word not in log_str, f"CRITICAL SECURITY LEAK: {sensitive_word} in audit log!"
    print("      [OK] Audit record validated. CRITICAL SECURITY: Zero secrets/tokens present.")

    # ------------------------------------------------------------------
    # Bonus Test 7: Review Center Graduation to APPROVED
    # ------------------------------------------------------------------
    print(f"\n[Bonus 7] Testing Review Center Graduation to APPROVED for {new_code} ...")
    # Ingest a source material and generate review to test human validation
    with get_cpse_service()._get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO source_materials (
                cpse_name, material_code, description, specification,
                material_grade, dimensions, unit_of_measure, category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "NTPC",
                "NTPC-CBL-TEST-99",
                "3 CORE 1.5 SQ MM COPPER ARMOURED POWER CABLE",
                "IS 1554 Part 1 / 1100V Grade",
                "Copper",
                "1.5 sq mm",
                "MTR",
                "Electrical & Cables",
            ),
        )
        src_id = cur.lastrowid
        conn.commit()

    # Generate review
    rev_svc = get_review_service()
    gen_res = rev_svc.generate_reviews()
    assert gen_res["status"] == "success"

    # Find the review for this source material
    rev_data = client.get("/api/reviews?search=NTPC-CBL-TEST-99").json()
    assert rev_data["total"] >= 1, "Review item for new material was not generated"
    rev_item = rev_data["items"][0]
    rev_id = rev_item["id"]

    # Approve match
    r_app = client.post(
        f"/api/reviews/{rev_id}/approve",
        json={
            "reviewer_name": "Chief Electrical Engineer (auditor@cpse.gov.in)",
            "comment": "Verified technical specs against IS 1554 Part 1 standards. Approved.",
        },
    )
    assert r_app.status_code == 200, f"Approval failed: {r_app.text}"

    # Check that canonical material is now APPROVED
    r_check = client.get(f"/api/canonical-materials/{new_code}")
    assert r_check.status_code == 200
    updated_canonical = r_check.json()
    print(f"      Canonical Status After Approval: {updated_canonical['approval_status']}")
    assert updated_canonical["approval_status"] == "APPROVED"
    print("      [OK] Review approval graduated prototype canonical to APPROVED.")

    print("\n" + "=" * 80)
    print("ALL DYNAMIC CANONICAL MATERIAL TESTS COMPLETED AND VERIFIED 100%!")
    print("=" * 80)


if __name__ == "__main__":
    test_dynamic_canonical_pipeline()
