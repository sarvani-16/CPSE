import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { LoadingState, ErrorState } from '../common/FeedbackStates';
import { Layers, Plus, FolderTree } from 'lucide-react';

export const TaxonomyView: React.FC = () => {
  const { role } = useAuth();
  const [tree, setTree] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState<boolean>(false);

  // New Node Form
  const [newNodeCode, setNewNodeCode] = useState('');
  const [newNodeName, setNewNodeName] = useState('');
  const [newNodeParent, setNewNodeParent] = useState('');
  const [newNodeLevel, setNewNodeLevel] = useState(2);
  const [newNodeDesc, setNewNodeDesc] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadTaxonomy();
  }, []);

  const loadTaxonomy = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getTaxonomyTree();
      setTree(res || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load commodity taxonomy hierarchy.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNodeCode.trim() || !newNodeName.trim()) return;

    setSubmitting(true);
    try {
      await api.createTaxonomy({
        code: newNodeCode.trim().toUpperCase(),
        name: newNodeName.trim(),
        parent_code: newNodeParent ? newNodeParent.trim().toUpperCase() : undefined,
        level: Number(newNodeLevel),
        description: newNodeDesc.trim(),
      });
      setShowAddModal(false);
      setNewNodeCode('');
      setNewNodeName('');
      setNewNodeDesc('');
      loadTaxonomy();
    } catch (err: any) {
      setError(err.message || 'Failed to create taxonomy classification.');
    } finally {
      setSubmitting(false);
    }
  };

  const renderTree = (nodes: any[]) => {
    if (!nodes || nodes.length === 0) return null;
    return (
      <ul className="taxonomy-branch-list" style={{ listStyle: 'none', paddingLeft: '16px' }}>
        {nodes.map((node) => (
          <li key={node.code} style={{ margin: '8px 0' }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 12px',
                backgroundColor: 'var(--surface-subtle)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-xs)',
              }}
            >
              <span className="cpse-badge" style={{ fontSize: '10px' }}>L{node.level}</span>
              <strong className="code-id">{node.code}</strong>
              <span style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{node.name}</span>
              {node.description && <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>— {node.description}</span>}
            </div>
            {node.children && node.children.length > 0 && renderTree(node.children)}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div>
      {/* Page Header */}
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Commodity Taxonomy Management</h1>
          <p className="page-subtitle">
            Harmonized industrial classification tree across Central Public Sector Enterprises
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Official CPSE Taxonomy Framework
          </span>
          {role === 'ADMIN' && (
            <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
              <Plus size={15} />
              <span>Add Classification</span>
            </button>
          )}
        </div>
      </div>

      <div className="table-surface" style={{ padding: '20px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <div className="table-surface-title">Standard Classification Tree</div>
            <div className="table-surface-subtitle">
              Hierarchical categorization for mechanical, electrical, and structural materials
            </div>
          </div>
          {role !== 'ADMIN' && (
            <span className="badge badge-outline">Read-Only Access</span>
          )}
        </div>

        {loading && <LoadingState message="Loading multi-level commodity taxonomy from PostgreSQL..." />}
        {error && <ErrorState error={error} onRetry={loadTaxonomy} />}

        {!loading && tree.length > 0 && (
          <div style={{ padding: '10px 0' }}>
            {renderTree(tree)}
          </div>
        )}

        {!loading && tree.length === 0 && !error && (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No taxonomy classifications established yet.
          </div>
        )}
      </div>

      {/* Add Modal for Admin */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3 className="modal-title">Create Commodity Classification Node</h3>
              <button type="button" className="modal-close-btn" onClick={() => setShowAddModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <form onSubmit={handleAddSubmit}>
                <div className="form-group">
                  <label className="form-label">Classification Code (Unique Identifier)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. BEARINGS, INSTRUMENTATION"
                    value={newNodeCode}
                    onChange={(e) => setNewNodeCode(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Standard Title</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Industrial Roller &amp; Ball Bearings"
                    value={newNodeName}
                    onChange={(e) => setNewNodeName(e.target.value)}
                    required
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Parent Classification Code</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. MECHANICAL (Leave empty if root)"
                      value={newNodeParent}
                      onChange={(e) => setNewNodeParent(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Hierarchy Level</label>
                    <select
                      className="form-input"
                      value={newNodeLevel}
                      onChange={(e) => setNewNodeLevel(Number(e.target.value))}
                    >
                      <option value={1}>Level 1 (Major Domain)</option>
                      <option value={2}>Level 2 (Commodity Family)</option>
                      <option value={3}>Level 3 (Product Line)</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Technical Scope &amp; Description</label>
                  <textarea
                    className="form-input"
                    rows={3}
                    placeholder="Describe included industrial standard parts and specifications..."
                    value={newNodeDesc}
                    onChange={(e) => setNewNodeDesc(e.target.value)}
                  />
                </div>

                <div className="modal-footer" style={{ padding: '14px 0 0 0', display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                  <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={submitting}>
                    {submitting ? 'Saving...' : 'Add Classification'}
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
