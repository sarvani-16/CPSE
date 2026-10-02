"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Module: CPSE Models & Schema Definitions
Description: Enterprise data models, Pydantic schemas, and SQL DDL for CPSE material governance.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Normalized Internal Schema Field Names
CPSE_SCHEMA_FIELDS = [
    "cpse_name",
    "material_code",
    "description",
    "specification",
    "material_type",
    "material_grade",
    "dimensions",
    "unit_of_measure",
    "manufacturer",
    "part_number",
    "category",
    "source_file",
]

REQUIRED_FIELDS = ["material_code", "description"]


class SourceMaterialModel(BaseModel):
    """
    Represents an ingested material item from any Central Public Sector Enterprise (CPSE).
    Preserves original CPSE identifiers and all optional technical metadata.
    """
    id: Optional[int] = None
    cpse_name: str = Field(..., description="Name of the enterprise (e.g., ONGC, IOCL, BHEL, NTPC, SAIL)")
    material_code: str = Field(..., description="Original CPSE item/material code (NEVER modified or deleted)")
    description: str = Field(..., description="Original CPSE material description")
    specification: Optional[str] = Field(None, description="Detailed technical specification")
    material_type: Optional[str] = Field(None, description="Material type/class (e.g. Raw Material, Spare, Consumable)")
    material_grade: Optional[str] = Field(None, description="Industrial/metallurgical grade (e.g. SS304, A106-B, IS 2062)")
    dimensions: Optional[str] = Field(None, description="Size or physical dimensions (e.g. M10x50mm, 2 inch Sch 40)")
    unit_of_measure: Optional[str] = Field(None, description="Unit of Measure (e.g. EA, MTR, KG, SET, NOS)")
    manufacturer: Optional[str] = Field(None, description="Original manufacturer or vendor make")
    part_number: Optional[str] = Field(None, description="Manufacturer part/catalog number")
    category: Optional[str] = Field(None, description="Commodity or procurement category")
    source_file: Optional[str] = Field(None, description="Source filename or batch identifier")
    created_at: Optional[str] = None


class CanonicalMaterialModel(BaseModel):
    """
    Represents the unified, standardized national material master definition.
    Labeled as: 'Prototype Common Material Code' (NMM Series).
    Do NOT claim these are official government material codes.
    """
    id: Optional[int] = None
    national_material_code: str = Field(..., description="Prototype Common Material Code (e.g. NMM-000001)")
    code_type_label: str = Field("Prototype Common Material Code", description="Explicit labeling as prototype code")
    canonical_code: Optional[str] = None
    standardized_description: str = Field(..., description="Standardized, harmonized description")
    canonical_description: Optional[str] = None
    category: Optional[str] = None
    material_type: Optional[str] = None
    standard_specification: Optional[str] = None
    standard_uom: Optional[str] = None
    technical_attributes: Optional[Dict[str, Any]] = None
    approval_status: str = Field("APPROVED", description="Approval status: APPROVED, PENDING, NEEDS_REVIEW")
    source_materials: Optional[List[Dict[str, Any]]] = None
    cpse_mappings: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MaterialMappingModel(BaseModel):
    """
    CRUCIAL DATA GOVERNANCE RECORD:
    Preserves the permanent linkage between the enterprise's original code
    and the Common National Canonical Material Code.
    """
    id: Optional[int] = None
    source_material_id: int
    cpse_name: str
    original_material_code: str
    original_description: str
    canonical_material_code: str
    canonical_description: str
    match_status: str  # MATCH, REVIEW, APPROVED, REJECTED, MANUAL
    confidence: float
    reviewer: str  # AI_SYSTEM or reviewer ID
    timestamp: Optional[str] = None


class UploadPreviewResponse(BaseModel):
    """
    Response returned during upload dry-run / column detection.
    """
    filename: str
    file_type: str
    total_rows_detected: int
    detected_columns: List[str]
    suggested_mappings: Dict[str, str]
    unmapped_columns: List[str]
    missing_required_fields: List[str]
    preview_rows: List[Dict[str, Any]]
    is_valid: bool
    validation_message: str


class AuditLogEntry(BaseModel):
    """
    Data Governance Audit Log Record.
    Tracks all lifecycle modifications across the CPSE standardization pipeline.
    CRITICAL: Never stores passwords, tokens, or security credentials.
    """
    id: int
    action: str = Field(..., description="Action performed: UPLOAD_MATERIALS, NORMALIZE_RECORD, AI_RECOMMENDATION, APPROVE_MATCH, REJECT_MATCH, CREATE_CANONICAL_CODE, MAPPING_CREATED, MAPPING_UPDATED")
    entity_type: str = Field(..., description="Target entity type (e.g. source_materials, canonical_materials, reviews, material_mappings)")
    entity_id: Optional[str] = Field(None, description="Identifier of the modified entity")
    old_value: Optional[str] = Field(None, description="Previous state or value prior to change")
    new_value: Optional[str] = Field(None, description="Resulting state or value after change")
    performed_by: str = Field(..., description="User ID, auditor designation, or automated system")
    timestamp: str = Field(..., description="ISO 8601 audit timestamp")
    reason: Optional[str] = Field(None, description="Audit justification, engineering comment, or operational rationale")
    details: Optional[Dict[str, Any]] = None
    user: Optional[str] = None


