import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { LoadingState, ErrorState } from '../common/FeedbackStates';
import { Cpu, RefreshCw, CheckCircle2, ShieldCheck, Activity, Layers } from 'lucide-react';

export const ModelStatusView: React.FC = () => {
  const [status, setStatus] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadModelStatus();
  }, []);

  const loadModelStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getModelStatus();
      setStatus(res);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to AI Model service.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">AI/ML Microservice Status &amp; Telemetry</h1>
          <p className="page-subtitle">
            Model parameters, domain guardrails &amp; hybrid ensemble weights (ADMIN ONLY)
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            FastAPI Microservice (Port 8001)
          </span>
          <button className="btn btn-secondary btn-sm" onClick={loadModelStatus}>
            <RefreshCw size={13} />
            <span>Poll Engine</span>
          </button>
        </div>
      </div>

      {loading && <LoadingState message="Connecting to AI/ML service gateway..." />}
      {error && <ErrorState error={error} onRetry={loadModelStatus} />}

      {!loading && status && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
          {/* Microservice Connectivity */}
          <div className="table-surface" style={{ padding: '20px 24px', marginBottom: 0 }}>
            <div className="table-surface-title" style={{ marginBottom: '12px' }}>
              Microservice Connectivity
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Status:</span>
                <span className="badge badge-success">✓ {status.ml_service_status}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Endpoint:</span>
                <code style={{ fontSize: '12px' }}>{status.ml_endpoint}</code>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Last Telemetry Check:</span>
                <span style={{ fontSize: '12px', color: 'var(--text-primary)' }}>
                  {new Date(status.last_health_check).toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          {/* Model Weights */}
          <div className="table-surface" style={{ padding: '20px 24px', marginBottom: 0 }}>
            <div className="table-surface-title" style={{ marginBottom: '12px' }}>
              Embedding &amp; Architecture
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Dense Transformer:</span>
                <span className="code-id">{status.embedding_model}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Duplicate Detection Mode:</span>
                <span className="badge badge-outline">{status.duplicate_detection_mode}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Vector Normalization:</span>
                <span style={{ color: 'var(--color-success)', fontWeight: 600 }}>L2 Unit-Norm Active</span>
              </div>
            </div>
          </div>

          {/* Ensemble Weights */}
          <div className="table-surface" style={{ padding: '20px 24px', gridColumn: '1 / -1', marginBottom: 0 }}>
            <div className="table-surface-title" style={{ marginBottom: '4px' }}>
              Ensemble Scoring Weights
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
              Mathematical composition weights determining candidate match rankings
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
              {Object.entries(status.hybrid_scoring_weights || {}).map(([key, val]) => (
                <div
                  key={key}
                  style={{
                    backgroundColor: 'var(--surface-subtle)',
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                >
                  <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', letterSpacing: '0.5px' }}>
                    {key.toUpperCase()}
                  </span>
                  <span style={{ fontSize: '20px', fontWeight: 700, color: 'var(--primary-navy)', marginTop: '4px' }}>
                    {Math.round(Number(val) * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Technical Conflict Rules */}
          <div className="table-surface" style={{ padding: '20px 24px', gridColumn: '1 / -1', marginBottom: 0 }}>
            <div className="table-surface-title" style={{ marginBottom: '4px' }}>
              Domain Conflict Demotion Guardrails
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
              Deterministic engineering constraints preventing dangerous procurement errors
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
              {Object.entries(status.technical_conflict_guardrails || {}).map(([rule, desc]) => (
                <div
                  key={rule}
                  style={{
                    padding: '12px 14px',
                    backgroundColor: 'var(--surface-subtle)',
                    borderRadius: 'var(--radius-xs)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <strong style={{ fontSize: '12.5px', color: 'var(--primary-navy)' }}>
                    {rule.replace('_', ' ').toUpperCase()}:
                  </strong>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>
                    {String(desc)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
