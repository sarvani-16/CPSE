/**
 * Centralized Enterprise API Client for SIH26099 React Frontend.
 * ARCHITECTURAL BOUNDARY:
 * React communicates EXCLUSIVELY with the Spring Boot Backend (default: http://localhost:8080/api).
 * React NEVER directly accesses PostgreSQL, FastAPI ML Service (8001), or SQLite.
 * Spring Security enforces JWT validation & RBAC (ADMIN, REVIEWER, OFFICER).
 */

// Resolve Backend API URL from environment variables (VITE_API_URL or VITE_API_BASE_URL)
const resolveBaseUrl = (): string => {
  const envUrl = (import.meta as any).env?.VITE_API_URL || (import.meta as any).env?.VITE_API_BASE_URL;
  if (!envUrl) {
    return '/api';
  }
  let trimmed = String(envUrl).trim();
  // If host only without protocol (e.g. cpse-backend.onrender.com), prepend https://
  if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://') && !trimmed.startsWith('/')) {
    trimmed = `https://${trimmed}`;
  }
  // Ensure it ends with /api
  if (trimmed.endsWith('/api')) {
    return trimmed;
  }
  return `${trimmed.replace(/\/+$/, '')}/api`;
};

export const BASE_URL: string = resolveBaseUrl();
export const ML_BASE_URL: string = (import.meta as any).env?.VITE_ML_API_URL || '';

export interface UserInfo {
  id: number;
  employee_id: string;
  name: string;
  email: string;
  role: 'ADMIN' | 'REVIEWER' | 'OFFICER';
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

export interface CompareRequest {
  title_a: string;
  title_b: string;
}

export interface CompareResponse {
  title_a: string;
  title_b: string;
  match_decision: 'MATCH' | 'REVIEW' | 'NOT_MATCH';
  hybrid_score: number;
  semantic_score: number;
  lexical_score: number;
  fuzzy_score: number;
  explanation: string[];
  technical_tokens?: {
    matching?: string[];
    conflicts?: string[];
    differing_a?: string[];
    differing_b?: string[];
    has_conflicts?: boolean;
  };
  sub_scores?: Record<string, number>;
  weights?: Record<string, number>;
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

export interface CanonicalMaterialItem {
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

export interface DashboardOverview {
  summary: {
    total_materials: number;
    potential_duplicates: number;
    high_confidence_matches: number;
    pending_reviews: number;
    harmonized_materials: number;
    cpse_sources: number;
    duplicate_ratio?: number;
  };
  charts: {
    by_cpse?: { labels: string[]; counts: number[] };
    review_status?: { labels: string[]; counts: number[] };
    category_distribution?: { labels: string[]; counts: number[] };
    duplicate_trend?: { labels: string[]; cumulative: number[] };
  };
  pipeline_status?: Array<{ stage: string; status: string; records: number }>;
}

export interface AdminDashboardData {
  summary: {
    total_materials: number;
    cpse_sources: number;
    potential_matches: number;
    pending_reviews: number;
    harmonized_materials: number;
    canonical_materials: number;
    active_users: number;
    total_users?: number;
    processing_jobs: number;
    technical_conflicts?: number;
  };
  charts: {
    by_cpse: { labels: string[]; counts: number[] };
    match_distribution: { labels: string[]; counts: number[] };
    review_status: { labels: string[]; counts: number[] };
    processing_activity: { labels: string[]; counts: number[] };
    category_distribution: { labels: string[]; counts: number[] };
  };
  recent_activity: AuditLogItem[];
  recent_processing_jobs: Array<{ id: string; cpse: string; material_code: string; status: string; timestamp: string }>;
  system_health: Record<string, string>;
}

export interface ReviewerDashboardData {
  summary: {
    pending_reviews: number;
    needs_review: number;
    technical_conflicts: number;
    high_confidence_recommendations: number;
    recently_approved: number;
    recently_rejected: number;
  };
  review_queue: Array<{
    id: number;
    source_material_id: number;
    source_material_code: string;
    source_description: string;
    source_cpse: string;
    candidate_canonical_code: string;
    candidate_description: string;
    similarity: number;
    technical_status: string;
    recommendation: string;
    status: string;
    conflicts?: string;
    explanation?: string;
  }>;
}

export interface OfficerDashboardData {
  summary: {
    my_materials: number;
    uploaded_today: number;
    processing: number;
    ai_recommendations: number;
    materials_requiring_attention: number;
    harmonized_materials: number;
    cpse_name: string;
  };
  my_recent_uploads: Array<{
    id: number;
    cpseName: string;
    materialCode: string;
    description: string;
    category?: string;
    createdAt?: string;
  }>;
  processing_status: Array<{ stage: string; status: string; records: number }>;
  recent_recommendations: Array<{
    id: number;
    material_code: string;
    description: string;
    suggested_canonical: string;
    score: number;
    status: string;
    conflicts?: string;
  }>;
  material_activity: AuditLogItem[];
}

export const TOKEN_KEY = 'sih26099_jwt_token';
export const USER_KEY = 'sih26099_auth_user';

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredSession(token: string, user: UserInfo): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearStoredSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): UserInfo | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const token = getStoredToken();

