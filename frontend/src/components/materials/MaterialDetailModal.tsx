import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { StatusBadge } from '../common/StatusBadge';
import { LoadingState, ErrorState } from '../common/FeedbackStates';

interface MaterialDetailModalProps {
  materialId: number;
  onClose: () => void;
}

export const MaterialDetailModal: React.FC<MaterialDetailModalProps> = ({ materialId, onClose }) => {
  const [detail, setDetail] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.getMaterialDetail(materialId);
        setDetail(res);
      } catch (err: any) {
        setError(err.message || 'Failed to retrieve material details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [materialId]);

  return (
    <div className="modal-overlay">
      <div className="modal-dialog" style={{ maxWidth: '680px' }}>
        <div className="modal-header">
          <div>
            <h3 className="modal-title">Material Record &amp; Specification Traceability</h3>
            <span className="code-id">Record ID #{materialId}</span>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        {loading && <LoadingState message="Querying PostgreSQL specification records..." />}
        {error && <ErrorState error={error} />}

        {!loading && detail && (
          <div className="modal-body">
            {/* Section 1: Original CPSE Material Information */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--primary-navy)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '6px', marginBottom: '10px' }}>
                1. Original CPSE Material Information
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', fontSize: '12.5px' }}>
                <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Material Code:</div>
                  <strong className="code-id">{detail.material_code}</strong>
                </div>
                <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Originating CPSE:</div>
                  <span className="cpse-badge">{detail.cpse_name}</span>
                </div>
                <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>UOM:</div>
                  <code>{detail.unit_of_measure || 'EA'}</code>
                </div>
              </div>
              <div style={{ marginTop: '10px', fontSize: '12.5px' }}>
                <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Original Description:</div>
                <div style={{ padding: '8px 10px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', marginTop: '3px' }}>
                  {detail.description}
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '10px', fontSize: '12.5px' }}>
                <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Technical Specification:</div>
                  <div>{detail.specification || 'None specified'}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Material Grade:</div>
                  <div>{detail.material_grade || 'Commercial Grade'}</div>
                </div>
              </div>
            </div>

            {/* Section 2: AI / Normalized Information */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--primary-navy)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '6px', marginBottom: '10px' }}>
                2. AI-Normalized Industrial Extraction
              </h4>
              <div style={{ fontSize: '12.5px', marginBottom: '8px' }}>
                <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Normalized Representation:</div>
                <code style={{ fontSize: '12px' }}>{detail.normalized_info?.normalized_description || detail.description.toUpperCase()}</code>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', fontSize: '12.5px' }}>
                <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Extracted Grade:</div>
                  <span>{detail.normalized_info?.extracted_attributes?.grade || detail.material_grade || 'Standard'}</span>
                </div>
                <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Extracted Dimensions:</div>
                  <span>{detail.normalized_info?.extracted_attributes?.dimensions || detail.dimensions || 'Standard'}</span>
                </div>
                <div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Category:</div>
                  <span>{detail.category || 'General Industrial Supplies'}</span>
                </div>
              </div>
            </div>

            {/* Section 3: Traceability Flow */}
            <div style={{ marginBottom: '16px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--primary-navy)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '6px', marginBottom: '10px' }}>
                3. End-to-End Codification Traceability
              </h4>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', flexWrap: 'wrap' }}>
                <div style={{ padding: '6px 10px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>ORIGIN CPSE</div>
                  <strong>{detail.cpse_name} • {detail.material_code}</strong>
                </div>
                <span>&rarr;</span>
                <div style={{ padding: '6px 10px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>NORMALIZATION</div>
                  <strong>{detail.category || 'Commodity Group'}</strong>
                </div>
                <span>&rarr;</span>
                <div style={{ padding: '6px 10px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>AI MATCHING</div>
                  <strong>FastAPI Microservice (8001)</strong>
                </div>
                <span>&rarr;</span>
                <div style={{ padding: '6px 10px', backgroundColor: 'var(--color-info-bg)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--color-info-border)' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-info)' }}>NATIONAL MASTER</div>
                  <strong style={{ color: 'var(--primary-navy)' }}>{detail.canonical_code || 'NMM-000001 (Candidate)'}</strong>
                </div>
              </div>
            </div>

            <div className="modal-footer" style={{ padding: '12px 0 0 0', display: 'flex', justifyContent: 'flex-end' }}>
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Close Details
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
