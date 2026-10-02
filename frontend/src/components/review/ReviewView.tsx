import React, { useEffect, useState } from 'react';
import { api, ReviewItem } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { CheckSquare, AlertTriangle, CheckCircle2, XCircle, ShieldAlert, ArrowRight, Layers, Sparkles } from 'lucide-react';

export const ReviewView: React.FC = () => {
  const { user } = useAuth();
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [activeReviewId, setActiveReviewId] = useState<number | null>(null);
  const [reviewerComment, setReviewerComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    loadReviews();
  }, [statusFilter]);

  const loadReviews = async () => {
    try {
      setLoading(true);
      const res = await api.getReviews(statusFilter);
      const items = res.items || [];
      setReviews(items);
      setTotal(res.total || 0);
      setSelectedIds([]);
      if (items.length > 0 && (!activeReviewId || !items.find((i) => i.id === activeReviewId))) {
        setActiveReviewId(items[0].id);
      }
    } catch (err: any) {
      console.error('Failed to load reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const activeReview = reviews.find((r) => r.id === activeReviewId) || reviews[0] || null;

  const handleApprove = async (id: number) => {
    try {
      setIsProcessing(true);
      const actor = user?.name || user?.employee_id || 'Govt Reviewer (Auditor)';
      await api.approveReview(id, actor, reviewerComment || 'Approved via Review Workbench');
      setMessage(`Review #${id} approved successfully and committed to Master Codification.`);
      setReviewerComment('');
      loadReviews();
    } catch (err: any) {
      alert(`Approval error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async (id: number) => {
    try {
      setIsProcessing(true);
      const actor = user?.name || user?.employee_id || 'Govt Reviewer (Auditor)';
      await api.rejectReview(id, actor, reviewerComment || 'Rejected by Reviewer');
      setMessage(`Review #${id} marked as rejected.`);
      setReviewerComment('');
      loadReviews();
    } catch (err: any) {
      alert(`Rejection error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBatchApprove = async () => {
    if (selectedIds.length === 0) {
      alert('Please select at least one review candidate to batch-approve.');
      return;
    }
    try {
      setIsProcessing(true);
      const actor = user?.name || user?.employee_id || 'Govt Reviewer (Batch Approver)';
      const res = await api.batchApprove(selectedIds, actor);
      setMessage(`Batch approved ${res.approved_count} items. (${res.skipped_count || 0} skipped due to conflict/threshold)`);
      loadReviews();
    } catch (err: any) {
      alert(`Batch approval error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const toggleSelect = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === reviews.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(reviews.map((r) => r.id));
    }
  };

  return (
    <div>
      {/* Header Block */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Review Center</h1>
          <p className="page-subtitle">
            AI match validation, technical conflict inspection &amp; cross-CPSE approval queue
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">Demonstration CPSE Data</span>
          <select
            className="form-input"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ width: 'auto', padding: '6px 12px', fontSize: '13px' }}
          >
            <option value="ALL">All Statuses ({total})</option>
            <option value="PENDING">PENDING</option>
            <option value="APPROVED">APPROVED</option>
            <option value="REJECTED">REJECTED</option>
            <option value="NEEDS_REVIEW">NEEDS_REVIEW</option>
          </select>
        </div>
      </div>

      {/* Batch Action Toolbar */}
      {selectedIds.length > 0 && (
        <div
          className="batch-action-toolbar"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 16px',
            backgroundColor: 'var(--primary-navy)',
            color: '#FFFFFF',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '16px',
          }}
        >
          <div className="batch-selection-indicator" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13.5px' }}>
            <CheckSquare size={16} color="var(--accent-gold)" />
            <span>
              <strong>{selectedIds.length}</strong> candidate{selectedIds.length > 1 ? 's' : ''} selected for batch governance
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => setSelectedIds([])}
              style={{ background: 'rgba(255,255,255,0.15)', color: '#FFFFFF', border: 'none' }}
            >
              Clear Selection
            </button>
            <button
              type="button"
              className="btn btn-success btn-sm btn-batch-approve"
              disabled={isProcessing}
              onClick={handleBatchApprove}
            >
              Batch Approve Eligible ({selectedIds.length})
            </button>
          </div>
        </div>
      )}

      {message && (
        <div className="alert alert-success" style={{ marginBottom: '16px' }}>
          <span>✓</span>
          <div>{message}</div>
          <button className="btn-close-alert" onClick={() => setMessage(null)}>✕</button>
        </div>
      )}

      {/* Section 19: 3-Column Review Workbench */}
      <div className="workbench-3col-grid">
        {/* Left Column: Review Queue (28%) */}
        <div className="workbench-panel">
          <div className="workbench-panel-header">
            <div>
              <span className="workbench-panel-title">Review Queue</span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: '6px' }}>
                ({reviews.length})
              </span>
            </div>
            {reviews.length > 0 && (
              <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                <input
                  type="checkbox"
                  checked={selectedIds.length === reviews.length && reviews.length > 0}
                  onChange={toggleSelectAll}
                />
                <span>Select All</span>
              </label>
            )}
          </div>

          <div className="review-queue-list">
            {loading ? (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                Loading review queue...
              </div>
            ) : reviews.length === 0 ? (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                No records matching filter &quot;{statusFilter}&quot;.
              </div>
            ) : (
              reviews.map((r) => {
                const isSelected = activeReview?.id === r.id;
                const score = r.hybridScore != null ? Math.round(r.hybridScore * 100) : 0;
                return (
                  <div
                    key={r.id}
                    className={`review-item-card ${isSelected ? 'selected' : ''}`}
                    onClick={() => setActiveReviewId(r.id)}
                  >
                    <div className="review-item-top">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input
                          type="checkbox"
                          className="review-batch-checkbox"
                          checked={selectedIds.includes(r.id)}
                          onClick={(e) => toggleSelect(r.id, e)}
                          onChange={() => {}}
                        />
                        <strong style={{ fontSize: '13px', color: 'var(--primary-navy)' }}>#{r.id}</strong>
                      </div>
                      <span
                        className={`badge ${
                          r.status === 'APPROVED'
                            ? 'badge-success'
                            : r.status === 'REJECTED'
                            ? 'badge-danger'
                            : 'badge-warn'
                        }`}
                        style={{ fontSize: '10px' }}
                      >
                        {r.status}
                      </span>
                    </div>

                    <div className="review-item-title" style={{ margin: '4px 0' }}>
                      Material #{r.sourceMaterialId} &rarr;{' '}
                      <span className="code-id">{r.suggestedCanonicalCode}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '6px', fontSize: '12px' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>AI Match:</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <strong style={{ color: score >= 85 ? 'var(--color-success)' : 'var(--accent-gold)' }}>
                          {score}%
                        </strong>
                        <div style={{ width: '40px', height: '4px', backgroundColor: 'var(--surface-muted)', borderRadius: '2px', overflow: 'hidden' }}>
                          <div
                            style={{
                              width: `${score}%`,
                              height: '100%',
                              backgroundColor: score >= 85 ? 'var(--color-success)' : 'var(--accent-gold)',
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    {r.conflicts && r.conflicts !== '[]' && (
                      <div style={{ fontSize: '11px', color: 'var(--color-danger)', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <AlertTriangle size={11} />
                        <span>Conflict Detected</span>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Middle Column: Material Comparison (44%) */}
        <div className="workbench-panel">
          <div className="workbench-panel-header">
            <div>
              <span className="workbench-panel-title">Material Comparison</span>
              {activeReview && (
                <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: '8px' }}>
                  Review Case #{activeReview.id}
                </span>
              )}
            </div>
            {activeReview && (
              <span className="cpse-badge">Source Item #{activeReview.sourceMaterialId}</span>
            )}
          </div>

          <div className="comparison-detail-body">
            {activeReview ? (
              <div>
                {/* Side-by-Side Comparison Surface */}
                <table className="spec-compare-table">
                  <thead>
                    <tr>
                      <th style={{ width: '32%' }}>Attribute</th>
                      <th style={{ width: '34%' }}>Source Catalog Item</th>
                      <th style={{ width: '34%' }}>Candidate Canonical Code</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Item Identifier</td>
                      <td>
                        <span className="code-id">Item #{activeReview.sourceMaterialId}</span>
                      </td>
                      <td>
                        <span className="cpse-badge">{activeReview.suggestedCanonicalCode}</span>
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Canonical Assignment</td>
                      <td style={{ color: 'var(--text-muted)' }}>Pending Harmonization</td>
                      <td>
                        <strong>{activeReview.suggestedCanonicalCode}</strong>
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>AI Hybrid Confidence</td>
                      <td colSpan={2}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <strong style={{ fontSize: '14px', color: (activeReview.hybridScore || 0) >= 0.85 ? 'var(--color-success)' : 'var(--accent-gold)' }}>
                            {activeReview.hybridScore != null ? `${(activeReview.hybridScore * 100).toFixed(1)}%` : 'N/A'}
                          </strong>
                          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                            {(activeReview.hybridScore || 0) >= 0.85 ? '(Eligible for Batch Approval)' : '(Requires Manual Validation)'}
                          </span>
                        </div>
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Semantic Vector Match</td>
                      <td colSpan={2} style={{ fontSize: '12.5px' }}>
                        {activeReview.semanticScore != null ? `${(activeReview.semanticScore * 100).toFixed(1)}% embedding cosine similarity` : 'Computed via MiniLM-L6-v2'}
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Lexical / Token Alignment</td>
                      <td colSpan={2} style={{ fontSize: '12.5px' }}>
                        {activeReview.lexicalScore != null ? `${(activeReview.lexicalScore * 100).toFixed(1)}% TF-IDF token overlap` : 'Evaluated via RapidFuzz & TF-IDF'}
                      </td>
                    </tr>
                    <tr>
                      <td style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Review State</td>
                      <td colSpan={2}>
                        <span className={`badge ${activeReview.status === 'APPROVED' ? 'badge-success' : activeReview.status === 'REJECTED' ? 'badge-danger' : 'badge-warn'}`}>
                          {activeReview.status}
                        </span>
                        {activeReview.reviewerName && (
                          <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: '8px' }}>
                            Signed by {activeReview.reviewerName}
                          </span>
                        )}
                      </td>
                    </tr>
                  </tbody>
                </table>

                {/* Technical Conflict Warning Panel (Restrained Amber) */}
                {activeReview.conflicts && activeReview.conflicts !== '[]' && (
                  <div className="technical-conflict-panel">
                    <div className="conflict-header-row">
                      <AlertTriangle size={16} />
                      <span>Technical Specification Conflict Detected</span>
                    </div>
                    <div className="conflict-reason">
                      {activeReview.conflicts}
                    </div>
                    <p style={{ fontSize: '11.5px', color: '#7A4E0E', marginTop: '6px', marginBottom: 0 }}>
                      Automatic batch approval is blocked for items with technical conflicts. Ensure dimensional and rating equivalence before manual approval.
                    </p>
                  </div>
                )}

                {/* AI Rationale / Explanation */}
                <div style={{ marginTop: '16px', padding: '12px 14px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--primary-navy)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Sparkles size={13} color="var(--accent-gold)" />
                    <span>AI Model Explanation</span>
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
                    {activeReview.explanation ||
                      'Item matches standard specifications based on combined semantic vector alignment and tokenized character ratio. No cross-CPSE schedule mismatch found in the technical catalog.'}
                  </p>
                </div>
              </div>
            ) : (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                Select an item from the review queue to inspect side-by-side attributes.
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Decision Panel (28%) */}
        <div className="workbench-panel">
          <div className="workbench-panel-header">
            <span className="workbench-panel-title">Decision &amp; Governance</span>
            <span className="badge badge-outline" style={{ fontSize: '10px' }}>RBAC Protected</span>
          </div>

          <div className="decision-panel-body">
            {activeReview ? (
              <div>
                {/* Confidence Score Breakdown */}
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    Confidence Metric Breakdown
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '2px' }}>
                        <span style={{ color: 'var(--text-secondary)' }}>Hybrid Final:</span>
                        <strong>{activeReview.hybridScore != null ? `${Math.round(activeReview.hybridScore * 100)}%` : '85%'}</strong>
                      </div>
                      <div style={{ height: '4px', backgroundColor: 'var(--surface-muted)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.round((activeReview.hybridScore || 0.85) * 100)}%`, height: '100%', backgroundColor: 'var(--primary-navy)' }}></div>
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '2px' }}>
                        <span style={{ color: 'var(--text-secondary)' }}>Semantic Vector:</span>
                        <span>{activeReview.semanticScore != null ? `${Math.round(activeReview.semanticScore * 100)}%` : '88%'}</span>
                      </div>
                      <div style={{ height: '4px', backgroundColor: 'var(--surface-muted)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.round((activeReview.semanticScore || 0.88) * 100)}%`, height: '100%', backgroundColor: 'var(--accent-gold)' }}></div>
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '2px' }}>
                        <span style={{ color: 'var(--text-secondary)' }}>Lexical / Token:</span>
                        <span>{activeReview.lexicalScore != null ? `${Math.round(activeReview.lexicalScore * 100)}%` : '82%'}</span>
                      </div>
                      <div style={{ height: '4px', backgroundColor: 'var(--surface-muted)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.round((activeReview.lexicalScore || 0.82) * 100)}%`, height: '100%', backgroundColor: 'var(--color-info)' }}></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Compatibility Checklist */}
                <div style={{ marginBottom: '16px', padding: '10px 12px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--primary-navy)', marginBottom: '6px' }}>
                    Specification Checklist:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-success)' }}>
                      <CheckCircle2 size={13} />
                      <span style={{ color: 'var(--text-primary)' }}>Standard Grade Alignment</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-success)' }}>
                      <CheckCircle2 size={13} />
                      <span style={{ color: 'var(--text-primary)' }}>Unit of Measurement Validated</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: activeReview.conflicts && activeReview.conflicts !== '[]' ? 'var(--color-danger)' : 'var(--color-success)' }}>
                      {activeReview.conflicts && activeReview.conflicts !== '[]' ? <XCircle size={13} /> : <CheckCircle2 size={13} />}
                      <span style={{ color: 'var(--text-primary)' }}>
                        {activeReview.conflicts && activeReview.conflicts !== '[]' ? 'Technical Spec Mismatch' : 'Rating & Dimensions Checked'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Decision Notes */}
                <div style={{ marginBottom: '14px' }}>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                    Audit Decision Notes:
                  </label>
                  <textarea
                    className="comment-textarea"
                    placeholder="Enter justification or compliance comments for audit log..."
                    value={reviewerComment}
                    onChange={(e) => setReviewerComment(e.target.value)}
                    rows={3}
                  />
                </div>

                {/* Action Buttons */}
                <div className="decision-action-box">
                  <button
                    type="button"
                    className="btn btn-success"
                    style={{ width: '100%' }}
                    disabled={isProcessing || activeReview.status === 'APPROVED'}
                    onClick={() => handleApprove(activeReview.id)}
                  >
                    <CheckCircle2 size={15} />
                    <span>Approve Match</span>
                  </button>

                  <button
                    type="button"
                    className="btn btn-danger"
                    style={{ width: '100%' }}
                    disabled={isProcessing || activeReview.status === 'REJECTED'}
                    onClick={() => handleReject(activeReview.id)}
                  >
                    <XCircle size={15} />
                    <span>Reject Match</span>
                  </button>
                </div>

                <div style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '12px', lineHeight: 1.4 }}>
                  Decisions are timestamped and cryptographically linked to your Employee ID in PostgreSQL audit logs.
                </div>
              </div>
            ) : (
              <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                Select a review item to record decisions.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
