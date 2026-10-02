import React, { useState } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { UploadCloud, FileSpreadsheet, CheckCircle2, AlertTriangle, ArrowRight, Layers, Database } from 'lucide-react';

export const UploadView: React.FC = () => {
  const { user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [cpseName, setCpseName] = useState<string>(user?.cpse_name && user.cpse_name !== 'CPSE_CONSORTIUM' ? user.cpse_name : 'ONGC');
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [uploading, setUploading] = useState<boolean>(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const steps = [
    { num: 1, title: 'Select CPSE & File' },
    { num: 2, title: 'Schema Auto-Detection' },
    { num: 3, title: 'Normalization Rules' },
    { num: 4, title: 'AI Matching Pipeline' },
    { num: 5, title: 'Summary & Ingestion' },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
      setCurrentStep(2);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a CSV or XLSX material master catalog file.');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);
    setCurrentStep(4);

    try {
      const resp = await api.uploadMaterials(file, cpseName);
      setResult(resp);
      setCurrentStep(5);
    } catch (err: any) {
      setError(err.message || 'File upload failed. Ensure valid format (.csv, .xlsx).');
      setCurrentStep(1);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Upload Materials Catalog</h1>
          <p className="page-subtitle">
            Enterprise ingestion pipeline • Automated schema harmonization &amp; normalization
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            RFC 4180 Compliant • CSV / XLSX
          </span>
        </div>
      </div>

      {/* 5-Step Ingestion Stepper */}
      <div className="table-surface" style={{ marginBottom: '20px', padding: 0 }}>
        <div className="upload-wizard-steps">
          {steps.map((s) => (
            <div
              key={s.num}
              className={`wizard-step-item ${currentStep === s.num ? 'active' : ''}`}
              style={{ cursor: 'pointer' }}
              onClick={() => {
                if (file || s.num === 1) setCurrentStep(s.num);
              }}
            >
              <div className="wizard-step-num">{s.num}</div>
              <span>{s.title}</span>
            </div>
          ))}
        </div>

        <div style={{ padding: '24px' }}>
          <form onSubmit={handleUpload}>
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(240px, 1fr) 2fr', gap: '20px', marginBottom: '20px' }}>
              <div className="form-group">
                <label className="form-label">Target CPSE Entity</label>
                <select
                  className="form-input"
                  value={cpseName}
                  disabled={user?.role === 'OFFICER' && !!user.cpse_name}
                  onChange={(e) => setCpseName(e.target.value)}
                >
                  <option value="ONGC">ONGC - Oil and Natural Gas Corporation</option>
                  <option value="BHEL">BHEL - Bharat Heavy Electricals Limited</option>
                  <option value="IOCL">IOCL - Indian Oil Corporation Limited</option>
                  <option value="NTPC">NTPC - NTPC Limited</option>
                  <option value="SAIL">SAIL - Steel Authority of India Limited</option>
                  <option value="GAIL">GAIL - GAIL (India) Limited</option>
                </select>
                {user?.role === 'OFFICER' && (
                  <small style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                    Locked to your authenticated CPSE tenant.
                  </small>
                )}
              </div>

              <div>
                <label className="form-label">Catalog File (.csv or .xlsx)</label>
                <label className="dropzone-surface" style={{ display: 'block' }}>
                  <FileSpreadsheet size={32} color="var(--primary-navy)" style={{ margin: '0 auto 8px auto' }} />
                  <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--primary-navy)' }}>
                    {file ? file.name : 'Click to select or drag & drop material catalog file'}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    {file ? `${(file.size / 1024).toFixed(1)} KB • Ready for processing` : 'Accepts CSV or Excel spreadsheet masters'}
                  </div>
                  <input
                    type="file"
                    style={{ display: 'none' }}
                    accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                    onChange={handleFileChange}
                  />
                </label>
              </div>
            </div>

            {error && (
              <div className="alert alert-danger" style={{ marginBottom: '16px' }}>
                <span>⛔</span>
                <div>{error}</div>
              </div>
            )}

            {result && (
              <div className="alert alert-success" style={{ marginBottom: '16px' }}>
                <span>✓</span>
                <div>
                  <strong>Ingestion Complete:</strong> {result.message || 'Catalog materials processed.'}
                  {result.records_ingested && <span> ({result.records_ingested} records stored in master database)</span>}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={uploading || !file}
              >
                <UploadCloud size={15} />
                <span>{uploading ? 'Processing & Normalizing Catalog...' : 'Upload & Initiate Pipeline'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Enterprise Format Specifications */}
      <div className="table-surface" style={{ padding: '20px 24px' }}>
        <div className="table-surface-title" style={{ marginBottom: '6px' }}>
          Enterprise Ingestion Specifications
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          The ingestion engine utilizes Apache Commons CSV &amp; POI to parse industrial material masters.
          Required attributes:
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          <div style={{ padding: '12px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
            <strong style={{ fontSize: '12.5px', color: 'var(--primary-navy)' }}>Material Code:</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>Original CPSE catalog identification number</p>
          </div>
          <div style={{ padding: '12px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
            <strong style={{ fontSize: '12.5px', color: 'var(--primary-navy)' }}>Description:</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>Standard industrial description with grade and dimensions</p>
          </div>
          <div style={{ padding: '12px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
            <strong style={{ fontSize: '12.5px', color: 'var(--primary-navy)' }}>Specification:</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>Manufacturing standard (e.g. DIN 933, ASTM A106, IS 1364)</p>
          </div>
          <div style={{ padding: '12px', backgroundColor: 'var(--surface-subtle)', borderRadius: 'var(--radius-xs)', border: '1px solid var(--border-subtle)' }}>
            <strong style={{ fontSize: '12.5px', color: 'var(--primary-navy)' }}>UOM:</strong>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '4px 0 0 0' }}>Standard Unit of Measure (EA, MTR, KGS, SET)</p>
          </div>
        </div>
      </div>
    </div>
  );
};
