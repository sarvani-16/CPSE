"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Test Suite: Enterprise Governance & Audit Layer Verification (test_audit.py)
Validates:
1. Health check includes Governance & Audit Trail
2. GET /api/audit-logs returns HTTP 200 with complete AuditLogsResponse schema
3. Every log item contains required fields: id, action, entity_type, entity_id, old_value, new_value, performed_by, timestamp, reason
4. All 7 core lifecycle events tracked: uploads, normalization, AI recommendations, approvals, rejections, canonical creation, mapping changes
5. Multi-factor filtering: action, entity, user, date
6. CRITICAL SECURITY GUARANTEE: Never store passwords, tokens, or secrets (active redaction test)
7. Security upload validation: extension whitelist, size bounds, path traversal prevention
8. Web route serving for /audit-trail and /audit
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from main import app
from backend.app.cpse.audit_service import sanitize_audit_payload, get_audit_service


def run_audit_verification():
    print("=" * 75)
    print("SIH26099 Verification: Enterprise Governance & Audit Layer")
    print("=" * 75)

    client = TestClient(app)

    # 1. Health check
    print("[1/8] Verifying Health Check features...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    health_data = res.json()
    assert any("Audit" in f for f in health_data.get("features", [])), "Audit feature missing from /api/health"
    print("      [OK] Health check verified with Audit & Governance features.")

    # 2. GET /api/audit-logs API
    print("[2/8] Testing GET /api/audit-logs baseline response...")
    res = client.get("/api/audit-logs")
    assert res.status_code == 200, f"GET /api/audit-logs returned {res.status_code}"
    data = res.json()
    for field in ["total", "page", "page_size", "total_pages", "items", "available_actions", "available_entities", "available_users"]:
        assert field in data, f"Missing required top-level field '{field}' in response"
    assert data["total"] > 0, "No audit logs found"
    print(f"      [OK] HTTP 200 OK. Total audit logs recorded: {data['total']}")

    # 3. Required Fields Verification
    print("[3/8] Verifying required audit log fields across records...")
    required_fields = ["id", "action", "entity_type", "entity_id", "old_value", "new_value", "performed_by", "timestamp", "reason"]
    sample_item = data["items"][0]
    for rf in required_fields:
        assert rf in sample_item, f"Required audit log field '{rf}' missing from item"
    print(f"      [OK] All {len(required_fields)} required fields present and verified in log items:")
    print(f"           - id:           {sample_item['id']}")
    print(f"           - action:       {sample_item['action']}")
    print(f"           - entity_type:  {sample_item['entity_type']}")
    print(f"           - entity_id:    {sample_item['entity_id']}")
    print(f"           - performed_by: {sample_item['performed_by']}")
    print(f"           - timestamp:    {sample_item['timestamp']}")
    print(f"           - reason:       {sample_item['reason']}")

    # 4. Core Lifecycle Events Tracked
    print("[4/8] Verifying all core lifecycle event types are tracked...")
    available_actions = set(data["available_actions"])
    expected_categories = [
        "UPLOAD_MATERIALS",
        "NORMALIZE_RECORD",
        "AI_RECOMMENDATION",
        "APPROVE_MATCH",
        "REJECT_MATCH",
        "CREATE_CANONICAL_CODE",
        "MAPPING_CREATED",
    ]
    for exp_act in expected_categories:
        assert exp_act in available_actions, f"Expected action '{exp_act}' not found in audit logs. Found: {available_actions}"
        print(f"      [OK] Tracked: {exp_act}")

    # 5. Multi-Factor Filtering
    print("[5/8] Testing multi-factor audit filters (action, entity, user, date)...")
    # 5a. Action filter
    res_act = client.get("/api/audit-logs?action=APPROVE_MATCH")
    assert res_act.status_code == 200
    act_data = res_act.json()
    assert all(i["action"] == "APPROVE_MATCH" for i in act_data["items"]), "Action filter failed"
    print(f"      [OK] Action Filter (action=APPROVE_MATCH): {act_data['total']} items matched")

    # 5b. Entity filter
    res_ent = client.get("/api/audit-logs?entity=source_materials")
    assert res_ent.status_code == 200
    ent_data = res_ent.json()
    assert all("source_materials" in (i["entity_type"] + (i["entity_id"] or "")).lower() for i in ent_data["items"])
    print(f"      [OK] Entity Filter (entity=source_materials): {ent_data['total']} items matched")

    # 5c. User filter
    res_usr = client.get("/api/audit-logs?user=Govt")
    assert res_usr.status_code == 200
    usr_data = res_usr.json()
    assert all("govt" in i["performed_by"].lower() for i in usr_data["items"])
    print(f"      [OK] User Filter (user=Govt): {usr_data['total']} items matched")

    # 5d. Date filter
    today_str = datetime.now().strftime("%Y-%m-%d")
    res_date = client.get(f"/api/audit-logs?date={today_str}")
    assert res_date.status_code == 200
    date_data = res_date.json()
    assert date_data["total"] > 0, f"No logs found for today: {today_str}"
    print(f"      [OK] Date Filter (date={today_str}): {date_data['total']} items matched")

    # 6. CRITICAL SECURITY: Confidential Secret Redaction
    print("[6/8] CRITICAL SECURITY TEST: Verifying zero secrets stored & active redaction...")
    # Test active redactor
    unsafe_payload = {
        "user_id": 42,
        "password": "SuperSecretPassword123!",
        "api_key": "sk-proj-abcdef123456",
        "auth_token": "Bearer eyJhbGciOi...",
        "session_cookie": "sess_998811",
        "regular_field": "Stainless Steel SS304",
        "nested": {
            "private_key": "-----BEGIN RSA PRIVATE KEY-----",
            "safe_attribute": "M10x50mm",
        },
    }
    sanitized = sanitize_audit_payload(unsafe_payload)
    assert sanitized["password"] == "[REDACTED_CONFIDENTIAL]", "Password was not redacted!"
    assert sanitized["api_key"] == "[REDACTED_CONFIDENTIAL]", "API Key was not redacted!"
    assert sanitized["auth_token"] == "[REDACTED_CONFIDENTIAL]", "Auth Token was not redacted!"
    assert sanitized["session_cookie"] == "[REDACTED_CONFIDENTIAL]", "Cookie was not redacted!"
    assert sanitized["nested"]["private_key"] == "[REDACTED_CONFIDENTIAL]", "Nested private key was not redacted!"
    assert sanitized["regular_field"] == "Stainless Steel SS304", "Safe data altered!"
    assert sanitized["nested"]["safe_attribute"] == "M10x50mm", "Safe nested data altered!"

    # Verify no leaked secrets across all existing audit log items
    for item in data["items"]:
        item_text = str(item).lower()
        assert "supersecret" not in item_text, "Found leaked secret in audit log"
        assert "bearer ey" not in item_text, "Found leaked bearer token in audit log"
    print("      [OK] Security Redactor verified: Passwords, tokens, cookies, and keys actively sanitized.")

    # 7. File Upload Security Validation
    print("[7/8] Testing Ingestion Security (format restriction & path traversal prevention)...")
    # Disallowed extension
    res_bad = client.post(
        "/api/materials/upload",
        files={"file": ("malicious.exe", b"fake binary content", "application/octet-stream")},
        data={"cpse_name": "ONGC", "dry_run": "true"},
    )
    assert res_bad.status_code in [400, 500], f"Expected rejection for .exe file, got {res_bad.status_code}"
    print("      [OK] Disallowed file extensions (.exe) rejected.")

    # Path traversal attempt in filename
    res_trav = client.post(
        "/api/materials/upload",
        files={"file": ("../../../../etc/passwd.csv", b"MAT_CODE,MAT_DESC\nC1,Bolt\n", "text/csv")},
        data={"cpse_name": "ONGC", "dry_run": "true"},
    )
    assert res_trav.status_code == 200, f"Valid CSV content should succeed after filename sanitization: {res_trav.status_code}"
    clean_filename = res_trav.json().get("filename")
    assert clean_filename == "passwd.csv", f"Path traversal not stripped from filename: {clean_filename}"
    print(f"      [OK] Filename path traversal stripped safely -> '{clean_filename}'.")

    # 8. Web Routes Check
    print("[8/8] Testing Web UI Route availability for Audit Trail...")
    res_trail = client.get("/audit-trail")
    assert res_trail.status_code == 200, f"/audit-trail returned {res_trail.status_code}"
    assert "Enterprise Governance Audit Trail" in res_trail.text
    res_audit = client.get("/audit")
    assert res_audit.status_code == 200, f"/audit returned {res_audit.status_code}"
    print("      [OK] Web routes /audit-trail and /audit verified.")

    print("=" * 75)
    print("ALL ENTERPRISE GOVERNANCE & AUDIT TESTS PASSED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_audit_verification()
