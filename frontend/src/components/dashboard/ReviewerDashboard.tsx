import React, { useEffect, useState } from 'react';
import { api, ReviewerDashboardData } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { CheckSquare, AlertTriangle, CheckCircle2, XCircle, ArrowRight, ShieldCheck } from 'lucide-react';

export const ReviewerDashboard: React.FC<{ onNavigateToReview?: () => void }> = ({ onNavigateToReview }) => {
  const { user } = useAuth();
  const [data, setData] = useState<ReviewerDashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchReviewerDashboard();
  }, []);

  const fetchReviewerDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getReviewerDashboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load reviewer dashboard.');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await api.approveReview(id, user?.name || user?.employee_id || 'REVIEWER', 'Approved via Reviewer Dashboard');
      setActionMessage(`Review #${id} approved successfully.`);
      fetchReviewerDashboard();
    } catch (err: any) {
      setError(err.message || `Failed to approve review #${id}`);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await api.rejectReview(id, user?.name || user?.employee_id || 'REVIEWER', 'Rejected via Reviewer Dashboard');
      setActionMessage(`Review #${id} marked as rejected.`);
      fetchReviewerDashboard();
    } catch (err: any) {
      setError(err.message || `Failed to reject review #${id}`);
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
        <strong>Error:</strong> {error || 'Unable to retrieve reviewer dashboard.'}
        <button className="btn btn-secondary btn-sm" style={{ marginLeft: '12px' }} onClick={fetchReviewerDashboard}>
          Retry
        </button>
      </div>
    );
  }

  const { summary, review_queue } = data;

  return (
    <div>
      {/* Header Block matching Section 11 */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Review Center</h1>
          <p className="page-subtitle">
            AI match validation, technical conflict inspection &amp; cross-CPSE approval queue
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Demonstration CPSE Data
          </span>
          {onNavigateToReview && (
            <button className="btn btn-primary" onClick={onNavigateToReview}>
              <span>Open 3-Column Workbench</span>
              <ArrowRight size={14} />
            </button>
          )}
        </div>
      </div>

      {actionMessage && (
        <div className="alert alert-success" style={{ marginBottom: '16px' }}>
          <span>✓</span>
          <div>{actionMessage}</div>
          <button className="btn-close-alert" onClick={() => setActionMessage(null)}>✕</button>
        </div>
      )}

      {/* 6 Reviewer KPIs */}
      <div className="kpi-row-grid">
        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Pending Reviews</span>
            <CheckSquare size={14} color="var(--color-warning)" />
          </div>
          <div className="kpi-block-value text-warn">{summary.pending_reviews}</div>
          <div className="kpi-block-subtext">Awaiting evaluation</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Needs Review</span>
            <AlertTriangle size={14} color="var(--accent-gold)" />
          </div>
          <div className="kpi-block-value" style={{ color: 'var(--accent-gold)' }}>{summary.needs_review}</div>
          <div className="kpi-block-subtext">Flagged for human check</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Technical Conflicts</span>
            <AlertTriangle size={14} color="var(--color-danger)" />
          </div>
          <div className="kpi-block-value text-danger">{summary.technical_conflicts}</div>
          <div className="kpi-block-subtext">Dimensional / spec mismatches</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>High Confidence</span>
            <ShieldCheck size={14} color="var(--color-success)" />
          </div>
          <div className="kpi-block-value text-success">{summary.high_confidence_recommendations}</div>
          <div className="kpi-block-subtext">Score &ge; 85% with zero conflicts</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Recently Approved</span>
            <CheckCircle2 size={14} color="var(--primary-navy)" />
          </div>
          <div className="kpi-block-value">{summary.recently_approved}</div>
          <div className="kpi-block-subtext">Codified to NMM canonicals</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Recently Rejected</span>
            <XCircle size={14} color="var(--text-secondary)" />
          </div>
          <div className="kpi-block-value">{summary.recently_rejected}</div>
          <div className="kpi-block-subtext">Unsuitable / distinct parts</div>
        </div>
      </div>

      {/* Prioritized Review Queue Table */}
      <div className="table-surface">
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Prioritized Validation Queue</div>
            <div className="table-surface-subtitle">
              Candidates sorted by AI confidence score and technical compliance
            </div>
          </div>
          {onNavigateToReview && (
            <button className="btn btn-secondary btn-sm" onClick={onNavigateToReview}>
              Workbench View &rarr;
            </button>
          )}
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Source Material</th>
                <th>Candidate Material</th>
                <th>Similarity</th>
                <th>Technical Status</th>
                <th>Recommendation</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {review_queue && review_queue.length > 0 ? (
                review_queue.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                        <span className="cpse-badge">{item.source_cpse}</span>
                        <span className="code-id">{item.source_material_code}</span>
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '240px' }}>
                        {item.source_description}
                      </div>
                    </td>
                    <td>
                      <div style={{ marginBottom: '3px' }}>
                        <span className="cpse-badge" style={{ background: 'var(--surface-muted)', color: 'var(--primary-navy)', borderColor: 'var(--border-color)' }}>
                          {item.candidate_canonical_code}
                        </span>
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '240px' }}>
                        {item.candidate_description}
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <strong style={{ fontSize: '13px', color: item.similarity >= 0.85 ? 'var(--color-success)' : 'var(--accent-gold)' }}>
                          {Math.round((item.similarity || 0) * 100)}%
                        </strong>
                        <div style={{ width: '48px', height: '5px', backgroundColor: 'var(--surface-muted)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div
                            style={{
                              width: `${Math.round((item.similarity || 0) * 100)}%`,
                              height: '100%',
                              backgroundColor: item.similarity >= 0.85 ? 'var(--color-success)' : 'var(--accent-gold)',
                            }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td>
                      {item.technical_status === 'CONFLICT_DETECTED' ? (
                        <span className="badge badge-danger">CONFLICT DETECTED</span>
                      ) : (
                        <span className="badge badge-success">COMPATIBLE</span>
                      )}
                      {item.conflicts && item.conflicts !== '[]' && (
                        <div style={{ fontSize: '11px', color: 'var(--color-danger)', marginTop: '2px' }}>
                          {item.conflicts}
                        </div>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${item.recommendation === 'AUTO_APPROVE_ELIGIBLE' ? 'badge-success' : 'badge-warn'}`}>
                        {item.recommendation}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '6px' }}>
                        <button
                          type="button"
                          className="btn btn-success btn-sm"
                          onClick={() => handleApprove(item.id)}
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => handleReject(item.id)}
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                    No pending review items found in PostgreSQL database.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
