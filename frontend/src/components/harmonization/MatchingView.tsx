import React, { useState } from 'react';
import { api, CompareResponse } from '../../services/api';
import { GitCompare, Sparkles, AlertTriangle, CheckCircle2, XCircle, ArrowRight, Layers, Cpu } from 'lucide-react';

export const MatchingView: React.FC = () => {
  const [titleA, setTitleA] = useState('Hex Bolt M10 x 50 SS304');
  const [titleB, setTitleB] = useState('Stainless Steel Hex Bolt M10 50mm SS304');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!titleA.trim() || !titleB.trim()) {
      setError('Please provide descriptions for both materials.');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const res = await api.compareMaterials({ title_a: titleA, title_b: titleB });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Comparison request failed');
    } finally {
      setLoading(false);
    }
  };

  const loadCase = (a: string, b: string) => {
    setTitleA(a);
    setTitleB(b);
    setResult(null);
    setError(null);
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">AI Matching Engine</h1>
          <p className="page-subtitle">
            Hybrid multi-modal material comparison, lexical alignment &amp; engineering conflict guardrails
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Production AI Pipeline (Port 8001)
          </span>
        </div>
      </div>

      {/* Input Formulation Surface */}
      <div className="table-surface" style={{ padding: '20px 24px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <div className="table-surface-title">Pairwise Material Evaluation</div>
            <div className="table-surface-subtitle">
              Input two CPSE material titles or select an evaluation preset
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => loadCase('Hex Bolt M10 x 50 SS304', 'Stainless Steel Hex Bolt M10 50mm SS304')}
            >
              Case 1: Standard Variation
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => loadCase('Hex Bolt M10 x 50 SS304', 'Hex Bolt M10 x 50 SS316')}
            >
              Case 2: Metallurgy Conflict
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => loadCase('Hex Bolt M10 x 50 SS304', 'Centrifugal Water Pump 5HP')}
            >
              Case 3: Unrelated Material
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
          <div className="form-group">
            <label className="form-label">Material Description A (Source CPSE Item)</label>
            <textarea
              className="form-input"
              rows={3}
              value={titleA}
              onChange={(e) => setTitleA(e.target.value)}
              placeholder="e.g. Hex Head Bolt M10 x 50mm SS304 Full Thread Grade 8.8"
              style={{ resize: 'vertical' }}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Material Description B (Candidate / Peer Item)</label>
            <textarea
              className="form-input"
              rows={3}
              value={titleB}
              onChange={(e) => setTitleB(e.target.value)}
              placeholder="e.g. Stainless Steel Hex Bolt M10 50mm SS304"
              style={{ resize: 'vertical' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <button
            type="button"
            onClick={handleCompare}
            disabled={loading}
            className="btn btn-primary"
          >
            <Sparkles size={15} />
            <span>{loading ? 'Evaluating via ML Microservice...' : 'Execute AI Comparison'}</span>
          </button>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Pipeline executes SentenceTransformer embeddings + RapidFuzz + TF-IDF n-grams
          </span>
        </div>

        {error && (
          <div className="alert alert-danger" style={{ marginTop: '16px' }}>
            <span>⛔</span>
            <div>{error}</div>
          </div>
        )}
      </div>

      {/* Results Surface */}
      {result && (
        <div className="table-surface" style={{ padding: '20px 24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <div className="table-surface-title">AI Decision &amp; Analytical Breakdown</div>
              <div className="table-surface-subtitle">Multi-model similarity vectors and domain validation result</div>
            </div>
            <span
              className={`badge ${
                result.match_decision === 'MATCH'
                  ? 'badge-success'
                  : result.match_decision === 'REVIEW'
                  ? 'badge-warn'
                  : 'badge-danger'
              }`}
              style={{ fontSize: '13px', padding: '6px 14px' }}
            >
              DECISION: {result.match_decision}
            </span>
          </div>

          {/* 4 Score Metrics */}
          <div className="kpi-row-grid" style={{ marginBottom: '20px' }}>
            <div className="kpi-block">
              <div className="kpi-block-label">
                <span>Hybrid Ensemble</span>
                <Cpu size={14} color="var(--primary-navy)" />
              </div>
              <div className="kpi-block-value" style={{ color: result.hybrid_score >= 0.85 ? 'var(--color-success)' : 'var(--accent-gold)' }}>
                {(result.hybrid_score * 100).toFixed(1)}%
              </div>
              <div className="kpi-block-subtext">Composite weighted score</div>
            </div>

            <div className="kpi-block">
              <div className="kpi-block-label">
                <span>Semantic Score</span>
                <Sparkles size={14} color="var(--color-info)" />
              </div>
              <div className="kpi-block-value text-info">
                {(result.semantic_score * 100).toFixed(1)}%
              </div>
              <div className="kpi-block-subtext">SentenceTransformer MiniLM</div>
            </div>

            <div className="kpi-block">
              <div className="kpi-block-label">
                <span>Lexical Score</span>
                <Layers size={14} color="var(--primary-navy)" />
              </div>
              <div className="kpi-block-value">
                {(result.lexical_score * 100).toFixed(1)}%
              </div>
              <div className="kpi-block-subtext">TF-IDF Word + Char N-grams</div>
            </div>

            <div className="kpi-block">
              <div className="kpi-block-label">
                <span>Fuzzy Alignment</span>
                <GitCompare size={14} color="var(--text-secondary)" />
              </div>
              <div className="kpi-block-value">
                {(result.fuzzy_score * 100).toFixed(1)}%
              </div>
              <div className="kpi-block-subtext">RapidFuzz token ratio</div>
            </div>
          </div>

          {/* Technical Conflict Panel */}
          {result.technical_tokens?.conflicts && result.technical_tokens.conflicts.length > 0 && (
            <div className="technical-conflict-panel">
              <div className="conflict-header-row">
                <AlertTriangle size={18} />
                <span>Technical Domain Conflict Triggered</span>
              </div>
              <div className="conflict-reason">
                Conflicting physical/metallurgical attributes detected: <strong>{result.technical_tokens.conflicts.join(', ')}</strong>.
              </div>
              <p style={{ fontSize: '12px', color: '#7A4E0E', margin: '6px 0 0 0' }}>
                To prevent critical procurement and assembly failure, automatic MATCH has been overridden to REVIEW for mandatory human verification.
              </p>
            </div>
          )}

          {/* Evidence-Based Explanations */}
          <div style={{ marginTop: '16px', padding: '16px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '13.5px', fontWeight: 700, color: 'var(--primary-navy)', marginBottom: '10px' }}>
              Why this match was suggested:
            </div>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {result.explanation.map((exp, idx) => (
                <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '13px', color: 'var(--text-primary)' }}>
                  <CheckCircle2 size={16} color="var(--color-success)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{exp}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
