"""
Step 4 Verification Test Suite: CPSE Material Master, CSV/XLSX Upload, Column Auto-Mapping, and Governance
"""

from pathlib import Path
from fastapi.testclient import TestClient
from main import app
from backend.app.cpse.service import get_cpse_service

client = TestClient(app)
cpse_service = get_cpse_service()


def test_step4_pipeline():
    print("=" * 75)
    print("RUNNING STEP 4 AUTOMATED VERIFICATION TEST SUITE (CPSE MATERIAL MASTER)")
    print("=" * 75)

    # 1. Verify 6 Core Governance Tables in SQLite
    print("\n[1/6] Verifying 6 Database Tables in cpse_master.db ...")
    with cpse_service._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = set(r[0] for r in cur.fetchall())
        expected = {
            "source_materials",
            "canonical_materials",
            "material_mappings",
            "match_candidates",
            "reviews",
            "audit_logs",
        }
        for t in expected:
            assert t in tables, f"Missing expected table: {t}"
            print(f"      [OK] Table exists: {t}")

    # 2. Test POST /api/materials/upload (Dry Run - Column Auto-Detection)
    print("\n[2/6] Testing POST /api/materials/upload (dry_run=True, ONGC CSV Format) ...")
    csv_path = Path("dataset/sample_cpse_data/cpse_a_ongc.csv")
    with open(csv_path, "rb") as f:
        r = client.post(
            "/api/materials/upload",
            files={"file": ("cpse_a_ongc.csv", f, "text/csv")},
            data={"cpse_name": "ONGC", "dry_run": "true"},
        )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    preview_data = r.json()
    print(f"      Filename:           {preview_data['filename']}")
    print(f"      Detected Columns:   {preview_data['detected_columns']}")
    print(f"      Suggested Mappings: {preview_data['suggested_mappings']}")
    print(f"      Is Valid:           {preview_data['is_valid']}")
    assert preview_data["is_valid"] is True
    assert preview_data["suggested_mappings"]["MAT_CODE"] == "material_code"
    assert preview_data["suggested_mappings"]["MAT_DESC"] == "description"
    assert preview_data["suggested_mappings"]["UOM"] == "unit_of_measure"

    # 3. Test POST /api/materials/upload (Execution - Ingest BHEL Excel Format)
    print("\n[3/6] Testing POST /api/materials/upload (dry_run=False, BHEL XLSX Format) ...")
    xlsx_path = Path("dataset/sample_cpse_data/cpse_b_bhel.xlsx")
    with open(xlsx_path, "rb") as f:
        r = client.post(
            "/api/materials/upload",
            files={"file": ("cpse_b_bhel.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"cpse_name": "BHEL", "dry_run": "false"},
        )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    import_data = r.json()
    print(f"      CPSE Name:     {import_data['cpse_name']}")
    print(f"      Rows Imported: {import_data['rows_imported']}")
    print(f"      Rows Skipped:  {import_data['rows_skipped']}")
    assert import_data["status"] == "success"
    assert import_data["rows_imported"] > 0

    # 4. Test GET /api/materials/source
    print("\n[4/6] Testing GET /api/materials/source ...")
    r = client.get("/api/materials/source?cpse_name=BHEL")
    assert r.status_code == 200
    source_items = r.json()
    print(f"      BHEL Items in Catalog: {source_items['total']}")
    sample = source_items["items"][0]
    print(f"      Sample Item: [{sample['material_code']}] {sample['description']} (UOM: {sample['unit_of_measure']})")
    assert "BHEL" in sample["material_code"]
    assert sample["cpse_name"] == "BHEL"

    # 5. Test Data Governance Rule: Original Codes Preserved
    print("\n[5/6] Testing Data Governance Rule: Original Code Preservation ...")
    with cpse_service._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT cpse_name, material_code, description, unit_of_measure FROM source_materials")
        rows = cur.fetchall()
        print(f"      Total Preserved CPSE Materials: {len(rows)}")
        for r in rows[:3]:
            print(f"        -> Enterprise: {r[0]} | Code: {r[1]} | Desc: {r[2]}")
        assert len(rows) > 0

    # 6. Test GET /api/materials/audit-logs
    print("\n[6/6] Testing GET /api/materials/audit-logs ...")
    r = client.get("/api/materials/audit-logs")
    assert r.status_code == 200
    logs = r.json()
    print(f"      Audit Logs Recorded: {len(logs)}")
    assert len(logs) > 0
    print(f"      Latest Action: {logs[0]['action']} by {logs[0]['user']} at {logs[0]['timestamp']}")

    print("\n" + "=" * 75)
    print("ALL STEP 4 TESTS PASSED SUCCESSFULLY! CPSE MASTER LAYER VERIFIED.")
    print("=" * 75)


if __name__ == "__main__":
    test_step4_pipeline()
