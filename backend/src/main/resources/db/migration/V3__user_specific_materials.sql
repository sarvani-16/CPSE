-- =============================================================================
-- SIH26099: V3 Migration - User-Specific Data Isolation
-- Associates uploaded materials and audit logs with user_id foreign key
-- =============================================================================

-- Add user_id to source_materials
ALTER TABLE source_materials ADD COLUMN IF NOT EXISTS user_id BIGINT REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_source_material_user_id ON source_materials(user_id);

-- Drop old global unique constraint across all users if present
ALTER TABLE source_materials DROP CONSTRAINT IF EXISTS uq_source_cpse_code;
ALTER TABLE source_materials DROP CONSTRAINT IF EXISTS source_materials_cpse_name_material_code_key;

-- Add user-scoped unique index for active users
CREATE UNIQUE INDEX IF NOT EXISTS uq_source_user_cpse_code ON source_materials(user_id, cpse_name, material_code) WHERE user_id IS NOT NULL;

-- Add user_id to audit_logs
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS user_id BIGINT REFERENCES users(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_logs(user_id);
