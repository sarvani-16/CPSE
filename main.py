"""
SIH26099 – AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
FastAPI Application: Dataset Service, Hybrid Matching Engine, and CPSE Material Master Upload & Governance
"""

import sys
from pathlib import Path
import json

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Query, HTTPException, Body, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from src.dataset_service import get_dataset_service
from backend.app.ml.hybrid_engine import get_hybrid_engine
from backend.app.ml.candidate_finder import find_top_candidates
from backend.app.ml.evaluator import run_evaluation
from backend.app.cpse.service import get_cpse_service
from backend.app.cpse.models import ReviewActionRequest, AuditLogsResponse, BatchApproveRequest
from backend.app.cpse.review_service import get_review_service
from backend.app.cpse.canonical_service import get_canonical_service
from backend.app.cpse.dashboard_service import get_dashboard_service
from backend.app.cpse.audit_service import get_audit_service

app = FastAPI(
    title="SIH26099 Material Standardization & Harmonization Service",
    description="Enterprise CPSE Material Master, CSV/XLSX Upload, Column Auto-Mapping, and AI Matching Engine.",
    version="3.0.0",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dataset_service = get_dataset_service()
hybrid_engine = get_hybrid_engine()
cpse_service = get_cpse_service()
review_service = get_review_service()
canonical_service = get_canonical_service()
dashboard_service = get_dashboard_service()
audit_service = get_audit_service()


class CompareRequest(BaseModel):
    title_a: str = Field(..., description="First material description/title")
    title_b: str = Field(..., description="Second material description/title")


class AutoCreateCanonicalRequest(BaseModel):
    source_material_id: Optional[int] = Field(None, description="Optional ID of existing source material")
    description: Optional[str] = Field(None, description="Material description if creating directly")
    cpse_name: Optional[str] = Field("CPSE", description="CPSE Name")
    material_code: Optional[str] = Field("UNSPECIFIED", description="Original Material Code")
    specification: Optional[str] = Field(None, description="Specification")
    material_grade: Optional[str] = Field(None, description="Material grade")
    dimensions: Optional[str] = Field(None, description="Dimensions")
    unit_of_measure: Optional[str] = Field("EA", description="UOM")
    category: Optional[str] = Field(None, description="Category")
    reviewer: Optional[str] = Field("AI_STANDARDIZATION_ENGINE", description="Creator identity")


@app.get("/", response_class=HTMLResponse)
@app.get("/overview", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/material-master", response_class=HTMLResponse)
@app.get("/matching-engine", response_class=HTMLResponse)
@app.get("/cpse-upload", response_class=HTMLResponse)
@app.get("/review-center", response_class=HTMLResponse)
@app.get("/harmonized-materials", response_class=HTMLResponse)
@app.get("/audit-trail", response_class=HTMLResponse)
@app.get("/audit", response_class=HTMLResponse)
def serve_ui():
    """
    Serves the integrated enterprise web dashboard.
    """
    html_path = PROJECT_ROOT / "frontend" / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="frontend/index.html not found.")
    return FileResponse(html_path)


# =====================================================================
# 1. Benchmark Dataset Exploration APIs (Development & Testing)
# =====================================================================

@app.get("/api/dataset/status")
def get_dataset_status():
    """
    Returns benchmark dataset load state and disclaimer.
    """
    return dataset_service.get_status()


@app.get("/api/dataset/summary")
def get_dataset_summary():
    """
    Returns benchmark dataset statistics.
    """
    return dataset_service.get_summary()


@app.get("/api/dataset/preview")
def get_dataset_preview(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Records per page"),
    search: str = Query(default="", description="Search query across titles and IDs"),
):
    """
    Paginated access to benchmark catalog.
    """
    return dataset_service.get_preview(page=page, page_size=page_size, search=search)


@app.get("/api/dataset/groups")
def get_dataset_groups():
    """
    Returns benchmark group size distribution.
    """
    return dataset_service.get_groups()


# =====================================================================
# 2. AI Matching Engine APIs (Lexical + Fuzzy + Semantic + Guardrails)
# =====================================================================

@app.post("/api/matching/compare")
def compare_materials(req: CompareRequest):
    """
    POST /api/matching/compare
    Calculates lexical, fuzzy, and semantic scores with technical domain guardrails.
    """
    if not req.title_a.strip() or not req.title_b.strip():
        raise HTTPException(
            status_code=400, detail="Both 'title_a' and 'title_b' must be non-empty strings."
        )

    res = hybrid_engine.compare(req.title_a, req.title_b)
    return {
        "title_a": req.title_a,
        "title_b": req.title_b,
        "match_decision": res["match_decision"],
        "hybrid_score": res["hybrid_score"],
        "semantic_score": res["semantic_score"],
        "lexical_score": res["lexical_score"],
        "fuzzy_score": res["fuzzy_score"],
        "explanation": res["explanation"],
        "technical_tokens": res["technical_tokens"],
        "sub_scores": res["sub_scores"],
        "weights": res["weights"],
    }


@app.get("/api/matching/candidates/{posting_id}")
def get_candidates(
    posting_id: str,
    top_k: int = Query(default=5, ge=1, le=20, description="Number of top candidates to retrieve"),
):
    """
    GET /api/matching/candidates/{posting_id}
    Retrieves top candidate matches from the benchmark dataset with explanations.
    """
    try:
        return find_top_candidates(posting_id=posting_id, top_k=top_k)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candidate retrieval error: {str(e)}")


@app.get("/api/ml/evaluation")
def get_evaluation(force_recompute: bool = False):
    """
    GET /api/ml/evaluation
    Returns actual calculated metrics on 1,000 controlled evaluation pairs.
    """
    metrics_path = PROJECT_ROOT / "outputs" / "results" / "evaluation_metrics.json"
    if not force_recompute and metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return run_evaluation()


# =====================================================================
# 3. CPSE Material Master Upload & Governance APIs
# =====================================================================

@app.post("/api/materials/upload")
async def upload_cpse_materials(
    file: UploadFile = File(..., description="CSV or XLSX file exported from CPSE ERP/SAP"),
    cpse_name: str = Form("ONGC", description="Enterprise Identifier (e.g. ONGC, IOCL, BHEL, NTPC, SAIL)"),
    mapping_overrides: Optional[str] = Form(None, description="Optional JSON string of column mappings"),
    dry_run: bool = Form(False, description="If true, returns preview and mappings without writing to DB"),
):
    """
    POST /api/materials/upload
    Ingests CSV/XLSX material data from any CPSE:
    - Auto-detects columns and maps them to normalized internal schema
    - Reports unmapped columns and validates required fields (material_code, description)
    - If dry_run=True, provides instant preview of first 5 rows with detected mappings
    - If dry_run=False, safely ingests items into source_materials and logs immutable audit trail
    """
    # Security: strip path components to prevent path traversal attacks
    filename = Path(file.filename).name if file.filename else "upload.csv"
    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    overrides_dict = None
    if mapping_overrides:
        try:
            overrides_dict = json.loads(mapping_overrides)
        except Exception:
            pass

    try:
        if dry_run:
            preview = cpse_service.preview_upload(
                file_bytes=contents,
                filename=filename,
                cpse_name=cpse_name,
                user_overrides=overrides_dict,
            )
            return preview.dict()
        else:
            # Detect mapping if not fully supplied
            preview = cpse_service.preview_upload(
                file_bytes=contents,
                filename=filename,
                cpse_name=cpse_name,
                user_overrides=overrides_dict,
            )
            if not preview.is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Schema mapping validation failed: {preview.validation_message}. Missing: {preview.missing_required_fields}",
                )

            confirmed = preview.suggested_mappings
            import_result = cpse_service.import_materials(
                file_bytes=contents,
                filename=filename,
                cpse_name=cpse_name,
                confirmed_mappings=confirmed,
                user="PROCUREMENT_ADMIN",
            )
            return import_result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")


