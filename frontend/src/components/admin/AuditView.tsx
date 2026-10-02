import React, { useEffect, useState } from 'react';
import { api, AuditLogItem } from '../../services/api';
import { History, Download, Filter, RefreshCw } from 'lucide-react';

export const AuditView: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [actionFilter, setActionFilter] = useState('');
  const [userFilter, setUserFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  useEffect(() => {
    loadLogs();
  }, [actionFilter, userFilter, dateFilter]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const res = await api.getAuditLogs({
        action: actionFilter || undefined,
        user: userFilter || undefined,
        date: dateFilter || undefined,
        page: 1,
        pageSize: 50,
      });
      setLogs(res.items || []);
      setTotal(res.total || 0);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    setExportError(null);
    try {
      await api.exportAuditLogsCsv(actionFilter, dateFilter);
    } catch (err: any) {
      console.error('Audit export failure:', err);
      setExportError(err.message || 'Unable to generate audit log CSV report.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Enterprise Governance &amp; Audit Trail</h1>
          <p className="page-subtitle">
            Immutable chain-of-custody logging of uploads, normalizations, AI recommendations, approvals, and mapping changes
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Tamper-Evident Ledger
          </span>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleExport}
            disabled={isExporting}
          >
            <Download size={14} />
            <span>{isExporting ? 'Exporting...' : 'Export Audit CSV'}</span>
          </button>
        </div>
      </div>

      {exportError && (
        <div className="alert alert-danger" style={{ marginBottom: '16px' }}>
          <span>⛔</span>
          <div>
            <strong>Export Error:</strong> {exportError}
          </div>
        </div>
      )}

      {/* Filter Surface */}
      <div className="table-surface" style={{ padding: '14px 18px', marginBottom: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', alignItems: 'flex-end' }}>
          <div>
            <label className="form-label">Filter Action</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. APPROVE_MATCH"
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
            />
          </div>
          <div>
            <label className="form-label">Filter User</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Govt Reviewer"
              value={userFilter}
              onChange={(e) => setUserFilter(e.target.value)}
            />
          </div>
          <div>
            <label className="form-label">Filter Date (YYYY-MM-DD)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. 2026-10-01"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
            />
          </div>
          <div>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => { setActionFilter(''); setUserFilter(''); setDateFilter(''); }}
              style={{ width: '100%' }}
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>

      {/* Table Surface */}
      <div className="table-surface">
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Audit Ledger Records ({total.toLocaleString()} Entries)</div>
            <div className="table-surface-subtitle">Chronological ledger of system and reviewer actions</div>
          </div>
          <span className="cpse-badge">Cryptographic Integrity</span>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading audit records from PostgreSQL...
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Performed By</th>
                  <th>New Value / Change</th>
                  <th>Audit Reason</th>
                </tr>
              </thead>
              <tbody>
                {logs && logs.length > 0 ? (
                  logs.map((l) => (
                    <tr key={l.id}>
                      <td style={{ whiteSpace: 'nowrap', fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {l.timestamp}
                      </td>
                      <td>
                        <span className="badge badge-outline">{l.action}</span>
                      </td>
                      <td>
                        <span className="code-id">{l.entityType}{l.entityId ? ` #${l.entityId}` : ''}</span>
                      </td>
                      <td style={{ fontWeight: 600 }}>{l.performedBy}</td>
                      <td style={{ maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {l.newValue || l.oldValue || '—'}
                      </td>
                      <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {l.reason || '—'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                      No audit records match the current criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
