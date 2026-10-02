"""
SIH26099: Dedicated Test Suite for AI/ML Microservice (ml-service)
Verifies:
1. Lexical + Fuzzy + Semantic comparison on port 8001
2. Metallurgy domain conflict detection (SS304 vs SS316 -> demoted to REVIEW)
3. Unrelated material comparison (-> NOT_MATCH)
4. Attribute extraction and normalization
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ML_ROOT = PROJECT_ROOT / "ml-service"
for p in [str(ML_ROOT), str(PROJECT_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ml_service_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["port"] == 8001


def test_ml_matching_identical():
    res = client.post(
        "/api/match",
        json={
            "title_a": "Hex Bolt M10 x 50 SS304",
            "title_b": "Stainless Steel Hex Bolt M10 50mm SS304",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["match_decision"] in ["MATCH", "REVIEW"]
    assert data["hybrid_score"] > 0.60
    assert len(data["explanation"]) > 0


def test_ml_matching_technical_conflict():
    res = client.post(
        "/api/match",
        json={
            "title_a": "Hex Bolt M10 x 50 SS304",
            "title_b": "Hex Bolt M10 x 50 SS316",
        },
    )
    assert res.status_code == 200
    data = res.json()
    # Guardrail MUST demote to REVIEW despite high textual similarity
    assert data["match_decision"] == "REVIEW"
    assert data["technical_tokens"]["has_conflicts"] is True
    assert any("ss304 vs ss316" in c for c in data["technical_tokens"]["conflicts"])


def test_ml_matching_unrelated():
    res = client.post(
        "/api/match",
        json={
            "title_a": "Hex Bolt M10 x 50 SS304",
            "title_b": "Centrifugal Water Pump 5HP",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["match_decision"] == "NOT_MATCH"
    assert data["hybrid_score"] < 0.30


def test_ml_extract_attributes():
    res = client.post(
        "/api/extract-attributes",
        json={"text": "Hex Head Bolt M10 x 50 mm, Stainless Steel Grade SS304 DIN 933"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "m10" in data["technical_tokens"] or "ss304" in data["technical_tokens"]