class AuditLogsResponse(BaseModel):
    """
    Paginated audit log query response with available filter dimensions.
    """
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[AuditLogEntry]
    available_actions: List[str]
    available_entities: List[str]
    available_users: List[str]


# ==========================================
# SQL Database Schema Definitions (DDL)
# ==========================================

class ReviewActionRequest(BaseModel):
    """
    Payload for human reviewer actions (Approve, Reject, Request Review).
    Uses a clearly labelled demo reviewer account for prototype governance.
    """
    reviewer_name: str = Field(
        default="Govt Reviewer (Demo Auditor: audit.officer@cpse.gov.in)",
        description="Official name / designation of the human reviewer",
    )
    comment: Optional[str] = Field(
        default=None,
        description="Optional justification, audit note, or engineering comment",
    )


class BatchApproveRequest(BaseModel):
    """
    Payload for batch approving multiple high-confidence candidate matches.
    """
    review_ids: List[int] = Field(
        ...,
        description="List of review IDs to batch-approve",
    )
    reviewer_name: Optional[str] = Field(
        default="Govt Reviewer (Demo Auditor: audit.officer@cpse.gov.in)",
        description="Official name / designation of the human reviewer",
    )
    comment: Optional[str] = Field(
        default=None,
        description="Optional justification, audit note, or batch approval comment",
    )
    min_confidence: Optional[float] = Field(
        default=0.80,
        description="Minimum confidence threshold required for batch approval (default: 0.80)",
    )


CREATE_TABLES_SQL = """
-- 1. Source Materials (Enterprise Catalog)
CREATE TABLE IF NOT EXISTS source_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpse_name TEXT NOT NULL,
    material_code TEXT NOT NULL,
    description TEXT NOT NULL,
    specification TEXT,
    material_type TEXT,
    material_grade TEXT,
    dimensions TEXT,
    unit_of_measure TEXT,
    manufacturer TEXT,
    part_number TEXT,
    category TEXT,
    source_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cpse_name, material_code)
);

-- 2. Canonical Materials (Standardized National Master - Prototype NMM Series)
CREATE TABLE IF NOT EXISTS canonical_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    national_material_code TEXT UNIQUE NOT NULL,
    canonical_code TEXT UNIQUE,
    standardized_description TEXT NOT NULL,
    canonical_description TEXT,
    category TEXT,
    material_type TEXT,
    standard_specification TEXT,
    standard_uom TEXT,
    technical_attributes TEXT,
    approval_status TEXT DEFAULT 'APPROVED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Material Mappings (Governance & Code Linkage)
CREATE TABLE IF NOT EXISTS material_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_material_id INTEGER NOT NULL,
    cpse_name TEXT NOT NULL,
    original_material_code TEXT NOT NULL,
    original_description TEXT NOT NULL,
    canonical_material_code TEXT NOT NULL,
    canonical_description TEXT NOT NULL,
    match_status TEXT NOT NULL,
    confidence REAL NOT NULL,
    reviewer TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_material_id) REFERENCES source_materials(id),
    FOREIGN KEY (canonical_material_code) REFERENCES canonical_materials(canonical_code)
);

-- 4. Match Candidates (AI Suggestions)
CREATE TABLE IF NOT EXISTS match_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_material_id INTEGER NOT NULL,
    candidate_source_material_id INTEGER,
    candidate_canonical_code TEXT,
    lexical_score REAL,
    fuzzy_score REAL,
    semantic_score REAL,
    hybrid_score REAL,
    decision TEXT NOT NULL,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_material_id) REFERENCES source_materials(id)
);

-- 5. Reviews (Human-in-the-Loop Review Queue)
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_material_id INTEGER NOT NULL,
    suggested_canonical_code TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    semantic_score REAL,
    fuzzy_score REAL,
    lexical_score REAL,
    hybrid_score REAL,
    detected_attributes TEXT,
    conflicts TEXT,
    explanation TEXT,
    reviewer_name TEXT,
    comments TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_material_id) REFERENCES source_materials(id),
    FOREIGN KEY (suggested_canonical_code) REFERENCES canonical_materials(canonical_code)
);

-- 6. Audit Logs (Immutable Governance Trail)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT,
    old_value TEXT,
    new_value TEXT,
    performed_by TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    details TEXT,
    user TEXT
);

-- Indexes for high-speed lookup & governance compliance
CREATE INDEX IF NOT EXISTS idx_source_cpse_code ON source_materials(cpse_name, material_code);
CREATE INDEX IF NOT EXISTS idx_source_desc ON source_materials(description);
CREATE INDEX IF NOT EXISTS idx_mappings_orig_code ON material_mappings(cpse_name, original_material_code);
CREATE INDEX IF NOT EXISTS idx_mappings_canon_code ON material_mappings(canonical_material_code);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
"""
