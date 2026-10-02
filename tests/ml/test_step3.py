"""
Step 3 Verification Test Suite: AI Matching Engine, Candidate Retrieval, and Benchmarking
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_step3_pipeline():
    print("=" * 70)
    print("RUNNING STEP 3 AUTOMATED VERIFICATION TEST SUITE")
    print("=" * 70)

    # 1. Test POST /api/matching/compare - Case A: Identical specs (MATCH)
    print("\n[1/6] Testing POST /api/matching/compare (Identical Specs) ...")
    payload_a = {
        "title_a": "M10 SS304 BOLT 50MM - Grade 8.8 (High Tensile)",
        "title_b": "M10 SS304 BOLT 50MM pack of 10 pcs",
    }
    r = client.post("/api/matching/compare", json=payload_a)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    res_a = r.json()
    print(f"      Hybrid Score:    {res_a['hybrid_score']}")
    print(f"      Semantic Score:  {res_a['semantic_score']}")
    print(f"      Lexical Score:   {res_a['lexical_score']}")
    print(f"      Fuzzy Score:     {res_a['fuzzy_score']}")
    print(f"      Match Decision:  {res_a['match_decision']}")
    print(f"      Matching Tokens: {res_a['technical_tokens']['matching']}")
    assert res_a["hybrid_score"] > 0.50
    assert len(res_a["explanation"]) > 0
    assert "m10" in res_a["technical_tokens"]["matching"]

    # 2. Test POST /api/matching/compare - Case B: Spec Conflict Guardrail (REVIEW)
    print("\n[2/6] Testing POST /api/matching/compare (Conflicting Specs SS304 vs SS316) ...")
    payload_b = {
        "title_a": "M10 SS304 BOLT 50MM - Grade 8.8 (High Tensile)",
        "title_b": "M10 SS316 BOLT 50MM - Grade 8.8 (High Tensile)",
    }
    r = client.post("/api/matching/compare", json=payload_b)
    assert r.status_code == 200
    res_b = r.json()
    print(f"      Hybrid Score:    {res_b['hybrid_score']}")
    print(f"      Conflicts:       {res_b['technical_tokens']['conflicts']}")
    print(f"      Match Decision:  {res_b['match_decision']}")
    # Crucial domain rule test: conflicting specs MUST force REVIEW instead of automatic MATCH
    assert res_b["technical_tokens"]["has_conflicts"] is True
    assert res_b["match_decision"] == "REVIEW"

    # 3. Test POST /api/matching/compare - Case C: Disparate Items (NOT_MATCH)
    print("\n[3/6] Testing POST /api/matching/compare (Disparate Items) ...")
    payload_c = {
        "title_a": "M10 SS304 BOLT 50MM - Grade 8.8 (High Tensile)",
        "title_b": "Transformer Oil 12V 100ml / 5kg Capacity",
    }
    r = client.post("/api/matching/compare", json=payload_c)
    assert r.status_code == 200
    res_c = r.json()
    print(f"      Hybrid Score:    {res_c['hybrid_score']}")
    print(f"      Match Decision:  {res_c['match_decision']}")
    assert res_c["match_decision"] == "NOT_MATCH"
    assert res_c["hybrid_score"] < 0.40

    # 4. Test GET /api/matching/candidates/{posting_id}
    print("\n[4/6] Testing GET /api/matching/candidates/train_129225211 ...")
    r = client.get("/api/matching/candidates/train_129225211?top_k=3")
    assert r.status_code == 200
    cand_data = r.json()
    print(f"      Query Item: {cand_data['query_item']['title']}")
    print(f"      Retrieved {len(cand_data['top_candidates'])} candidates:")
    for c in cand_data["top_candidates"]:
        print(f"        -> [{c['posting_id']}] {c['title']} (Hybrid: {c['hybrid_score']}) -> {c['match_decision']}")
    assert len(cand_data["top_candidates"]) > 0
    top1 = cand_data["top_candidates"][0]
    assert "VICTORIA SECRET" in top1["title"].upper()
    assert top1["hybrid_score"] >= 0.90
    assert top1["match_decision"] == "MATCH"

    # 5. Test GET /api/ml/evaluation
    print("\n[5/6] Testing GET /api/ml/evaluation (Actual Benchmark Metrics) ...")
    r = client.get("/api/ml/evaluation")
    assert r.status_code == 200
    eval_data = r.json()
    print(f"      Total Evaluation Pairs: {eval_data['total_evaluation_pairs']}")
    print("      Model Comparison Table:")
    for row in eval_data["comparison_table"]:
        print(f"        {row['model']:<36} | Prec: {row['precision']:.4f} | Rec: {row['recall']:.4f} | F1: {row['f1']:.4f} | FP: {row['false_positives']}")
    assert eval_data["total_evaluation_pairs"] == 1000
    assert len(eval_data["comparison_table"]) == 4

    # 6. Regression check on existing endpoints & frontend delivery
    print("\n[6/6] Testing Regression & Frontend Web Delivery ...")
    assert client.get("/api/dataset/status").status_code == 200
    assert client.get("/api/dataset/summary").status_code == 200
    assert client.get("/").status_code == 200
    assert client.get("/matching-engine").status_code == 200
    html = client.get("/").text
    assert "AI-Driven Material Standardization & Harmonization" in html
    assert "Direct Material Pair Comparison" in html
    assert "Standardized Model Benchmark Matrix" in html

    print("\n" + "=" * 70)
    print("ALL STEP 3 TESTS PASSED SUCCESSFULLY! FULL ENGINE VERIFIED.")
    print("=" * 70)


if __name__ == "__main__":
    test_step3_pipeline()
