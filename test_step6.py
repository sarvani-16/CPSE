"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: Step 6 Test Suite - Canonical Material & Common National Material Code Verification
Description: Validates deterministic NMM-XXXXXX prototype codes,
             multi-enterprise CPSE mapping provenance, traceability tree,
             and REST API endpoints.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_canonical_materials_pipeline():
    print("=" * 75)
    print("SIH26099 Step 6 Verification: Canonical Material & NMM Prototype Series")
    print("=" * 75)

    # 1. Health check verification
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    features = res.json()["features"]
    assert "Canonical National Material Master (NMM Series)" in features
    assert "Cross-Enterprise Traceability" in features
    print("[OK] 1. Health check verifies Canonical Material Master & Traceability features.")

    # 2. Test GET /api/canonical-materials (List)
    res = client.get("/api/canonical-materials")
    assert res.status_code == 200, f"GET /api/canonical-materials failed: {res.text}"
    data = res.json()
    total = data["total"]
    items = data["items"]

    assert total >= 8, f"Expected at least 8 canonical items, got {total}"
    assert len(items) >= 8, f"Item count mismatch: {len(items)}"
    assert data["code_type"] == "Prototype Common Material Code"
    assert "NOT an official government material code" in data["disclaimer"]
    print(f"[OK] 2. GET /api/canonical-materials returned {total} prototype canonical items.")
    print(f"     - Label: {data['code_type']}")
    print(f"     - Disclaimer: {data['disclaimer'][:80]}...")

    # 3. Verify Deterministic Code Format (NMM-000001, NMM-000002, etc.)
    code_pattern = re.compile(r"^NMM-\d{6}$")
    for it in items:
        code = it["national_material_code"]
        assert code_pattern.match(code), f"Invalid code format: {code}"
        assert it["code_type_label"] == "Prototype Common Material Code"
        assert it["standardized_description"] and len(it["standardized_description"]) > 10
        assert it["category"]
        assert it["material_type"]
        assert isinstance(it["technical_attributes"], dict)
        assert it["approval_status"] in ["APPROVED", "PENDING", "NEEDS_REVIEW"]
    print("[OK] 3. Deterministic code format verified (NMM-000001 through NMM-000008).")

    # 4. Verify Multi-CPSE Provenance Mapping (e.g. NMM-000001 maps to both ONGC and BHEL)
    bolt_item = next((it for it in items if it["national_material_code"] == "NMM-000001"), None)
    assert bolt_item is not None, "NMM-000001 item missing!"
    assert "ONGC" in bolt_item["mapped_cpses"], "ONGC missing from mapped CPSEs"
    assert "BHEL" in bolt_item["mapped_cpses"], "BHEL missing from mapped CPSEs"
    assert "ONGC-BLT-1001" in bolt_item["original_codes"], "ONGC-BLT-1001 missing"
    assert "BHEL-MEC-001" in bolt_item["original_codes"], "BHEL-MEC-001 missing"
    print(f"[OK] 4. Multi-CPSE Mapping Provenance verified for NMM-000001:")
    print(f"     - Common Code: {bolt_item['national_material_code']}")
    print(f"     - Description: {bolt_item['standardized_description']}")
    print(f"     - Mapped CPSEs: {bolt_item['mapped_cpses']}")
    print(f"     - Original Codes: {bolt_item['original_codes']}")
    print(f"     - Confidence: {bolt_item['confidence']}")

    # 5. Test Filters: Category & Search
    res_cat = client.get("/api/canonical-materials?category=Fasteners%20%26%20Mechanical%20Hardware")
    assert res_cat.status_code == 200
    cat_items = res_cat.json()["items"]
    assert len(cat_items) >= 2
    assert all(it["category"] == "Fasteners & Mechanical Hardware" for it in cat_items)
    print(f"[OK] 5. Category filter verified: {len(cat_items)} Fasteners items found.")

    res_search = client.get("/api/canonical-materials?search=SS316")
    assert res_search.status_code == 200
    search_items = res_search.json()["items"]
    assert len(search_items) >= 2  # SS316 Bolt, Pump Impeller, Ball Valve trim
    print(f"[OK] 6. Search filter verified: {len(search_items)} items matched query 'SS316'.")

    # 6. Test GET /api/canonical-materials/{id} (Detail & Traceability Tree)
    res_detail = client.get("/api/canonical-materials/NMM-000001")
    assert res_detail.status_code == 200, f"Detail lookup failed: {res_detail.text}"
    detail = res_detail.json()

    assert detail["national_material_code"] == "NMM-000001"
    assert "traceability_tree" in detail
    tree = detail["traceability_tree"]
    assert tree["common_code"] == "NMM-000001"
    assert tree["code_type"] == "Prototype Common Material Code"
    assert "branches" in tree and len(tree["branches"]) >= 2

    # Verify Traceability Hierarchy:
    # Common Code -> Canonical Description -> CPSE A -> Original Code, CPSE B -> Original Code
    branches_by_cpse = {b["cpse_name"]: b for b in tree["branches"]}
    assert "ONGC" in branches_by_cpse
    assert "BHEL" in branches_by_cpse
    ongc_branch = branches_by_cpse["ONGC"]
    bhel_branch = branches_by_cpse["BHEL"]

    assert ongc_branch["original_code"] == "ONGC-BLT-1001"
    assert bhel_branch["original_code"] == "BHEL-MEC-001"
    assert ongc_branch["match_status"] == "APPROVED"
    assert bhel_branch["match_status"] == "APPROVED"

    print("[OK] 7. Complete Traceability Tree verified:")
    print(f"     Common Code: {tree['common_code']} ({tree['code_type']})")
    print(f"     |")
    print(f"     v")
    print(f"     Canonical Description: {tree['canonical_description']}")
    print(f"     |")
    print(f"     v")
    for b in tree["branches"]:
        print(f"     [{b['cpse_name']}] -> Original Code: {b['original_code']} (Desc: '{b['original_description']}', UOM: {b['unit_of_measure']}, Conf: {b['confidence']})")

    # 7. Test Lookup by Numeric ID
    numeric_id = detail["id"]
    res_num = client.get(f"/api/canonical-materials/{numeric_id}")
    assert res_num.status_code == 200
    assert res_num.json()["national_material_code"] == "NMM-000001"
    print(f"[OK] 8. Lookup by integer ID #{numeric_id} succeeded.")

    # 8. Test 404 for Non-Existent Identifier
    res_404 = client.get("/api/canonical-materials/NMM-999999")
    assert res_404.status_code == 404
    print("[OK] 9. 404 error correctly returned for non-existent canonical code.")

    print("\n" + "=" * 75)
    print("ALL STEP 6 CANONICAL MATERIAL & TRACEABILITY TESTS PASSED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_canonical_materials_pipeline()
