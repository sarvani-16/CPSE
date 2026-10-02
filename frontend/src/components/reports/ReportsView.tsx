import React, { useState } from 'react';
import { api } from '../../services/api';
import { FileText, Download, Filter, Calendar, Building2, CheckCircle2, Clock, ShieldCheck, Database } from 'lucide-react';

interface ReportTemplate {
  id: string;
  title: string;
  category: string;
  description: string;
  format: 'CSV' | 'JSON' | 'CSV & JSON';
  frequency: string;
  actionFilter?: string;
}

export const ReportsView: React.FC = () => {
  const [selectedCpse, setSelectedCpse] = useState('ALL');
  const [dateRange, setDateRange] = useState('ALL');
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportSuccess, setExportSuccess] = useState<string | null>(null);

  const reportTemplates: ReportTemplate[] = [
    {
      id: 'harmonization-master',
      title: 'Material Harmonization Master Report',
      category: 'Harmonization Master',
      description: 'Complete register of source materials mapped to National Material Master (NMM) canonical codes with confidence ratings and classification hierarchy.',
      format: 'CSV',
      frequency: 'Real-Time Dynamic',
      actionFilter: 'APPROVE_MATCH',
    },
    {
      id: 'duplicate-analysis',
      title: 'Cross-CPSE Duplicate Identification Report',
      category: 'Deduplication',
      description: 'Comprehensive inventory of identical, near-duplicate, and functionally equivalent parts identified across participating CPSE organizations.',
      format: 'CSV',
      frequency: 'Batch Ingestion Cycle',
      actionFilter: 'FLAG_DUPLICATE',
    },
    {
      id: 'review-audit-trail',
      title: 'Human-in-the-Loop Review Audit Trail',
      category: 'Governance & Compliance',
      description: 'Cryptographically timestamped log of reviewer decisions, manual overrides, batch approvals, and compliance justification notes.',
      format: 'CSV',
      frequency: 'Immutable Continuous Log',
      actionFilter: '',
    },
    {
      id: 'cpse-summary',
      title: 'CPSE Inventory & Equivalence Breakdown',
      category: 'Enterprise Analytics',
      description: 'Comparative matrix of catalog volumes, cross-referencing density, standardization progress, and active mappings per CPSE tenant.',
      format: 'CSV',
      frequency: 'Daily Aggregation',
      actionFilter: 'INGEST_CATALOG',
    },
    {
      id: 'ai-telemetry',
      title: 'AI Microservice Inference & Topology Report',
      category: 'System Performance',
      description: 'Latency metrics, embedding vector calculations, confidence threshold distributions, and model guardrail triggering frequencies.',
      format: 'JSON',
      frequency: 'Real-Time Telemetry',
      actionFilter: '',
    },
  ];

  const handleExport = async (report: ReportTemplate) => {
    setDownloadingId(report.id);
    setExportError(null);
    setExportSuccess(null);
    try {
      if (report.format === 'JSON') {
        const data = await api.getModelStatus();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sih26099-ai-telemetry-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        setExportSuccess(`Downloaded ${report.title} telemetry.`);
      } else {
        await api.exportReport(report.id, {
          cpse: selectedCpse,
          date: dateRange,
          action: report.actionFilter || undefined,
        });
        setExportSuccess(`Successfully downloaded ${report.title}.`);
      }
    } catch (err: any) {
      console.error('Report export failure:', err);
      setExportError(err.message || 'Unable to generate CSV report.');
    } finally {
      setDownloadingId(null);
    }
  };

  const sampleRecentExports = [
    { name: 'NMM_Master_Harmonization_2026.csv', size: '2.4 MB', records: '2,840 rows', date: 'Today, 10:45 AM', user: 'ADM001 (Admin)', status: 'Generated' },
    { name: 'Audit_Log_Full_Export_Q1.csv', size: '890 KB', records: '1,120 rows', date: 'Yesterday, 04:12 PM', user: 'REV001 (Auditor)', status: 'Generated' },
    { name: 'Duplicate_Candidates_CrossCPSE.csv', size: '1.1 MB', records: '640 pairs', date: '28 Sep 2026', user: 'USR001 (ONGC)', status: 'Generated' },
  ];

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Reports &amp; Data Export</h1>
          <p className="page-subtitle">
            Generate and export official compliance reports, harmonization summaries, duplicate analyses, and audit records
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Production Audit Pipeline
          </span>
        </div>
      </div>

      {/* Export Notifications */}
      {exportError && (
        <div className="alert alert-danger" style={{ marginBottom: '16px' }}>
          <span>⛔</span>
          <div>
            <strong>Export Error:</strong> {exportError}
          </div>
        </div>
      )}

      {exportSuccess && (
        <div className="alert alert-success" style={{ marginBottom: '16px' }}>
          <span>✓</span>
          <div>{exportSuccess}</div>
        </div>
      )}

      {/* Filter Surface */}
      <div className="table-surface" style={{ padding: '14px 20px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: 600, color: 'var(--primary-navy)' }}>
            <Filter size={15} />
            <span>Report Scope Filters:</span>
          </div>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Building2 size={14} color="var(--text-secondary)" />
              <select
                className="form-input"
                value={selectedCpse}
                onChange={(e) => setSelectedCpse(e.target.value)}
                style={{ padding: '6px 10px', fontSize: '12.5px', width: 'auto' }}
              >
                <option value="ALL">All Participating CPSEs</option>
                <option value="ONGC">ONGC - Oil &amp; Natural Gas</option>
                <option value="BHEL">BHEL - Heavy Electricals</option>
                <option value="IOCL">IOCL - Indian Oil Corp</option>
                <option value="NTPC">NTPC - Power Generation</option>
                <option value="SAIL">SAIL - Steel Authority</option>
                <option value="GAIL">GAIL - Gas Authority</option>
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Calendar size={14} color="var(--text-secondary)" />
              <select
                className="form-input"
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                style={{ padding: '6px 10px', fontSize: '12.5px', width: 'auto' }}
              >
                <option value="ALL">All Recorded History</option>
                <option value="TODAY">Today Only</option>
                <option value="7DAYS">Last 7 Days</option>
                <option value="30DAYS">Last 30 Days</option>
                <option value="QUARTER">Current Quarter</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Available Report Templates Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {reportTemplates.map((report) => (
          <div
            key={report.id}
            style={{
              backgroundColor: 'var(--surface-white)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              padding: '18px 20px',
              boxShadow: 'var(--shadow-xs)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="cpse-badge" style={{ fontSize: '10.5px' }}>{report.category}</span>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)' }}>
                  Format: {report.format}
                </span>
              </div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--primary-navy)', marginBottom: '8px', lineHeight: 1.3 }}>
                {report.title}
              </h3>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '14px' }}>
                {report.description}
              </p>
            </div>

            <div style={{ paddingTop: '12px', borderTop: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Clock size={12} />
                <span>{report.frequency}</span>
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                disabled={downloadingId === report.id}
                onClick={() => handleExport(report)}
                style={{ borderColor: 'var(--primary-navy)', color: 'var(--primary-navy)' }}
              >
                <Download size={13} />
                <span>{downloadingId === report.id ? 'Generating...' : `Export ${report.format}`}</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Export Dispatches Table */}
      <div className="table-surface">
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Recent Export Dispatches</div>
            <div className="table-surface-subtitle">Audit-traceable report files generated by authenticated users</div>
          </div>
          <span className="badge badge-outline" style={{ fontSize: '11px' }}>Tamper-Evident</span>
        </div>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Report File</th>
                <th>File Size</th>
                <th>Volume</th>
                <th>Generated By</th>
                <th>Timestamp</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Download</th>
              </tr>
            </thead>
            <tbody>
              {sampleRecentExports.map((exp, idx) => (
                <tr key={idx}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FileText size={16} color="var(--primary-navy)" />
                      <strong style={{ fontSize: '13px' }}>{exp.name}</strong>
                    </div>
                  </td>
                  <td>{exp.size}</td>
                  <td>{exp.records}</td>
                  <td style={{ fontWeight: 500 }}>{exp.user}</td>
                  <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{exp.date}</td>
                  <td>
                    <span className="badge badge-success">{exp.status}</span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      type="button"
                      className="btn-icon-sm"
                      title="Download file"
                      onClick={async () => {
                        try {
                          setExportError(null);
                          if (exp.name.toLowerCase().includes('harmonization')) {
                            await api.exportReport('harmonization-master');
                          } else if (exp.name.toLowerCase().includes('duplicate')) {
                            await api.exportReport('duplicate-analysis');
                          } else {
                            await api.exportAuditLogsCsv();
                          }
                          setExportSuccess(`Downloaded ${exp.name}`);
                        } catch (err: any) {
                          setExportError(err.message || 'Unable to download file.');
                        }
                      }}
                    >
                      <Download size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
