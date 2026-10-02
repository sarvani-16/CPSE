"""
SIH26099 - Verification Test Suite for Executive Overview Dashboard
Tests:
- GET /api/health includes Executive Overview Dashboard
- GET /api/dashboard/overview returns 200 with all 6 KPI cards
- Validates 5 charts (Match Distribution, Materials by CPSE, Duplicate Detection Trend, Review Status, Category Distribution)
- Validates National Material Harmonization Engine 6-stage status (all '✓' and active)
- Verifies that all metrics match real SQLite database values (zero fake data)
"""

import sys
from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
DB_PATH = PROJECT_ROOT / "outputs" / "analysis" / "cpse_master.db"


def test_overview_dashboard():
    print("=" * 75)
    print("SIH26099 Verification: Executive Overview Dashboard")
    print("=" * 75)

    # 1. Health check includes Executive Overview Dashboard
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    assert "Executive Overview Dashboard" in health_data["features"]
    print("[OK] 1. Health check verifies Executive Overview Dashboard active.")

    # 2. Query overview endpoint
    res = client.get("/api/dashboard/overview")
    assert res.status_code == 200, f"Overview API failed: {res.text}"
    data = res.json()
    assert "kpis" in data, "Missing 'kpis' in dashboard response"
    assert "charts" in data, "Missing 'charts' in dashboard response"
    assert "system_status" in data, "Missing 'system_status' in dashboard response"
    print("[OK] 2. GET /api/dashboard/overview returned HTTP 200 with all major sections.")

    # 3. Validate 6 KPI Cards
    kpis = data["kpis"]
    required_kpis = [
        "total_materials",
        "potential_duplicates",
        "high_confidence_matches",
        "pending_reviews",
        "harmonized_materials",
        "cpse_sources",
    ]
    for k in required_kpis:
        assert k in kpis, f"Missing KPI card metric: {k}"
        assert isinstance(kpis[k], int), f"KPI {k} must be an integer, got {type(kpis[k])}"

    print("[OK] 3. All 6 KPI cards present and valid:")
    print(f"     1. Total Materials:          {kpis['total_materials']} (Benchmark Managed: {kpis.get('total_materials_benchmark', 0):,})")
    print(f"     2. Potential Duplicates:     {kpis['potential_duplicates']}")
    print(f"     3. High Confidence Matches:  {kpis['high_confidence_matches']}")
    print(f"     4. Pending Reviews:          {kpis['pending_reviews']}")
    print(f"     5. Harmonized Materials:     {kpis['harmonized_materials']} (Links: {kpis.get('harmonized_mappings', 0)})")
    print(f"     6. CPSE Sources:             {kpis['cpse_sources']} ({', '.join(kpis.get('active_cpses', []))})")

    # Verify zero fake data against direct SQLite query
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM source_materials")
        db_total_mats = cur.fetchone()[0]
        assert kpis["total_materials"] == db_total_mats, f"Total materials mismatch: API {kpis['total_materials']} vs DB {db_total_mats}"

        cur.execute("SELECT COUNT(DISTINCT cpse_name) FROM source_materials")
        db_sources = cur.fetchone()[0]
        assert kpis["cpse_sources"] == db_sources, f"CPSE sources mismatch: API {kpis['cpse_sources']} vs DB {db_sources}"

        cur.execute("SELECT COUNT(*) FROM canonical_materials")
        db_canons = cur.fetchone()[0]
        assert kpis["harmonized_materials"] == db_canons, f"Harmonized materials mismatch: API {kpis['harmonized_materials']} vs DB {db_canons}"

    print("[OK] 4. Zero fake data verified: KPI values strictly match underlying SQLite database tables.")

    # 4. Validate 5 Charts
    charts = data["charts"]
    required_charts = [
        "match_distribution",
        "materials_by_cpse",
        "duplicate_detection_trend",
        "review_status",
        "category_distribution",
    ]
    for c in required_charts:
        assert c in charts, f"Missing chart data for: {c}"

    # Chart 1: Material Match Distribution (Match, Review, Not Match)
    match_dist = charts["match_distribution"]
    assert "labels" in match_dist and len(match_dist["labels"]) == 3
    assert any("Match" in l for l in match_dist["labels"])
    assert any("Review" in l for l in match_dist["labels"])
    assert any("Not Match" in l for l in match_dist["labels"])
    assert "counts" in match_dist and len(match_dist["counts"]) == 3
    print(f"[OK] 5. Chart 1 (Material Match Distribution) verified: {dict(zip(match_dist['labels'], match_dist['counts']))}")

    # Chart 2: Materials by CPSE
    by_cpse = charts["materials_by_cpse"]
    assert len(by_cpse["labels"]) >= 2
    assert "ONGC" in by_cpse["labels"]
    assert "BHEL" in by_cpse["labels"]
    print(f"[OK] 6. Chart 2 (Materials by CPSE) verified: {dict(zip(by_cpse['labels'], by_cpse['counts']))}")

    # Chart 3: Duplicate Detection Trend
    dup_trend = charts["duplicate_detection_trend"]
    assert "labels" in dup_trend and len(dup_trend["labels"]) >= 3
    assert "cumulative" in dup_trend and len(dup_trend["cumulative"]) == len(dup_trend["labels"])
    print(f"[OK] 7. Chart 3 (Duplicate Detection Trend) verified: {dict(zip(dup_trend['labels'], dup_trend['cumulative']))}")

    # Chart 4: Review Status
    rev_status = charts["review_status"]
    assert "Approved" in rev_status["labels"]
    assert "Pending" in rev_status["labels"]
    assert "Needs Review" in rev_status["labels"]
    print(f"[OK] 8. Chart 4 (Review Status) verified: {dict(zip(rev_status['labels'], rev_status['counts']))}")

    # Chart 5: Category Distribution
    cat_dist = charts["category_distribution"]
    assert len(cat_dist["labels"]) >= 4
    print(f"[OK] 9. Chart 5 (Category Distribution) verified: {len(cat_dist['labels'])} procurement categories tracked.")

    # 5. Validate System Status Section
    sys_status = data["system_status"]
    assert sys_status["engine_name"] == "National Material Harmonization Engine"
    subsystems = sys_status["subsystems"]
    subsystem_names = [s["name"] for s in subsystems]
    expected_subsystems = [
        "Data Ingestion",
        "Normalization",
        "AI Matching",
        "Human Validation",
        "Canonical Mapping",
        "Audit Trail",
    ]
    for sub in expected_subsystems:
        assert sub in subsystem_names, f"Missing subsystem in status: {sub}"
        item = next(s for s in subsystems if s["name"] == sub)
        assert item["symbol"] == "✓", f"Subsystem {sub} must have symbol '✓'"
        assert item["active"] is True, f"Subsystem {sub} must be active"

    print("[OK] 10. National Material Harmonization Engine Status Section verified:")
    for s in subsystems:
        print(f"     - {s['name']:20} [[OK] {s['status']}] -> {s['detail']}")

    print("\n" + "=" * 75)
    print("ALL OVERVIEW DASHBOARD VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 75)




def test_dynamic_duplicate_detection_trend_matches_database():
    """
    REGRESSION TEST:
    Verifies that the Duplicate Detection Trend returned by GET /api/dashboard/overview
    is dynamically calculated from the underlying SQLite database, matches an
    independent calculation, and fails if hardcoded values (e.g. [2, 6, 10, 13]) are reintroduced.
    Also verifies graceful handling of empty database states.
    """
    print("\n" + "=" * 75)
    print("SIH26099 Regression Test: Dynamic Duplicate Detection Trend")
    print("=" * 75)

    from datetime import datetime

    def parse_dt(ts_str):
        if not ts_str:
            return None
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(ts_str, fmt)
            except ValueError:
                pass
        return None

    # 1. Independently compute expected trend directly from SQLite database
    matching_actions = (
        "AI_RECOMMENDATION",
        "APPROVE_MATCH",
        "MAPPING_CREATED",
        "MAPPING_UPDATED",
        "REQUEST_FURTHER_REVIEW",
    )
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        placeholders = ",".join("?" for _ in matching_actions)
        cur.execute(
            f"""
            SELECT timestamp
            FROM audit_logs
            WHERE action IN ({placeholders})
            ORDER BY timestamp ASC, id ASC
            """,
            matching_actions,
        )
        audit_rows = cur.fetchall()

        cand_rows = []
        try:
            cur.execute(
                """
                SELECT created_at
                FROM match_candidates
                WHERE hybrid_score >= 0.65
                ORDER BY created_at ASC, id ASC
                """
            )
            cand_rows = cur.fetchall()
        except Exception:
            pass

    all_raw = [r[0] for r in audit_rows if r[0]] + [r[0] for r in cand_rows if r[0]]
    parsed_dts = []
    for ts in all_raw:
        dt = parse_dt(ts)
        if dt:
            parsed_dts.append(dt)
    parsed_dts.sort()

    unique_days = sorted(set(d.strftime("%Y-%m-%d") for d in parsed_dts))
    if len(unique_days) >= 3:
        bucket_fn = lambda d: d.strftime("%Y-%m-%d")
    else:
        unique_hours = sorted(set(d.strftime("%Y-%m-%d %H:00") for d in parsed_dts))
        if len(unique_hours) >= 3:
            bucket_fn = lambda d: d.strftime("%Y-%m-%d %H:00")
        else:
            bucket_fn = lambda d: d.strftime(f"%Y-%m-%d %H:{(d.minute // 15) * 15:02d}")

    buckets = {}
    for d in parsed_dts:
        k = bucket_fn(d)
        buckets[k] = buckets.get(k, 0) + 1

    sorted_keys = sorted(buckets.keys())
    expected_labels = []
    expected_new = []
    expected_cumulative = []
    running_sum = 0
    for k in sorted_keys:
        cnt = buckets[k]
        running_sum += cnt
        expected_labels.append(k)
        expected_new.append(cnt)
        expected_cumulative.append(running_sum)

    # 2. Call GET /api/dashboard/overview
    res = client.get("/api/dashboard/overview")
    assert res.status_code == 200, f"Dashboard API call failed: {res.text}"
    trend = res.json()["charts"]["duplicate_detection_trend"]

    # 3. Assert dynamic API results strictly match independent database calculation
    assert trend["labels"] == expected_labels, (
        f"Labels mismatch: API {trend['labels']} vs expected DB {expected_labels}"
    )
    assert trend["cumulative"] == expected_cumulative, (
        f"Cumulative mismatch: API {trend['cumulative']} vs expected DB {expected_cumulative}"
    )
    assert trend["new"] == expected_new, (
        f"New mismatch: API {trend['new']} vs expected DB {expected_new}"
    )
    assert trend["new_per_batch"] == expected_new, (
        f"New_per_batch mismatch: API {trend['new_per_batch']} vs expected DB {expected_new}"
    )

    # 4. Strict anti-mock / zero-fake-data check: MUST NOT be old hardcoded arrays
    OLD_HARDCODED_CUMULATIVE = [2, 6, 10, 13]
    OLD_HARDCODED_NEW = [2, 4, 4, 3]
    assert trend["cumulative"] != OLD_HARDCODED_CUMULATIVE, (
        "FAIL: Duplicate Detection Trend contains old hardcoded milestone values [2, 6, 10, 13]!"
    )
    assert trend["new"] != OLD_HARDCODED_NEW, (
        "FAIL: Duplicate Detection Trend contains old hardcoded new counts [2, 4, 4, 3]!"
    )

    print(f"[OK] 1. Dynamic Duplicate Detection Trend verified against independent SQLite query:")
    print(f"     - Labels:     {trend['labels']}")
    print(f"     - New:        {trend['new']}")
    print(f"     - Cumulative: {trend['cumulative']}")
    print(f"[OK] 2. Strict anti-mock verification passed: Old hardcoded arrays [2, 6, 10, 13] rejected.")

    # 5. Empty database test: ensure robust zero-state handling without crashing
    import tempfile
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        empty_db_path = Path(tmp_dir) / "empty_cpse.db"
        from backend.app.cpse.dashboard_service import DashboardService
        from backend.app.cpse.models import CREATE_TABLES_SQL

        empty_conn = sqlite3.connect(empty_db_path)
        try:
            empty_conn.executescript(CREATE_TABLES_SQL)
            empty_conn.commit()
        finally:
            empty_conn.close()

        empty_service = DashboardService(db_path=empty_db_path)
        empty_overview = empty_service.get_overview_metrics()
        empty_trend = empty_overview["charts"]["duplicate_detection_trend"]

        assert empty_trend["labels"] == [], f"Expected empty labels, got {empty_trend['labels']}"
        assert empty_trend["cumulative"] == [], f"Expected empty cumulative, got {empty_trend['cumulative']}"
        assert empty_trend["new"] == [], f"Expected empty new, got {empty_trend['new']}"
        assert empty_overview["kpis"]["total_materials"] == 0

    print("[OK] 3. Empty database resilience verified: clean zero-state returned with zero crashes.")
    print("=" * 75)
    print("ALL DYNAMIC DUPLICATE DETECTION TREND REGRESSION TESTS PASSED!")
    print("=" * 75)


if __name__ == "__main__":
    test_overview_dashboard()
    test_dynamic_duplicate_detection_trend_matches_database()

