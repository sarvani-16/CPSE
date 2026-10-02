import React, { useEffect, useState } from 'react';
import { api, CanonicalMaterialItem } from '../../services/api';
import { Layers, Plus, Search, CheckCircle2, Shield } from 'lucide-react';

export const CanonicalView: React.FC = () => {
  const [items, setItems] = useState<CanonicalMaterialItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDesc, setNewDesc] = useState('');
  const [newCategory, setNewCategory] = useState('General');
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadCanonical();
  }, [search]);

  const loadCanonical = async () => {
    try {
      setLoading(true);
      const res = await api.getCanonicalMaterials(search);
      setItems(res.items || []);
      setTotal(res.total || 0);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDesc.trim()) return;
    try {
      const res = await api.autoCreateCanonical({
        description: newDesc,
        category: newCategory,
        cpse_name: 'DEMO_ENTERPRISE',
      });
      setMessage(`Successfully created Prototype Canonical Code: ${res.canonical_code}`);
      setShowCreateModal(false);
      setNewDesc('');
      loadCanonical();
    } catch (err: any) {
      alert(`Creation failed: ${err.message}`);
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">National Canonical Material Master (NMM Series)</h1>
          <p className="page-subtitle">
            Unified, harmonized common material catalog. Original CPSE item codes remain permanently mapped.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            NMM Common Codification
          </span>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus size={15} />
            <span>Create Canonical Code</span>
          </button>
        </div>
      </div>

      {message && (
        <div className="alert alert-success" style={{ marginBottom: '16px' }}>
          <span>✓</span>
          <div>{message}</div>
          <button className="btn-close-alert" onClick={() => setMessage(null)}>✕</button>
        </div>
      )}

      {/* Filter Surface */}
      <div className="table-surface" style={{ padding: '12px 18px', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Search size={15} color="var(--text-muted)" />
          <input
            type="text"
            className="form-input"
            placeholder="Search canonical materials by NMM code, standardized description, or specification..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ border: 'none', padding: '4px 8px' }}
          />
        </div>
      </div>

      {/* Table Surface */}
      <div className="table-surface">
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Canonical Repository ({total.toLocaleString()} Codes)</div>
            <div className="table-surface-subtitle">Master standardized descriptions across CPSEs</div>
          </div>
          <span className="cpse-badge">National Catalog</span>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading canonical master repository...
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Common Material Code</th>
                  <th>Standardized Description</th>
                  <th>Commodity Category</th>
                  <th>UOM</th>
                  <th>Governance Status</th>
                </tr>
              </thead>
              <tbody>
                {items && items.length > 0 ? (
                  items.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <span className="code-id">{item.nationalMaterialCode}</span>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{item.codeTypeLabel}</div>
                      </td>
                      <td>
                        <strong>{item.standardizedDescription}</strong>
                      </td>
                      <td>
                        <span className="group-pill">{item.category || 'General'}</span>
                      </td>
                      <td>
                        <code style={{ fontSize: '12px' }}>{item.standardUom || 'EA'}</code>
                      </td>
                      <td>
                        <span className="badge badge-success">{item.approvalStatus || 'APPROVED'}</span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                      No canonical records found matching query.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Overlay */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3 className="modal-title">Dynamic Canonical Material Creation</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setShowCreateModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleCreate}>
                <div className="form-group">
                  <label className="form-label">Material Description</label>
                  <textarea
                    className="form-input"
                    rows={3}
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                    placeholder="e.g. Centrifugal Boiler Feed Pump Impeller Bronze Grade 2"
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Procurement Category</label>
                  <input
                    type="text"
                    className="form-input"
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                  />
                </div>
                <div className="modal-footer" style={{ padding: '14px 0 0 0', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                  <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Generate NMM Code
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
