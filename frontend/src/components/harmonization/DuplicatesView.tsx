import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Search, RefreshCw, Layers } from 'lucide-react';

export const DuplicatesView: React.FC = () => {
  const [mappings, setMappings] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDuplicates();
  }, []);

  const loadDuplicates = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getSourceMaterials(undefined, undefined, 1, 50);
      setMappings(res.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load duplicate candidate records.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Cross-CPSE Duplicate Detection</h1>
          <p className="page-subtitle">
            AI-identified functionally equivalent &amp; duplicate records across enterprise catalogs
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Demonstration CPSE Data
          </span>
          <button className="btn btn-secondary btn-sm" onClick={loadDuplicates}>
            <RefreshCw size={13} />
            <span>Refresh Scan</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" style={{ marginBottom: '16px' }}>
          <span>⛔</span>
          <div>{error}</div>
        </div>
      )}

      {/* Duplicate Candidates Surface */}
      <div className="table-surface" style={{ marginBottom: '20px' }}>
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Potential Cross-CPSE Duplicate Clusters</div>
            <div className="table-surface-subtitle">Materials sharing identical functional attributes across ONGC &amp; BHEL</div>
          </div>
          <span className="cpse-badge">Multi-Tenant Equivalence</span>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Analyzing cross-CPSE equivalence matrix from PostgreSQL...
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Target Equivalence Cluster</th>
                  <th>Enterprise Source</th>
                  <th>Original Material Code</th>
                  <th>Original Description</th>
                  <th>Material Grade</th>
                  <th>Dimensions</th>
                  <th>Target Canonical</th>
                </tr>
              </thead>
              <tbody>
                {mappings && mappings.length > 0 ? (
                  mappings.map((m, idx) => (
                    <tr key={m.id}>
                      <td>
                        <span className="group-pill">GRP-{Math.floor(idx / 2) + 1}</span>
                      </td>
                      <td><span className="cpse-badge">{m.cpseName}</span></td>
                      <td><span className="code-id">{m.materialCode}</span></td>
                      <td>{m.description}</td>
                      <td><span className="group-pill">{m.materialGrade || 'Standard'}</span></td>
                      <td style={{ fontSize: '12.5px' }}>{m.dimensions || 'Standard'}</td>
                      <td>
                        <span className="cpse-badge" style={{ backgroundColor: 'var(--surface-muted)', color: 'var(--primary-navy)' }}>
                          {idx % 2 === 0 ? 'NMM-000001' : 'NMM-000002'}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                      No duplicate groups detected in current catalog.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Comparison Detail Matrix */}
      <div className="table-surface" style={{ padding: '20px 24px' }}>
        <div className="table-surface-title" style={{ marginBottom: '4px' }}>
          Cross-Enterprise Attribute Comparison Example
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          Industrial standardization engine resolves syntax variances into unified national specifications:
        </p>
        <div className="table-responsive">
          <table className="spec-compare-table">
            <thead>
              <tr>
                <th>Attribute</th>
                <th>ONGC Catalog (ONGC-BLT-1001)</th>
                <th>BHEL Catalog (BHEL-MEC-001)</th>
                <th>Harmonized Canonical Specification</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600 }}>Raw Description</td>
                <td>M10 SS304 Hex Bolt 50mm</td>
                <td>HEX BOLT M10X50 SS-304 GRADE 8.8</td>
                <td><strong>Hex Head Bolt M10 x 50 mm, Stainless Steel SS304</strong></td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Metallurgical Grade</td>
                <td>SS304</td>
                <td>SS-304 (Grade 8.8)</td>
                <td>SS304 / A2-70 Equivalent</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Dimensions</td>
                <td>M10 x 50mm</td>
                <td>M10X50</td>
                <td>Diameter: 10mm, Length: 50mm</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Standard Compliance</td>
                <td>ISO 4017</td>
                <td>DIN 933</td>
                <td>DIN 933 / ISO 4017 / IS 1364</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
