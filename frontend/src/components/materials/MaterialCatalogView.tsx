import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { MaterialDetailModal } from './MaterialDetailModal';

export const MaterialCatalogView: React.FC = () => {
  const [materials, setMaterials] = useState<any[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [cpseFilter, setCpseFilter] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMaterialId, setSelectedMaterialId] = useState<number | null>(null);

  useEffect(() => {
    loadMaterials();
  }, [page, cpseFilter]);

  const loadMaterials = async () => {
    setLoading(true);
    setError(null);
    try {
      const cpse = cpseFilter === 'ALL' ? undefined : cpseFilter;
      const res = await api.getSourceMaterials(cpse, search, page, 20);
      setMaterials(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch {
      setError('Unable to load materials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadMaterials();
  };

  const handleRefresh = () => {
    loadMaterials();
  };

  const [isExporting, setIsExporting] = useState<boolean>(false);
  const handleExport = async () => {
    setIsExporting(true);
    try {
      const cpse = cpseFilter === 'ALL' ? undefined : cpseFilter;
      await api.exportMaterialsMasterCsv(cpse, search);
    } catch (err: any) {
      alert(`Export failed: ${err.message || 'Unable to download materials CSV.'}`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="material-catalog-container">
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Material Master Catalog</h1>
          <p className="page-subtitle">
            Enterprise raw material catalog ingested from participating CPSEs
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            Demonstration CPSE Data
          </span>
        </div>
      </div>

      {/* Filter, Search & Refresh Controls */}
      <div className="table-surface" style={{ padding: '12px 18px', marginBottom: '16px' }}>
        <form onSubmit={handleSearch} className="filter-form-flex" style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="search-wrap" style={{ flex: 1, minWidth: '260px' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search by Material Code, Description, or Grade..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <button type="submit" className="btn btn-secondary">Search</button>

          <div className="role-filter-group" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '13px', fontWeight: 600 }}>CPSE:</label>
            <select
              className="form-input select-role"
              value={cpseFilter}
              onChange={(e) => {
                setCpseFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="ALL">All CPSEs</option>
              <option value="ONGC">ONGC</option>
              <option value="BHEL">BHEL</option>
              <option value="IOCL">IOCL</option>
              <option value="NTPC">NTPC</option>
              <option value="SAIL">SAIL</option>
              <option value="GAIL">GAIL</option>
            </select>
          </div>

          <button type="button" className="btn btn-secondary" onClick={handleRefresh}>
            Refresh
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleExport}
            disabled={isExporting}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <span>{isExporting ? 'Exporting...' : 'Export CSV'}</span>
          </button>
        </form>
      </div>

      {error && (
        <div className="alert alert-danger mb-3">
          <span>⛔</span>
          <div>{error}</div>
          <button type="button" className="btn btn-secondary btn-sm ml-3" onClick={handleRefresh}>
            Retry
          </button>
        </div>
      )}

      {/* Materials Table */}
      <div className="table-surface">
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Catalog Inventory ({total.toLocaleString()} Items)</div>
            <div className="table-surface-subtitle">PostgreSQL Source Master Catalog</div>
          </div>
          <span className="cpse-badge">PostgreSQL Active</span>
        </div>

        {loading ? (
          <div className="dashboard-loading py-5">
            <div className="spinner"></div>
            <p>Loading materials...</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>CPSE</th>
                  <th>Original Code</th>
                  <th>Material Description</th>
                  <th>UOM</th>
                  <th>Grade</th>
                  <th>Technical Specification</th>
                  <th>Manufacturer</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {materials && materials.length > 0 ? (
                  materials.map((m) => (
                    <tr key={m.id}>
                      <td><span className="cpse-badge">{m.cpseName || m.cpse_name}</span></td>
                      <td><strong className="code-id">{m.materialCode || m.material_code}</strong></td>
                      <td>{m.description}</td>
                      <td><code>{m.unitOfMeasure || m.unit_of_measure || 'EA'}</code></td>
                      <td><span className="group-pill">{m.materialGrade || m.material_grade || '—'}</span></td>
                      <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{m.specification || '—'}</td>
                      <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{m.manufacturer || '—'}</td>
                      <td>
                        <span className="badge badge-success">{m.status || 'Active'}</span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={() => setSelectedMaterialId(m.id)}
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={9} className="text-center text-muted py-4">
                      No material records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {totalPages > 1 && (
          <div className="pagination-bar">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
            >
              &larr; Previous
            </button>
            <span className="pagination-info">
              Page {page} of {totalPages}
            </span>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
            >
              Next &rarr;
            </button>
          </div>
        )}
      </div>

      {selectedMaterialId !== null && (
        <MaterialDetailModal
          materialId={selectedMaterialId}
          onClose={() => setSelectedMaterialId(null)}
        />
      )}
    </div>
  );
};
