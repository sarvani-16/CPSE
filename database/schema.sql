-- =============================================================================
-- SIH26099: AI-Driven Standardization & Harmonization of Material Codes
-- PostgreSQL Enterprise Database Schema
-- Database: sih26099
-- =============================================================================

-- Enable UUID extension if available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table (Enterprise Role-Based Access Control)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'OFFICER', -- ADMIN, REVIEWER, OFFICER
    cpse_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- 2. CPSE Organizations (Participating Central Public Sector Enterprises)
CREATE TABLE IF NOT EXISTS cpse (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL, -- e.g. ONGC, IOCL, BHEL, NTPC, SAIL
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100) NOT NULL, -- Oil & Gas, Power, Heavy Engineering, Steel
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Taxonomy / Commodity Classifications
CREATE TABLE IF NOT EXISTS taxonomy (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_code VARCHAR(50),
    level INT NOT NULL DEFAULT 1,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Source Materials (Enterprise Raw Catalogs from CPSEs)
CREATE TABLE IF NOT EXISTS source_materials (
    id BIGSERIAL PRIMARY KEY,
    cpse_name VARCHAR(100) NOT NULL,
    material_code VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    specification TEXT,
    material_type VARCHAR(100),
    material_grade VARCHAR(100),
    dimensions VARCHAR(150),
    unit_of_measure VARCHAR(50),
    manufacturer VARCHAR(255),
    part_number VARCHAR(150),
    category VARCHAR(150),
    source_file VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_source_cpse_code UNIQUE (cpse_name, material_code)
);

-- 5. Material Attributes (Normalized key-value specifications)
CREATE TABLE IF NOT EXISTS material_attributes (
    id BIGSERIAL PRIMARY KEY,
    source_material_id BIGINT NOT NULL REFERENCES source_materials(id) ON DELETE CASCADE,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value TEXT NOT NULL,
    normalized_value TEXT,
    uom VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Canonical Materials (Standardized National Material Master - NMM Series)
CREATE TABLE IF NOT EXISTS canonical_materials (
    id BIGSERIAL PRIMARY KEY,
    national_material_code VARCHAR(100) UNIQUE NOT NULL,
    code_type_label VARCHAR(100) NOT NULL DEFAULT 'Prototype Common Material Code',
    canonical_code VARCHAR(100) UNIQUE,
    standardized_description TEXT NOT NULL,
    canonical_description TEXT,
    category VARCHAR(150),
    material_type VARCHAR(100),
    standard_specification TEXT,
    standard_uom VARCHAR(50),
    technical_attributes JSONB,
    approval_status VARCHAR(50) NOT NULL DEFAULT 'APPROVED', -- APPROVED, PENDING, NEEDS_REVIEW
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Material Mappings (Data Governance Linkage between Original Codes and Canonical Codes)
CREATE TABLE IF NOT EXISTS material_mappings (
    id BIGSERIAL PRIMARY KEY,
    source_material_id BIGINT NOT NULL REFERENCES source_materials(id) ON DELETE CASCADE,
    cpse_name VARCHAR(100) NOT NULL,
    original_material_code VARCHAR(150) NOT NULL,
    original_description TEXT NOT NULL,
    canonical_material_code VARCHAR(100) NOT NULL REFERENCES canonical_materials(canonical_code),
    canonical_description TEXT NOT NULL,
    match_status VARCHAR(50) NOT NULL, -- MATCH, REVIEW, APPROVED, REJECTED, MANUAL
    confidence NUMERIC(6, 4) NOT NULL,
    reviewer VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Match Candidates (AI Model Suggestions & Explanations)
CREATE TABLE IF NOT EXISTS match_candidates (
    id BIGSERIAL PRIMARY KEY,
    source_material_id BIGINT NOT NULL REFERENCES source_materials(id) ON DELETE CASCADE,
    candidate_source_material_id BIGINT,
    candidate_canonical_code VARCHAR(100),
    lexical_score NUMERIC(6, 4),
    fuzzy_score NUMERIC(6, 4),
    semantic_score NUMERIC(6, 4),
    hybrid_score NUMERIC(6, 4),
    decision VARCHAR(50) NOT NULL, -- MATCH, REVIEW, NOT_MATCH
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Reviews (Human-in-the-Loop Review Queue)
CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    source_material_id BIGINT NOT NULL REFERENCES source_materials(id) ON DELETE CASCADE,
    suggested_canonical_code VARCHAR(100) NOT NULL REFERENCES canonical_materials(canonical_code),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED, NEEDS_REVIEW
    semantic_score NUMERIC(6, 4),
    fuzzy_score NUMERIC(6, 4),
    lexical_score NUMERIC(6, 4),
    hybrid_score NUMERIC(6, 4),
    detected_attributes TEXT,
    conflicts TEXT,
    explanation TEXT,
    reviewer_name VARCHAR(255),
    comments TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Processing Jobs (Asynchronous Ingestion and AI Inference Runs)
CREATE TABLE IF NOT EXISTS processing_jobs (
    id BIGSERIAL PRIMARY KEY,
    job_type VARCHAR(100) NOT NULL, -- UPLOAD, BATCH_MATCH, RE-INDEX
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- PENDING, RUNNING, COMPLETED, FAILED
    total_records INT NOT NULL DEFAULT 0,
    processed_records INT NOT NULL DEFAULT 0,
    error_message TEXT,
    metadata JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. Audit Logs (Immutable Data Governance Trail)
-- CRITICAL SECURITY RULE: Passwords, tokens, and confidential keys must NEVER be stored here.
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    performed_by VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    details JSONB,
    "user" VARCHAR(255)
);

-- =============================================================================
-- High-Performance Enterprise Indexes
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_source_cpse_code ON source_materials(cpse_name, material_code);
CREATE INDEX IF NOT EXISTS idx_source_desc ON source_materials(description);
CREATE INDEX IF NOT EXISTS idx_mappings_orig_code ON material_mappings(cpse_name, original_material_code);
CREATE INDEX IF NOT EXISTS idx_mappings_canon_code ON material_mappings(canonical_material_code);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(status);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_performed_by ON audit_logs(performed_by);
