import React, { useEffect, useState } from 'react';
import { api, AdminDashboardData } from '../../services/api';
import { Users, Package, Building2, CheckSquare, Layers, Clock, AlertTriangle, CheckCircle2, Activity } from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [data, setData] = useState<AdminDashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getAdminDashboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load administration dashboard.');
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
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="skeleton-card" style={{ height: '80px' }}></div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="alert alert-danger">
        <strong>Error:</strong> {error || 'Unable to retrieve dashboard metrics.'}
        <button className="btn btn-secondary btn-sm" style={{ marginLeft: '12px' }} onClick={fetchDashboard}>
          Retry
        </button>
      </div>
    );
  }

  const { summary, charts, recent_activity, recent_processing_jobs, system_health } = data;

  return (
    <div>
      {/* Header Block matching Section 11 */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">System Administration</h1>
          <p className="page-subtitle">
            System-wide material harmonization, tenant management &amp; governance overview
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Demonstration CPSE Data
          </span>
          <button className="btn btn-secondary btn-sm" onClick={fetchDashboard}>
            <Activity size={13} />
            <span>Refresh Telemetry</span>
          </button>
        </div>
      </div>

      {/* 8 Operational KPIs */}
      <div className="kpi-row-grid">
        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Total Users</span>
            <Users size={14} color="var(--primary-navy)" />
          </div>
          <div className="kpi-block-value">{summary.total_users ?? summary.active_users}</div>
          <div className="kpi-block-subtext">Configured enterprise users</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Total Materials</span>
            <Package size={14} color="var(--primary-navy)" />
          </div>
          <div className="kpi-block-value">{summary.total_materials.toLocaleString()}</div>
          <div className="kpi-block-subtext">Ingested across CPSEs</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>CPSE Sources</span>
            <Building2 size={14} color="var(--primary-navy)" />
          </div>
          <div className="kpi-block-value">{summary.cpse_sources}</div>
          <div className="kpi-block-subtext">Participating CPSE entities</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Pending Reviews</span>
            <CheckSquare size={14} color="var(--color-warning)" />
          </div>
          <div className="kpi-block-value text-warn">{summary.pending_reviews.toLocaleString()}</div>
          <div className="kpi-block-subtext">Awaiting auditor decision</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Harmonized Materials</span>
            <CheckCircle2 size={14} color="var(--color-success)" />
          </div>
          <div className="kpi-block-value text-success">{summary.harmonized_materials.toLocaleString()}</div>
          <div className="kpi-block-subtext">Linked to standard codes</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Canonical Materials</span>
            <Layers size={14} color="var(--accent-gold)" />
          </div>
          <div className="kpi-block-value" style={{ color: 'var(--accent-gold)' }}>
            {summary.canonical_materials.toLocaleString()}
          </div>
          <div className="kpi-block-subtext">National Master (NMM)</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Processing Jobs</span>
            <Clock size={14} color="var(--color-info)" />
          </div>
          <div className="kpi-block-value text-info">{summary.processing_jobs}</div>
          <div className="kpi-block-subtext">Batch pipelines executed</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Technical Conflicts</span>
            <AlertTriangle size={14} color="var(--color-danger)" />
          </div>
          <div className="kpi-block-value text-danger">{summary.technical_conflicts ?? 0}</div>
          <div className="kpi-block-subtext">Spec / grade mismatches</div>
        </div>
      </div>

      {/* System Infrastructure Health Strip */}
      <div
        style={{
          backgroundColor: 'var(--surface-white)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-sm)',
          padding: '12px 18px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={16} color="var(--color-success)" />
          <strong style={{ fontSize: '13px', color: 'var(--primary-navy)' }}>
            Microservices &amp; Infrastructure Health:
          </strong>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          {Object.entries(system_health || {}).map(([service, status]) => (
            <div key={service} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: status.toLowerCase().includes('ok') || status.toLowerCase().includes('up') || status.toLowerCase().includes('active')
                    ? 'var(--color-success)'
                    : 'var(--color-warning)',
                }}
              ></span>
              <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>{service.toUpperCase()}:</span>
              <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{status}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 4 Analytical Distribution Surfaces */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        {/* CPSE Distribution */}
        <div className="table-surface" style={{ marginBottom: 0 }}>
          <div className="table-surface-header">
            <div className="table-surface-title">Materials by CPSE</div>
          </div>
          <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {charts.by_cpse?.labels.map((label, idx) => {
              const count = charts.by_cpse.counts[idx];
              const max = Math.max(...charts.by_cpse.counts, 1);
              const pct = Math.round((count / max) * 100);
              return (
                <div key={label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--primary-navy)' }}>{label}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{count.toLocaleString()}</span>
                  </div>
                  <div style={{ height: '6px', backgroundColor: 'var(--surface-muted)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', backgroundColor: 'var(--primary-navy)' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Match Distribution */}
        <div className="table-surface" style={{ marginBottom: 0 }}>
          <div className="table-surface-header">
            <div className="table-surface-title">Match Distribution</div>
          </div>
          <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {charts.match_distribution?.labels.map((label, idx) => {
              const count = charts.match_distribution.counts[idx];
              const max = Math.max(...charts.match_distribution.counts, 1);
              const pct = Math.round((count / max) * 100);
              const color = idx === 0 ? 'var(--color-success)' : idx === 1 ? 'var(--accent-gold)' : 'var(--color-warning)';
              return (
                <div key={label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{label}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{count.toLocaleString()}</span>
                  </div>
                  <div style={{ height: '6px', backgroundColor: 'var(--surface-muted)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', backgroundColor: color }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Review Status Breakdown */}
        <div className="table-surface" style={{ marginBottom: 0 }}>
          <div className="table-surface-header">
            <div className="table-surface-title">Review Status Breakdown</div>
          </div>
          <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {charts.review_status?.labels.map((label, idx) => {
              const count = charts.review_status.counts[idx];
              const max = Math.max(...charts.review_status.counts, 1);
              const pct = Math.round((count / max) * 100);
              const color = label.toUpperCase().includes('APPROVED')
                ? 'var(--color-success)'
                : label.toUpperCase().includes('PENDING')
                ? 'var(--color-warning)'
                : 'var(--color-danger)';
              return (
                <div key={label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{label}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{count.toLocaleString()}</span>
                  </div>
                  <div style={{ height: '6px', backgroundColor: 'var(--surface-muted)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', backgroundColor: color }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Processing Pipeline Activity */}
        <div className="table-surface" style={{ marginBottom: 0 }}>
          <div className="table-surface-header">
            <div className="table-surface-title">Pipeline Throughput</div>
          </div>
          <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {charts.processing_activity?.labels.map((label, idx) => {
              const count = charts.processing_activity.counts[idx];
              const max = Math.max(...charts.processing_activity.counts, 1);
              const pct = Math.round((count / max) * 100);
              return (
                <div key={label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--primary-navy)' }}>{label}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{count.toLocaleString()}</span>
                  </div>
                  <div style={{ height: '6px', backgroundColor: 'var(--surface-muted)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', backgroundColor: 'var(--color-info)' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Row: Recent System Activity & Ingestion Jobs */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Recent Audit / System Activity */}
        <div className="table-surface">
          <div className="table-surface-header">
            <div>
              <div className="table-surface-title">Recent System &amp; Audit Activity</div>
              <div className="table-surface-subtitle">Latest tamper-evident logs across CPSE nodes</div>
            </div>
            <span className="badge badge-outline" style={{ fontSize: '11px' }}>Immutable Log</span>
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
                {recent_activity && recent_activity.length > 0 ? (
                  recent_activity.slice(0, 6).map((log) => (
                    <tr key={log.id}>
                      <td>
                        <span className="badge badge-outline">{log.action}</span>
                      </td>
                      <td>{log.entityType} {log.entityId ? `(#${log.entityId})` : ''}</td>
                      <td style={{ fontWeight: 500 }}>{log.performedBy}</td>
                      <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                      No audit activity recorded.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Ingestion Jobs */}
        <div className="table-surface">
          <div className="table-surface-header">
            <div>
              <div className="table-surface-title">Recent Ingestion Jobs</div>
              <div className="table-surface-subtitle">Automated batch harmonization jobs</div>
            </div>
            <span className="badge badge-success" style={{ fontSize: '11px' }}>Automated Pipeline</span>
          </div>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>CPSE</th>
                  <th>Material Code</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recent_processing_jobs && recent_processing_jobs.length > 0 ? (
                  recent_processing_jobs.slice(0, 6).map((job) => (
                    <tr key={job.id}>
                      <td><span className="code-id">{job.id}</span></td>
                      <td><span className="cpse-badge">{job.cpse}</span></td>
                      <td>{job.material_code}</td>
                      <td><span className="badge badge-success">{job.status}</span></td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                      No processing jobs active.
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