  const headers: Record<string, string> = {
    ...(options?.headers as Record<string, string> || {}),
  };

  // Only set Content-Type JSON if not FormData
  if (!(options?.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      clearStoredSession();
      window.dispatchEvent(new CustomEvent('session-expired', { detail: { message: 'Your session has expired. Please sign in again.' } }));
      throw new Error('Your session has expired. Please sign in again.');
    }

    if (res.status === 403) {
      window.dispatchEvent(new CustomEvent('forbidden-access', { detail: { message: 'Access Restricted: You do not have permission for this section.' } }));
      throw new Error('Access Restricted: You do not have permission to access this resource.');
    }

    if (!res.ok) {
      const errorText = await res.text();
      let errorJson: any;
      try {
        errorJson = JSON.parse(errorText);
      } catch {
        errorJson = { message: errorText || `HTTP ${res.status} ${res.statusText}` };
      }
      throw new Error(errorJson.message || errorJson.error || `Request failed with status ${res.status}`);
    }

    return await res.json();
  } catch (err: any) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

async function downloadFile(endpoint: string, fallbackFilename = 'report.csv'): Promise<void> {
  const url = `${BASE_URL}${endpoint}`;
  const token = getStoredToken();

  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, { headers });

    if (res.status === 401) {
      clearStoredSession();
      window.dispatchEvent(new CustomEvent('session-expired', { detail: { message: 'Your session has expired. Please sign in again.' } }));
      throw new Error('Session expired. Please sign in again.');
    }

    if (res.status === 403) {
      window.dispatchEvent(new CustomEvent('forbidden-access', { detail: { message: 'Access Restricted: You do not have permission for this section.' } }));
      throw new Error('Access Restricted: You do not have permission to download this report.');
    }

    if (!res.ok) {
      const errorText = await res.text();
      let errorJson: any;
      try {
        errorJson = JSON.parse(errorText);
      } catch {
        errorJson = { message: errorText || `HTTP ${res.status} ${res.statusText}` };
      }
      throw new Error(errorJson.message || errorJson.error || `Export failed with status ${res.status}`);
    }

