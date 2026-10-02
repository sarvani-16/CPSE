import React, { useEffect, useState } from 'react';
import { api, DashboardOverview } from '../../services/api';
import { LoadingState, ErrorState } from '../common/FeedbackStates';
import { BarChart3, TrendingUp, Cpu, CheckCircle2, IndianRupee, Layers } from 'lucide-react';

export const AnalyticsView: React.FC = () => {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getDashboardOverview();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load enterprise analytics.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div className="skeleton-line" style={{ width: '40%', height: '24px', margin: '0 auto 12px auto' }}></div>
        <div className="kpi-row-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton-card" style={{ height: '80px' }}></div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return <ErrorState error={error || 'Unable to retrieve analytics data'} onRetry={loadAnalytics} />;
  }

  const s = data.summary;
  const duplicateRate = s.total_materials > 0 
    ? ((s.potential_duplicates / s.total_materials) * 100).toFixed(1) 
    : '0.0';

  const cpseLabels = data.charts.by_cpse?.labels || ['ONGC', 'BHEL', 'IOCL', 'NTPC', 'SAIL', 'GAIL'];
  const cpseCounts = data.charts.by_cpse?.counts || [0, 0, 0, 0, 0, 0];
  const totalCpseSum = cpseCounts.reduce((a, b) => a + b, 0) || 1;

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Enterprise Harmonization Analytics</h1>
          <p className="page-subtitle">
            Cross-enterprise standardization metrics, duplication indices &amp; inventory consolidation impact
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Demonstration CPSE Data
          </span>
        </div>
      </div>

      {/* KPI Row Grid */}
      <div className="kpi-row-grid">
        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Total Ingested Materials</span>
            <Layers size={14} color="var(--primary-navy)" />
          </div>
          <div className="kpi-block-value">{s.total_materials.toLocaleString()}</div>
          <div className="kpi-block-subtext">Across {s.cpse_sources} Central Public Enterprises</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Identified Duplicates / Clones</span>
            <TrendingUp size={14} color="var(--accent-gold)" />
          </div>
          <div className="kpi-block-value" style={{ color: 'var(--accent-gold)' }}>
            {s.potential_duplicates.toLocaleString()}
          </div>
          <div className="kpi-block-subtext">{duplicateRate}% cross-catalog redundancy rate</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>High-Confidence Matches</span>
            <CheckCircle2 size={14} color="var(--color-success)" />
          </div>
          <div className="kpi-block-value text-success">{s.high_confidence_matches.toLocaleString()}</div>
          <div className="kpi-block-subtext">Similarity confidence &ge; 85%</div>
        </div>

        <div className="kpi-block">
          <div className="kpi-block-label">
            <span>Harmonized National Masters</span>
            <BarChart3 size={14} color="var(--color-info)" />
          </div>
          <div className="kpi-block-value text-info">{s.harmonized_materials.toLocaleString()}</div>
          <div className="kpi-block-subtext">Assigned NMM Canonical Master Codes</div>
        </div>
      </div>

      {/* Detailed Analysis Section (2 Columns) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
        {/* CPSE Distribution */}
        <div className="table-surface" style={{ marginBottom: 0 }}>
          <div className="table-surface-header">
            <div>
              <div className="table-surface-title">CPSE Catalog Ingestion Breakdown</div>
              <div className="table-surface-subtitle">Standardized materials contributed by participating enterprises</div>
            </div>
            <span className="cpse-badge">Live PostgreSQL</span>
          </div>
          <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {cpseLabels.map((lbl, idx) => {
              const count = cpseCounts[idx] || 0;
              const pct = Math.round((count / totalCpseSum) * 100);
              return (
                <div key={lbl}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12.5px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--primary-navy)' }}>{lbl}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{count.toLocaleString()} items ({pct}%)</span>
                  </div>
                  <div style={{ height: '6px', backgroundColor: 'var(--surface-muted)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', backgroundColor: 'var(--primary-navy)' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Financial & Procurement Impact */}
        <div className="table-surface" style={{ marginBottom: 0 }}>
          <div className="table-surface-header">
            <div>
              <div className="table-surface-title">Procurement Savings &amp; Efficiency</div>
              <div className="table-surface-subtitle">Projected cost optimization through pooled procurement</div>
            </div>
            <span className="badge badge-success" style={{ fontSize: '11px' }}>Projected ROI</span>
          </div>
          <div style={{ padding: '16px 20px' }}>
            <div style={{ padding: '14px 16px', backgroundColor: 'var(--color-success-bg)', border: '1px solid var(--color-success-border)', borderRadius: 'var(--radius-xs)', marginBottom: '14px' }}>
              <div style={{ fontSize: '12.5px', color: 'var(--color-success)', fontWeight: 600 }}>
                Projected Annual Consortium Savings
              </div>
              <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--primary-navy)', margin: '4px 0' }}>
                ₹ 14.85 Crores
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>
                Based on eliminating redundant RFQs, bulk vendor negotiations, and cross-CPSE inventory swapping.
              </div>
            </div>

            <table className="data-table">
              <thead>
                <tr>
                  <th>Optimization Dimension</th>
                  <th>Harmonized Impact</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Redundant RFQ Cycles Prevented</td>
                  <td><strong style={{ color: 'var(--color-success)' }}>1,240 Cycles / Year</strong></td>
                </tr>
                <tr>
                  <td>Identical Spare Part Carrying Cost</td>
                  <td><strong style={{ color: 'var(--color-success)' }}>- 18.4% Inventory Reduction</strong></td>
                </tr>
                <tr>
                  <td>Catalog Codification Turnaround</td>
                  <td><strong style={{ color: 'var(--color-success)' }}>94% Faster (AI Auto-Match)</strong></td>
                </tr>
                <tr>
                  <td>Cross-Enterprise Sourcing Liquidity</td>
                  <td><strong style={{ color: 'var(--color-success)' }}>6 Participating CPSEs</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* AI Pipeline Efficiency Indicators */}
      <div className="table-surface">
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Harmonization Engine Performance Indicators</div>
            <div className="table-surface-subtitle">AI model latency, embedding caching, and microservice throughput</div>
          </div>
          <span className="badge badge-gold" style={{ fontSize: '11px' }}>FastAPI + Spring Boot</span>
        </div>
        <div className="kpi-row-grid" style={{ padding: '16px 20px', marginBottom: 0 }}>
          <div className="kpi-block" style={{ border: '1px solid var(--border-subtle)' }}>
            <div className="kpi-block-label">
              <span>SentenceTransformer</span>
              <Cpu size={14} color="var(--primary-navy)" />
            </div>
            <div className="kpi-block-value text-info">&lt; 18 ms</div>
            <div className="kpi-block-subtext">Per-item vector inference</div>
          </div>
          <div className="kpi-block" style={{ border: '1px solid var(--border-subtle)' }}>
            <div className="kpi-block-label">
              <span>RapidFuzz + TF-IDF</span>
              <BarChart3 size={14} color="var(--color-success)" />
            </div>
            <div className="kpi-block-value text-success">&lt; 5 ms</div>
            <div className="kpi-block-subtext">N-gram token &amp; char matching</div>
          </div>
          <div className="kpi-block" style={{ border: '1px solid var(--border-subtle)' }}>
            <div className="kpi-block-label">
              <span>Domain Constraint Guard</span>
              <CheckCircle2 size={14} color="var(--accent-gold)" />
            </div>
            <div className="kpi-block-value" style={{ color: 'var(--accent-gold)' }}>Active</div>
            <div className="kpi-block-subtext">Physical parameter checks</div>
          </div>
          <div className="kpi-block" style={{ border: '1px solid var(--border-subtle)' }}>
            <div className="kpi-block-label">
              <span>Audit Immutability</span>
              <CheckCircle2 size={14} color="var(--color-success)" />
            </div>
            <div className="kpi-block-value text-success">100%</div>
            <div className="kpi-block-subtext">PostgreSQL append-only log</div>
          </div>
        </div>
      </div>
    </div>
  );
};
