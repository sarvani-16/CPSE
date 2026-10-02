"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Step 5 Test Suite - Human-in-the-Loop Review Center Verification
Description: Validates review lifecycle (Approve, Reject, Needs Review),
             3-column evidence comparison, data governance code preservation,
             and immutable audit logging.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from fastapi.testclient import TestClient
from main import app
from backend.app.cpse.review_service import get_review_service
from backend.app.cpse.service import get_cpse_service

client = TestClient(app)


def test_review_center_pipeline():
    print("=" * 75)
    print("SIH26099 Step 5 Verification: Human-in-the-Loop Review Center")
    print("=" * 75)

    # 1. Test GET /api/health includes review center
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    assert "Human-in-the-Loop Review Center" in health_data["features"]
    print("[OK] 1. Health check verifies Human-in-the-Loop Review Center feature active.")

    # 2. Test GET /api/reviews (all items)
    res = client.get("/api/reviews")
    assert res.status_code == 200, f"GET /api/reviews failed: {res.text}"
    data = res.json()
    total = data["total"]
    counts = data["counts"]
    items = data["items"]

    assert total > 0, "No reviews returned!"
    assert len(items) > 0, "Item list is empty!"
    print(f"[OK] 2. GET /api/reviews retrieved {total} candidate items. Status distribution: {counts}")

    # Inspect first item for 3-column requirements
    item = items[0]
    review_id = item["id"]

    # Verify LEFT Column: Source Material
    assert "source" in item, "Missing source material in review item"
    src = item["source"]
    assert "cpse_name" in src and src["cpse_name"], "Missing cpse_name"
    assert "material_code" in src and src["material_code"], "Missing original material_code"
    assert "description" in src and src["description"], "Missing original description"
    assert "specification" in src, "Missing specification"
    assert "unit_of_measure" in src, "Missing unit_of_measure"
    print(f"[OK] 3. Left Column (Source Material) validated:")
    print(f"     - CPSE: {src['cpse_name']} | Code: {src['material_code']}")
    print(f"     - Description: {src['description']}")
    print(f"     - Specification: {src['specification']} | UOM: {src['unit_of_measure']}")

    # Verify CENTER Column: AI Comparison & Evidence
    assert "ai_comparison" in item, "Missing AI comparison in review item"
    ai = item["ai_comparison"]
    assert "semantic_score" in ai and isinstance(ai["semantic_score"], float)
    assert "fuzzy_score" in ai and isinstance(ai["fuzzy_score"], float)
    assert "lexical_score" in ai and isinstance(ai["lexical_score"], float)
    assert "hybrid_score" in ai and isinstance(ai["hybrid_score"], float)
    assert "detected_attributes" in ai
    assert "conflicts" in ai
    assert "explanation" in ai and len(ai["explanation"]) > 0
    print(f"[OK] 4. Center Column (AI Comparison) validated:")
    print(f"     - Scores: Hybrid={ai['hybrid_score']:.4f} | Semantic={ai['semantic_score']:.4f} | Fuzzy={ai['fuzzy_score']:.4f} | Lexical={ai['lexical_score']:.4f}")
    print(f"     - Detected Attributes: {ai['detected_attributes'].get('matching', [])}")
    print(f"     - Conflicts Detected: {ai['conflicts']}")
    print(f"     - Explanations: {ai['explanation'][:2]}")

    # Verify RIGHT Column: Recommended Canonical Material
    assert "canonical" in item, "Missing canonical material in review item"
    can = item["canonical"]
    assert "canonical_code" in can and (can["canonical_code"].startswith("NMM-") or can["canonical_code"].startswith("NAT-"))
    assert "canonical_description" in can and can["canonical_description"]
    assert "category" in can
    assert "standard_specification" in can
    print(f"[OK] 5. Right Column (Canonical Material) validated:")
    print(f"     - Common National Code: {can['canonical_code']}")
    print(f"     - Standardized Desc: {can['canonical_description']}")
    print(f"     - Category: {can['category']}")
    print(f"     - Standard Specs: {can['standard_specification']}")

    # 6. Test Action: POST /api/reviews/{id}/request-review
    demo_reviewer = "Govt Reviewer (Demo Auditor: audit.officer@cpse.gov.in)"
    comment_req = "Requires metallurgical chemical composition review for valve trim."
    res = client.post(
        f"/api/reviews/{review_id}/request-review",
        json={"reviewer_name": demo_reviewer, "comment": comment_req},
    )
    assert res.status_code == 200, f"request-review failed: {res.text}"
    req_data = res.json()
    assert req_data["action"] == "NEEDS_REVIEW"
    print(f"[OK] 6. Action POST /api/reviews/{review_id}/request-review succeeded. Status -> NEEDS_REVIEW")

    # 7. Test Action: POST /api/reviews/{id}/reject
    comment_rej = "Dimensional tolerance discrepancy with standard specification."
    res = client.post(
        f"/api/reviews/{review_id}/reject",
        json={"reviewer_name": demo_reviewer, "comment": comment_rej},
    )
    assert res.status_code == 200, f"reject failed: {res.text}"
    rej_data = res.json()
    assert rej_data["action"] == "REJECTED"
    print(f"[OK] 7. Action POST /api/reviews/{review_id}/reject succeeded. Status -> REJECTED")

    # 8. Test Action: POST /api/reviews/{id}/approve
    comment_app = "Confirmed ISO 4014 and DIN standard dimensions. Approved by engineering."
    res = client.post(
        f"/api/reviews/{review_id}/approve",
        json={"reviewer_name": demo_reviewer, "comment": comment_app},
    )
    assert res.status_code == 200, f"approve failed: {res.text}"
    app_data = res.json()
    assert app_data["action"] == "APPROVED"
    assert "mapping_id" in app_data
    print(f"[OK] 8. Action POST /api/reviews/{review_id}/approve succeeded. Status -> APPROVED (Mapping ID: {app_data['mapping_id']})")

    # 9. Test Data Governance Rule: Source material code MUST BE PRESERVED in material_mappings
    res = client.get("/api/materials/mappings")
    assert res.status_code == 200
    mappings = res.json()["items"]
    assert len(mappings) > 0, "No mappings found after approval!"

    matching_map = next((m for m in mappings if m["id"] == app_data["mapping_id"]), None)
    assert matching_map is not None, "Created mapping not found in list!"
    assert matching_map["original_material_code"] == src["material_code"]
    assert matching_map["original_description"] == src["description"]
    assert matching_map["canonical_material_code"] == can["canonical_code"]
    assert matching_map["match_status"] == "APPROVED"
    assert matching_map["reviewer"] == demo_reviewer
    print(f"[OK] 9. Data Governance Invariant Verified in material_mappings:")
    print(f"     - CPSE: {matching_map['cpse_name']}")
    print(f"     - Original Code (PRESERVED): {matching_map['original_material_code']}")
    print(f"     - Original Desc (PRESERVED): {matching_map['original_description']}")
    print(f"     - Common National Code:     {matching_map['canonical_material_code']}")
    print(f"     - Canonical Desc:            {matching_map['canonical_description']}")
    print(f"     - Status:                    {matching_map['match_status']}")
    print(f"     - Reviewer Identity:         {matching_map['reviewer']}")

    # 10. Test Audit Logs: Ensure all review actions were recorded immutably
    res = client.get("/api/materials/audit-logs?limit=10")
    assert res.status_code == 200
    audit_logs = res.json()
    actions = [a["action"] for a in audit_logs]
    assert "APPROVE_MATCH" in actions, "APPROVE_MATCH action missing in audit logs!"
    assert "REJECT_MATCH" in actions, "REJECT_MATCH action missing in audit logs!"
    assert "REQUEST_FURTHER_REVIEW" in actions, "REQUEST_FURTHER_REVIEW action missing in audit logs!"
    print(f"[OK] 10. Immutable Audit Trail verified in audit_logs:")
    for entry in audit_logs[:3]:
        print(f"     - [{entry['timestamp']}] Action: {entry['action']} | User: {entry['user']} | Entity: {entry['entity_type']}#{entry['entity_id']}")

    # 11. Test Filtering by Status
    res_pending = client.get("/api/reviews?status=PENDING")
    assert res_pending.status_code == 200
    res_approved = client.get("/api/reviews?status=APPROVED")
    assert res_approved.status_code == 200
    assert any(it["id"] == review_id for it in res_approved.json()["items"])
    print(f"[OK] 11. Status filtering verified (PENDING items: {res_pending.json()['total']}, APPROVED items: {res_approved.json()['total']}).")

    print("\n" + "=" * 75)
    print("ALL STEP 5 HUMAN-IN-THE-LOOP REVIEW CENTER TESTS PASSED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_review_center_pipeline()
