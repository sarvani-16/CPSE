import React, { useEffect, useState } from 'react';
import { api, OfficerDashboardData } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { UploadCloud, CheckCircle2, Clock, AlertTriangle, Layers, Sparkles } from 'lucide-react';

export const OfficerDashboard: React.FC<{ onNavigateToUpload?: () => void }> = ({ onNavigateToUpload }) => {
  const { user } = useAuth();
  const [data, setData] = useState<OfficerDashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOfficerDashboard();
  }, []);

  const fetchOfficerDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getOfficerDashboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load material operations dashboard.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px 0', textAlign: 'center' }}>
        <div className="skeleton-line" style={{ width: '40%', height: '24px', margin: '0 auto 12px auto' }}></div>
        <div className="skeleton-line" style={{ width: '60%', height: '14px', margin: '0 auto 24px auto' }}></div>
        <div className="kpi-row-grid">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="skeleton-card" style={{ height: '80px' }}></div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="alert alert-danger">
        <strong>Error:</strong> {error || 'Unable to retrieve operations dashboard.'}
        <button className="btn btn-secondary btn-sm" style={{ marginLeft: '12px' }} onClick={fetchOfficerDashboard}>
          Retry
        </button>
      </div>
    );
  }

  const { summary, my_recent_uploads, processing_status, recent_recommendations, material_activity } = data;

  return (
    <div>
      {/* Header Block matching Section 11 */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Material Operations</h1>
          <p className="page-subtitle">
            Enterprise ingestion, status tracking &amp; codification for {summary.cpse_name}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Demonstration CPSE Data
          </span>
          {onNavigateToUpload && (
            <button className="btn btn-primary" onClick={onNavigateToUpload}>
              <UploadCloud size={15} />
              <span>Upload Materials</span>
            </button>
          )}
        </div>
      </div>

      {/* 6 Compact KPI Blocks */}
      <div className="kpi-row-grid">
        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>My Materials</span>
            <Layers size={14} color="var(--primary-navy)" />
          </div>
          <div className="kpi-block-value">{summary.my_materials}</div>
          <div className="kpi-block-subtext">Catalog items for {summary.cpse_name}</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Uploaded Materials</span>
            <UploadCloud size={14} color="var(--accent-gold)" />
          </div>
          <div className="kpi-block-value" style={{ color: 'var(--accent-gold)' }}>
            {summary.uploaded_today}
          </div>
          <div className="kpi-block-subtext">Recent catalog batch</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Processing</span>
            <Clock size={14} color="var(--color-warning)" />
          </div>
          <div className="kpi-block-value text-warn">{summary.processing}</div>
          <div className="kpi-block-subtext">Pipeline validation active</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>AI Recommendations</span>
            <Sparkles size={14} color="var(--color-info)" />
          </div>
          <div className="kpi-block-value text-info">{summary.ai_recommendations}</div>
          <div className="kpi-block-subtext">Candidate matches found</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Potential Duplicates</span>
            <AlertTriangle size={14} color="var(--color-danger)" />
          </div>
          <div className="kpi-block-value text-danger">{summary.materials_requiring_attention}</div>
          <div className="kpi-block-subtext">Conflicts / Low similarity</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Harmonized Materials</span>
            <CheckCircle2 size={14} color="var(--color-success)" />
          </div>
          <div className="kpi-block-value text-success">{summary.harmonized_materials}</div>
          <div className="kpi-block-subtext">Mapped to Common Code</div>
        </div>
      </div>

      {/* Row 1: Processing Pipeline Throughput & AI Recommendations */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 4fr) minmax(360px, 5fr)', gap: '16px', marginBottom: '16px' }}>
        {/* Processing Pipeline Stages */}
        <div className="table-surface" style={{ marginBottom: 0 }}>
          <div className="table-surface-header">
            <div>
              <div className="table-surface-title">Processing Pipeline Status</div>
              <div className="table-surface-subtitle">Pipeline throughput for {summary.cpse_name}</div>
            </div>
            <span className="cpse-badge">{summary.cpse_name}</span>
          </div>
          <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {processing_status.map((item, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '9px 12px',
                  backgroundColor: 'var(--surface-subtle)',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary-navy)' }}>
                    {item.stage}
                  </div>
                  <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                    <strong>{item.records}</strong> records processed
                  </div>
                </div>
                <span className="badge badge-success">{item.status}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent AI Recommendations */}
        <div className="table-surface" style={{ marginBottom: 0 }}>
          <div className="table-surface-header">
            <div>
              <div className="table-surface-title">Recent AI Recommendations</div>
              <div className="table-surface-subtitle">Top match suggestions from MiniLM + Lexical</div>
            </div>
            <span className="badge badge-gold" style={{ fontSize: '11px' }}>MiniLM Hybrid</span>
          </div>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Material Code</th>
                  <th>Suggested Canonical</th>
                  <th>Confidence</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recent_recommendations && recent_recommendations.length > 0 ? (
                  recent_recommendations.map((rec) => (
                    <tr key={rec.id}>
                      <td>
                        <span className="code-id">{rec.material_code}</span>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {rec.description}
                        </div>
                      </td>
                      <td>
                        <span className="cpse-badge">{rec.suggested_canonical}</span>
                      </td>
                      <td>
                        <strong>{Math.round((rec.score || 0) * 100)}%</strong>
                      </td>
                      <td>
                        <span className={`badge ${rec.status === 'APPROVED' ? 'badge-success' : rec.status === 'PENDING' ? 'badge-warn' : 'badge-danger'}`}>
                          {rec.status}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                      No recent recommendations found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Row 2: Recent Uploads & Material Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* My Recent Uploads */}
        <div className="table-surface">
          <div className="table-surface-header">
            <div>
              <div className="table-surface-title">Recent Catalog Ingestion ({summary.cpse_name})</div>
              <div className="table-surface-subtitle">Latest materials ingested into master repository</div>
            </div>
          </div>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Description</th>
                  <th>Category</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {my_recent_uploads && my_recent_uploads.length > 0 ? (
                  my_recent_uploads.map((m) => (
                    <tr key={m.id}>
                      <td><span className="code-id">{m.materialCode}</span></td>
                      <td style={{ maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {m.description}
                      </td>
                      <td><span className="group-pill">{m.category || 'General'}</span></td>
                      <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {m.createdAt ? new Date(m.createdAt).toLocaleDateString() : 'Active'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                      No uploads recorded for {summary.cpse_name}.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Material Activity Audit */}
        <div className="table-surface">
          <div className="table-surface-header">
            <div>
              <div className="table-surface-title">Material Activity Trail</div>
              <div className="table-surface-subtitle">Recent governance actions and system events</div>
            </div>
            <span className="badge badge-outline" style={{ fontSize: '11px' }}>Governance</span>
          </div>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Actor</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {material_activity && material_activity.length > 0 ? (
                  material_activity.map((act) => (
                    <tr key={act.id}>
                      <td><span className="badge badge-outline">{act.action}</span></td>
                      <td>{act.entityType} {act.entityId ? `(#${act.entityId})` : ''}</td>
                      <td style={{ fontWeight: 500 }}>{act.performedBy}</td>
                      <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {new Date(act.timestamp).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                      No recent activity for this workspace.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
