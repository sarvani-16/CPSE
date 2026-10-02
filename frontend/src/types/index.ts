/**
 * Enterprise Data Types for SIH26099 CPSE Material Harmonization Platform
 */

export type UserRole = 'ADMIN' | 'REVIEWER' | 'OFFICER';

export interface UserInfo {
  id: number;
  employee_id: string;
  name: string;
  email: string;
  role: UserRole;
  cpse_name?: string;
  status: string;
  is_active: boolean;
  last_login?: string;
}

export interface AuthResponse {
  token: string;
  token_type: string;
  user: UserInfo;
}

export interface SourceMaterial {
  id: number;
  cpseName: string;
  materialCode: string;
  description: string;
  specification?: string;
  materialType?: string;
  materialGrade?: string;
  dimensions?: string;
  unitOfMeasure?: string;
  manufacturer?: string;
  partNumber?: string;
  category?: string;
  sourceFile?: string;
  createdAt?: string;
}

export interface MaterialDetail extends SourceMaterial {
  normalized_info?: {
    normalized_description: string;
    extracted_attributes: Record<string, string>;
    technical_parameters: string;
  };
  status?: string;
  canonical_code?: string;
  mapping?: any;
}

export interface CanonicalMaterial {
  id: number;
  nationalMaterialCode: string;
  codeTypeLabel: string;
  canonicalCode: string;
  standardizedDescription: string;
  category?: string;
  materialType?: string;
  standardSpecification?: string;
  standardUom?: string;
  approvalStatus: string;
}

export interface ReviewItem {
  id: number;
  sourceMaterialId: number;
  suggestedCanonicalCode: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'NEEDS_REVIEW';
  hybridScore?: number;
  semanticScore?: number;
  fuzzyScore?: number;
  lexicalScore?: number;
  conflicts?: string;
  explanation?: string;
  reviewerName?: string;
  comments?: string;
  reviewedAt?: string;
  createdAt?: string;
}

export interface AuditLogItem {
  id: number;
  action: string;
  entityType: string;
  entityId?: string;
  oldValue?: string;
  newValue?: string;
  performedBy: string;
  timestamp: string;
  reason?: string;
}

export interface TaxonomyNode {
  id: number;
  code: string;
  name: string;
  parent_code?: string | null;
  level: number;
  description?: string;
  children?: TaxonomyNode[];
}

export interface ProcessingJob {
  job_id: string;
  cpse_name: string;
  file_name?: string;
  rows_total: number;
  rows_processed: number;
  status: 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  created_at: string;
  completed_at?: string;
}