    // Extract filename from Content-Disposition header
    let filename = fallbackFilename;
    const disposition = res.headers.get('content-disposition');
    if (disposition && disposition.includes('filename=')) {
      const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, '').trim();
      }
    }

    const blob = await res.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(blobUrl);
  } catch (err: any) {
    console.error(`Export Download Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // 1. Authentication & Identity
  login: (credentials: { username: string; password: string }) =>
    request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  register: (payload: { employee_id: string; name: string; email: string; password: string; cpse_name: string }) =>
    request<UserInfo>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getMe: () => request<UserInfo>('/auth/me'),

  logout: () =>
    request<{ message: string }>('/auth/logout', {
      method: 'POST',
    }),

  // 2. Role-Based Dashboards
  getAdminDashboard: () => request<AdminDashboardData>('/dashboard/admin'),
  getReviewerDashboard: () => request<ReviewerDashboardData>('/dashboard/reviewer'),
  getOfficerDashboard: () => request<OfficerDashboardData>('/dashboard/officer'),
  getDashboardOverview: () => request<DashboardOverview>('/dashboard/overview'),

  // 3. User & Role Management (ADMIN ONLY)
  getUsers: (role?: string, search?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (role && role !== 'ALL') params.append('role', role);
    if (search) params.append('search', search);
    return request<{ total: number; page: number; total_pages: number; items: UserInfo[] }>(`/users?${params.toString()}`);
  },

  changeUserRole: (id: number, role: string) =>
    request<UserInfo>(`/users/${id}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    }),

  changeUserStatus: (id: number, active: boolean) =>
    request<UserInfo>(`/users/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ active, status: active ? 'ACTIVE' : 'INACTIVE' }),
    }),

  // 4. Material Submission (OFFICER & ADMIN)
  uploadMaterials: (file: File, cpseName: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('cpse_name', cpseName);
    return request<any>('/materials/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // 5. AI Matching (Spring Boot -> FastAPI ML Service)
  compareMaterials: (data: CompareRequest) =>
    request<CompareResponse>('/matching/compare', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 6. Human Review Center (REVIEWER & ADMIN)
  getReviews: (status?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (status && status !== 'ALL') params.append('status', status);
    return request<{ total: number; page: number; total_pages: number; items: ReviewItem[] }>(`/reviews?${params.toString()}`);
  },

  approveReview: (id: number, reviewerName: string, comment?: string) =>
    request<any>(`/reviews/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ reviewer_name: reviewerName, comment }),
    }),

  rejectReview: (id: number, reviewerName: string, comment?: string) =>
    request<any>(`/reviews/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ reviewer_name: reviewerName, comment }),
    }),

  batchApprove: (reviewIds: number[], reviewerName: string, minConfidence = 0.80) =>
    request<any>('/reviews/batch-approve', {
      method: 'POST',
      body: JSON.stringify({ review_ids: reviewIds, reviewer_name: reviewerName, min_confidence: minConfidence }),
    }),

  // 7. Canonical Materials Master
  getCanonicalMaterials: (search?: string, category?: string, status?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.append('search', search);
    if (category) params.append('category', category);
    if (status && status !== 'ALL') params.append('approval_status', status);
    return request<{ total: number; page: number; total_pages: number; items: CanonicalMaterialItem[] }>(`/canonical-materials?${params.toString()}`);
  },

  autoCreateCanonical: (payload: { description: string; cpse_name?: string; material_code?: string; category?: string }) =>
    request<any>('/canonical-materials/auto-create', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // 8. Enterprise Governance & Audit Trail
  getAuditLogs: (filters: { action?: string; entity?: string; user?: string; date?: string; page?: number; pageSize?: number }) => {
    const params = new URLSearchParams();
    if (filters.action) params.append('action', filters.action);
    if (filters.entity) params.append('entity', filters.entity);
    if (filters.user) params.append('user', filters.user);
    if (filters.date) params.append('date', filters.date);
    params.append('page', String(filters.page || 1));
    params.append('page_size', String(filters.pageSize || 25));
    return request<{ total: number; page: number; total_pages: number; items: AuditLogItem[]; available_actions?: string[]; available_entities?: string[]; available_users?: string[] }>(`/audit-logs?${params.toString()}`);
  },

  getAuditExportUrl: (action?: string, date?: string) => {
    const params = new URLSearchParams();
    if (action && action !== 'ALL') params.append('action', action);
    if (date && date !== 'ALL') params.append('date', date);
    return `${BASE_URL}/audit-logs/export?${params.toString()}`;
  },

  exportAuditLogsCsv: (action?: string, date?: string) => {
    const params = new URLSearchParams();
    if (action && action !== 'ALL') params.append('action', action);
    if (date && date !== 'ALL') params.append('date', date);
    return downloadFile(`/audit-logs/export?${params.toString()}`, 'audit-report.csv');
  },

  exportReport: (type: string, filters?: { cpse?: string; status?: string; date?: string; search?: string; action?: string }) => {
    const params = new URLSearchParams({ type });
    if (filters?.cpse && filters.cpse !== 'ALL') params.append('cpse', filters.cpse);
    if (filters?.status && filters.status !== 'ALL') params.append('status', filters.status);
    if (filters?.date && filters.date !== 'ALL') params.append('date', filters.date);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.action && filters.action !== 'ALL') params.append('action', filters.action);
    return downloadFile(`/reports/export?${params.toString()}`, `${type}-report.csv`);
  },

  exportMaterialsMasterCsv: (cpse?: string, search?: string) => {
    const params = new URLSearchParams();
    if (cpse && cpse !== 'ALL') params.append('cpse_name', cpse);
    if (search) params.append('search', search);
    return downloadFile(`/materials/export?${params.toString()}`, 'material-master-report.csv');
  },

  // 9. Source Material Catalog
  getSourceMaterials: async (cpseName?: string, search?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (cpseName && cpseName !== 'ALL') params.append('cpse_name', cpseName);
    if (search) params.append('search', search);
    const data = await request<any>(`/materials/source?${params.toString()}`);
    const items = data.items || data.materials || data.content || [];
    const total = data.total ?? data.totalElements ?? items.length;
    const total_pages = data.total_pages ?? data.totalPages ?? Math.ceil(total / pageSize) ?? 1;
    return {
      items,
      materials: items,
      total,
      total_pages,
      page: data.page ?? page,
      page_size: data.page_size ?? pageSize,
    };
  },

  getMaterialDetail: (id: number) => request<any>(`/materials/${id}`),

  // 10. Taxonomy & Commodity Classifications
  getTaxonomyTree: () => request<any[]>('/taxonomy'),
  createTaxonomy: (item: { code: string; name: string; parent_code?: string; level: number; description?: string }) =>
    request<any>('/taxonomy', {
      method: 'POST',
      body: JSON.stringify(item),
    }),

  // 11. Pipeline Processing Jobs
  getJobStatus: (jobId: string) => request<any>(`/jobs/${jobId}`),
  getRecentJobs: () => request<any[]>('/jobs'),

  // 12. Safe AI Telemetry & Model Status (ADMIN ONLY)
  getModelStatus: () => request<any>('/model-status'),

  getHealth: () => request<any>('/health'),
};
