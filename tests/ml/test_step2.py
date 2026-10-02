"""
Step 2 Verification Test Suite
Tests all REST endpoints, SQLite data integrity, search, and frontend delivery.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api():
    print("[1/5] Testing GET /api/dataset/status ...")
    r = client.get("/api/dataset/status")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    status = r.json()
    print(f"      Status: loaded={status['loaded']}, records={status['total_records']:,}")
    assert status["loaded"] is True
    assert status["total_records"] == 27188

    print("[2/5] Testing GET /api/dataset/summary ...")
    r = client.get("/api/dataset/summary")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    summary = r.json()
    print(f"      Summary: {summary}")
    assert summary["total_records"] == 27188
    assert summary["total_groups"] == 8811
    assert summary["unique_titles"] == 26303
    assert summary["missing_values"] == 0
    assert summary["duplicate_records"] == 0
    assert summary["minimum_group_size"] == 2
    assert summary["maximum_group_size"] == 51

    print("[3/5] Testing GET /api/dataset/preview (pagination & search) ...")
    r = client.get("/api/dataset/preview?page=1&page_size=5")
    assert r.status_code == 200
    preview = r.json()
    assert len(preview["items"]) == 5
    assert preview["total_records"] == 27188
    print(f"      Preview page 1 returned {len(preview['items'])} items (total {preview['total_records']:,})")

    # Test search
    r = client.get("/api/dataset/preview?search=victoria")
    assert r.status_code == 200
    search_data = r.json()
    print(f"      Search 'victoria' matched {search_data['total_records']} items")
    assert search_data["total_records"] > 0

    print("[4/5] Testing GET /api/dataset/groups ...")
    r = client.get("/api/dataset/groups")
    assert r.status_code == 200
    groups = r.json()
    print(f"      Groups distribution: {groups['distribution']}")
    print(f"      Top 10 largest groups retrieved: count={len(groups['top_groups'])}")
    assert len(groups["distribution"]) == 4
    assert len(groups["top_groups"]) == 10

    print("[5/5] Testing GET / and GET /material-master (Frontend delivery) ...")
    r1 = client.get("/")
    assert r1.status_code == 200
    assert "SIH26099" in r1.text
    assert "Development Benchmark Dataset" in r1.text
    r2 = client.get("/material-master")
    assert r2.status_code == 200
    assert "Material Master (Benchmark Ingestion)" in r2.text

    print("\n" + "=" * 60)
    print("ALL 5 TESTS PASSED SUCCESSFULLY! BACKEND & FRONTEND VERIFIED.")
    print("=" * 60)


if __name__ == "__main__":
    test_api()