@app.get("/api/materials/source")
def get_source_materials(
    cpse_name: Optional[str] = Query(None, description="Filter by enterprise name"),
    search: Optional[str] = Query(None, description="Search by code, description, or grade"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """
    GET /api/materials/source
    Retrieves ingested CPSE source materials with original codes preserved.
    """
    return cpse_service.get_source_materials(
        cpse_name=cpse_name,
        search=search,
        page=page,
        page_size=page_size,
    )


@app.get("/api/materials/mappings")
def get_material_mappings(
    cpse_name: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """
    GET /api/materials/mappings
    Retrieves permanent data governance linkages between original CPSE codes and national codes.
    """
    return cpse_service.get_material_mappings(
        cpse_name=cpse_name,
        page=page,
        page_size=page_size,
    )


@app.get("/api/materials/audit-logs")
def get_audit_logs(limit: int = Query(default=50, ge=1, le=200)):
    """
    GET /api/materials/audit-logs
    Retrieves immutable audit log entries for enterprise data governance.
    """
    return cpse_service.get_audit_logs(limit=limit)


@app.post("/api/materials/load-sample/{sample_key}")
def load_sample_cpse_data(sample_key: str):
    """
    POST /api/materials/load-sample/{sample_key}
    Loads pre-bundled sample CPSE files:
    - 'ongc': cpse_a_ongc.csv (MAT_CODE, MAT_DESC, UOM format)
    - 'bhel': cpse_b_bhel.xlsx (ITEM_NO, LONG_DESCRIPTION, BASE_UOM format)
    """
    sample_dir = PROJECT_ROOT / "dataset" / "sample_cpse_data"
    if sample_key.lower() == "ongc":
        file_path = sample_dir / "cpse_a_ongc.csv"
        cpse = "ONGC"
    elif sample_key.lower() == "bhel":
        file_path = sample_dir / "cpse_b_bhel.xlsx"
        cpse = "BHEL"
    else:
        raise HTTPException(status_code=400, detail="Invalid sample key. Use 'ongc' or 'bhel'.")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample file not found at {file_path}")

    contents = file_path.read_bytes()
    preview = cpse_service.preview_upload(contents, file_path.name, cpse)
    import_res = cpse_service.import_materials(
        file_bytes=contents,
        filename=file_path.name,
        cpse_name=cpse,
        confirmed_mappings=preview.suggested_mappings,
        user="SYSTEM_SAMPLE_LOADER",
    )
    return {
        "sample_loaded": sample_key,
        "import_result": import_res,
        "mappings_applied": preview.suggested_mappings,
    }


# =====================================================================
# 4. Human-in-the-Loop Review Center Endpoints
# =====================================================================

@app.get("/api/reviews")
def get_reviews(
    status: Optional[str] = Query(None, description="Filter by review status: PENDING, APPROVED, REJECTED, NEEDS_REVIEW, ALL"),
    search: Optional[str] = Query(None, description="Search across original and canonical codes/descriptions"),
    cpse_name: Optional[str] = Query(None, description="Filter by enterprise name"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Records per page"),
):
    """
    GET /api/reviews
    Retrieves candidate items awaiting human review with full 3-column data:
    Source Material, AI Comparison & Evidence, Recommended Canonical Item.
    """
    return review_service.get_reviews(
        status=status,
        search=search,
        cpse_name=cpse_name,
        page=page,
        page_size=page_size,
    )


@app.post("/api/reviews/{id}/approve")
def approve_review(
    id: int,
    req: ReviewActionRequest = Body(default_factory=ReviewActionRequest),
):
    """
    POST /api/reviews/{id}/approve
    Human reviewer approves the suggested match:
    - Creates or updates record in material_mappings
    - Strictly preserves original CPSE material code and description
    - Logs immutable governance entry in audit_logs
    """
    try:
        return review_service.approve_review(
            review_id=id,
            reviewer_name=req.reviewer_name,
            comment=req.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review approval failed: {str(e)}")


@app.post("/api/reviews/{id}/reject")
def reject_review(
    id: int,
    req: ReviewActionRequest = Body(default_factory=ReviewActionRequest),
):
    """
    POST /api/reviews/{id}/reject
    Human reviewer rejects the suggested match:
    - Sets review status to REJECTED
    - Logs immutable governance entry in audit_logs
    """
    try:
        return review_service.reject_review(
            review_id=id,
            reviewer_name=req.reviewer_name,
            comment=req.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review rejection failed: {str(e)}")


@app.post("/api/reviews/{id}/request-review")
def request_further_review(
    id: int,
    req: ReviewActionRequest = Body(default_factory=ReviewActionRequest),
):
    """
    POST /api/reviews/{id}/request-review
    Marks item as NEEDS_REVIEW (requires engineering committee or lab analysis):
    - Sets review status to NEEDS_REVIEW
    - Logs immutable governance entry in audit_logs
    """
    try:
        return review_service.request_further_review(
            review_id=id,
            reviewer_name=req.reviewer_name,
            comment=req.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request further review failed: {str(e)}")


@app.post("/api/reviews/batch-approve")
def batch_approve_reviews(
    req: BatchApproveRequest = Body(...),
):
    """
    POST /api/reviews/batch-approve
    Batch-approves multiple high-confidence candidate matches:
    - Enforces confidence threshold (hybrid_score >= min_confidence, default 0.80)
    - Strictly blocks any items with technical conflicts
    - Safely skips already-approved items (idempotent)
    - Reuses individual approval workflow, generating distinct audit entries
    - Preserves all original CPSE material codes and descriptions
    """
    if not req.review_ids:
        raise HTTPException(status_code=400, detail="The 'review_ids' list must not be empty.")

    try:
        result = review_service.batch_approve_reviews(
            review_ids=req.review_ids,
            reviewer_name=req.reviewer_name,
            comment=req.comment,
            min_confidence=req.min_confidence if req.min_confidence is not None else 0.80,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch approval failed: {str(e)}")


@app.post("/api/reviews/generate")
def generate_review_queue(
    force_refresh: bool = Query(default=False, description="If true, clears unreviewed pending items and recomputes")
):
    """
    POST /api/reviews/generate
    Runs the AI matching engine on unreviewed source materials to propose matches against canonical master.
    """
    return review_service.generate_reviews(force_refresh=force_refresh)


# =====================================================================
# 5. Canonical Material & Common National Code APIs (Step 6)
# =====================================================================

@app.get("/api/canonical-materials")
def get_canonical_materials(
    search: Optional[str] = Query(None, description="Search across prototype code, description, specifications, or attributes"),
    category: Optional[str] = Query(None, description="Filter by commodity/procurement category"),
    approval_status: Optional[str] = Query(None, description="Filter by status: APPROVED, PENDING, NEEDS_REVIEW, ALL"),
    cpse_name: Optional[str] = Query(None, description="Filter by mapped enterprise name (e.g. ONGC, BHEL)"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Records per page"),
):
    """
    GET /api/canonical-materials
    Retrieves paginated list of canonical materials with Prototype Common Material Codes (NMM Series),
    standardized descriptions, mapped CPSEs, original codes, and approval statuses.
    """
    return canonical_service.get_canonical_materials(
        search=search,
        category=category,
        approval_status=approval_status,
        cpse_name=cpse_name,
        page=page,
        page_size=page_size,
    )


@app.get("/api/canonical-materials/{id}")
def get_canonical_material_detail(id: str):
    """
    GET /api/canonical-materials/{id}
    Retrieves complete detailed record with multi-branch provenance tree:
    Common Code (NMM-000001)
    ↓
    Canonical Description
    ↓
    CPSE A → Original Code
    CPSE B → Original Code
    CPSE C → Original Code
    """
    try:
        return canonical_service.get_canonical_material_detail(identifier=id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch canonical material: {str(e)}")


@app.post("/api/canonical-materials/auto-create")
def auto_create_canonical_material(payload: AutoCreateCanonicalRequest):
    """
    POST /api/canonical-materials/auto-create
    Dynamically creates or returns a Prototype Common Material Code (NMM Series)
    for previously unseen materials with full idempotency and immutable audit trail.
    """
    try:
        source_data = {}
        if payload.source_material_id:
            with cpse_service._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM source_materials WHERE id = ?", (payload.source_material_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail=f"Source material {payload.source_material_id} not found.")
                source_data = dict(row)
        else:
            if not payload.description:
                raise HTTPException(status_code=400, detail="Either source_material_id or description must be provided.")
            source_data = {
                "description": payload.description,
                "cpse_name": payload.cpse_name or "CPSE",
                "material_code": payload.material_code or "UNSPECIFIED",
                "specification": payload.specification,
                "material_grade": payload.material_grade,
                "dimensions": payload.dimensions,
                "unit_of_measure": payload.unit_of_measure or "EA",
                "category": payload.category,
            }

        result = canonical_service.create_prototype_canonical(
            source_material=source_data,
            performed_by=payload.reviewer or "AI_STANDARDIZATION_ENGINE",
            reason="Dynamic canonical generation for previously unseen material.",
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create canonical material: {str(e)}")


# =====================================================================
# 6. Executive Overview Dashboard APIs
# =====================================================================

@app.get("/api/dashboard/overview")
def get_dashboard_overview():
    """
    GET /api/dashboard/overview
    Retrieves dynamic enterprise overview metrics:
    - 6 KPI cards (Total Materials, Potential Duplicates, High Confidence Matches,
      Pending Reviews, Harmonized Materials, CPSE Sources)
    - 5 Charts (Match Distribution, Materials by CPSE, Duplicate Detection Trend,
      Review Status, Category Distribution)
    - 6-Stage System Status for National Material Harmonization Engine
    All metrics computed directly from SQLite databases (100% verified real data).
    """
    return dashboard_service.get_overview_metrics()


# =====================================================================
# 7. Enterprise Governance & Audit Trail APIs
# =====================================================================

@app.get("/api/audit-logs", response_model=AuditLogsResponse)
def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action (e.g. UPLOAD_MATERIALS, APPROVE_MATCH, NORMALIZE_RECORD, etc.)"),
    entity: Optional[str] = Query(None, description="Filter by entity type or entity ID"),
    user: Optional[str] = Query(None, description="Filter by user or system performing the action"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=25, ge=1, le=100, description="Records per page"),
):
    """
    GET /api/audit-logs
    Retrieves enterprise data governance audit trail with multi-factor filtering:
    action, entity, user, date, and pagination.
    CRITICAL SECURITY GUARANTEE: Never exposes passwords, tokens, or confidential keys.
    """
    return audit_service.get_audit_logs(
        action=action,
        entity=entity,
        user=user,
        date=date,
        page=page,
        page_size=page_size,
    )


@app.get("/api/audit-logs/export")
def export_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action (e.g. UPLOAD_MATERIALS, APPROVE_MATCH, etc.)"),
    entity: Optional[str] = Query(None, description="Filter by entity type or entity ID"),
    entity_type: Optional[str] = Query(None, description="Filter specifically by entity_type"),
    entity_id: Optional[str] = Query(None, description="Filter specifically by entity_id"),
    user: Optional[str] = Query(None, description="Filter by user or system performing the action"),
    performed_by: Optional[str] = Query(None, description="Filter specifically by performed_by"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    date_from: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
):
    """
    GET /api/audit-logs/export
    Exports enterprise audit records to a downloadable, standards-compliant CSV file.
    Applies identical multi-factor filter semantics as get_audit_logs.
    CRITICAL SECURITY GUARANTEE: Never exposes passwords, tokens, or confidential keys.
    """
    try:
        csv_content, filename, count = audit_service.export_audit_logs_csv(
            action=action,
            entity=entity,
            entity_type=entity_type,
            entity_id=entity_id,
            user=user,
            performed_by=performed_by,
            date=date,
            date_from=date_from,
            date_to=date_to,
            log_export_event=True,
            exported_by="AUDITOR",
        )
        return Response(
            content=csv_content.encode("utf-8"),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Audit-Record-Count": str(count),
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export audit report: {str(e)}")


@app.get("/api/health")
def get_health():
    """
    Liveness and health check endpoint.
    """
    return {
        "status": "ok",
        "service": "SIH26099 Enterprise CPSE Material Standardization API",
        "features": [
            "Executive Overview Dashboard",
            "Benchmark Exploration",
            "Hybrid Matching Engine (MiniLM + TFIDF + RapidFuzz)",
            "CPSE Material Master Ingestion (CSV/XLSX)",
            "Schema Auto-Detection & Mapping",
            "Human-in-the-Loop Review Center",
            "Canonical National Material Master (NMM Series)",
            "Cross-Enterprise Traceability",
            "Enterprise Governance & Audit Trail (7 Tracked Lifecycle Events)",
        ],
    }


def main():
    """
    Direct execution entry point: initializes SQLite DB, models, and starts Uvicorn server.
    """
    print("=" * 75)
    print("SIH26099 AI Material Standardization & Harmonization System")
    print("=" * 75)
    print(f"[*] Project Root: {PROJECT_ROOT}")
    print("[*] Initializing dataset cache & CPSE database...")
    status = dataset_service.get_status()
    print(f"[+] Benchmark Loaded: {status['loaded']} ({status['total_records']:,} items)")
    source_stats = cpse_service.get_source_materials(page_size=1)
    print(f"[+] CPSE Source Materials: {source_stats['total']} items cataloged")
    canonical_stats = canonical_service.get_canonical_materials(page_size=1)
    print(f"[+] National Master (NMM): {canonical_stats['total']} common materials cataloged")
    audit_stats = audit_service.get_audit_logs(page_size=1)
    print(f"[+] Audit Trail Records:      {audit_stats['total']} governance events recorded")
    print("[+] Starting Web Server at http://127.0.0.1:8000")
    print("[+] Executive Overview:        http://127.0.0.1:8000/overview")
    print("[+] Material Master Dashboard: http://127.0.0.1:8000/material-master")
    print("[+] AI Matching Engine:        http://127.0.0.1:8000/matching-engine")
    print("[+] CPSE Material Upload:      http://127.0.0.1:8000/cpse-upload")
    print("[+] Human Review Center:       http://127.0.0.1:8000/review-center")
    print("[+] Harmonized Materials (NMM):http://127.0.0.1:8000/harmonized-materials")
    print("[+] Audit Trail & Governance:  http://127.0.0.1:8000/audit-trail")
    print("[+] REST API Documentation:    http://127.0.0.1:8000/docs")
    print("=" * 75)

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
