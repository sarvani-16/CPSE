import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { StatusBadge } from '../common/StatusBadge';
import { LoadingState, ErrorState } from '../common/FeedbackStates';
import { Database, RefreshCw } from 'lucide-react';

export const DataManagementView: React.FC = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getRecentJobs();
      setJobs(res || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load data ingestion jobs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Data Ingestion &amp; Pipeline Management</h1>
          <p className="page-subtitle">
            Catalog processing throughput, schema mapping &amp; batch execution history (ADMIN ONLY)
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Enterprise Ingestion Queue
          </span>
          <button className="btn btn-secondary btn-sm" onClick={loadJobs}>
            <RefreshCw size={13} />
            <span>Refresh Jobs</span>
          </button>
        </div>
      </div>

      <div className="table-surface">
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Catalog Upload &amp; Batch Ingestion Executions</div>
            <div className="table-surface-subtitle">Throughput records across participating enterprise nodes</div>
          </div>
          <span className="cpse-badge">Automated Pipeline</span>
        </div>

        {loading && <LoadingState message="Querying batch pipeline executions..." />}
        {error && <ErrorState error={error} onRetry={loadJobs} />}

        {!loading && (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Originating CPSE</th>
                  <th>Catalog File</th>
                  <th>Total Rows</th>
                  <th>Processed Rows</th>
                  <th>Status</th>
                  <th>Initiated At</th>
                </tr>
              </thead>
              <tbody>
                {jobs && jobs.length > 0 ? (
                  jobs.map((job) => (
                    <tr key={job.job_id}>
                      <td><span className="code-id">{job.job_id}</span></td>
                      <td><span className="cpse-badge">{job.cpse_name}</span></td>
                      <td>{job.file_name || `${job.cpse_name?.toLowerCase()}_catalog.csv`}</td>
                      <td>{job.rows_total}</td>
                      <td>{job.rows_processed}</td>
                      <td><StatusBadge status={job.status || 'COMPLETED'} /></td>
                      <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {job.created_at ? new Date(job.created_at).toLocaleString() : 'Recent'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                      No ingestion jobs recorded in PostgreSQL.
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
