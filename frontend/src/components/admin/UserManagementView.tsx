import React, { useEffect, useState } from 'react';
import { api, UserInfo } from '../../services/api';

export const UserManagementView: React.FC = () => {
  const [users, setUsers] = useState<UserInfo[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Edit Role Modal State
  const [selectedUser, setSelectedUser] = useState<UserInfo | null>(null);
  const [targetRole, setTargetRole] = useState<string>('OFFICER');
  const [isUpdating, setIsUpdating] = useState<boolean>(false);

  useEffect(() => {
    loadUsers();
  }, [page, roleFilter]);

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getUsers(roleFilter, search, page, 20);
      setUsers(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch user directory from PostgreSQL.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadUsers();
  };

  const handleToggleStatus = async (user: UserInfo) => {
    const newStatus = !user.is_active;
    const confirmAction = window.confirm(
      `Are you sure you want to ${newStatus ? 'ACTIVATE' : 'DEACTIVATE'} user ${user.name} (${user.employee_id})?`
    );
    if (!confirmAction) return;

    try {
      await api.changeUserStatus(user.id, newStatus);
      setSuccessMsg(`User ${user.employee_id} status updated to ${newStatus ? 'ACTIVE' : 'INACTIVE'}.`);
      loadUsers();
    } catch (err: any) {
      setError(err.message || 'Failed to change user status.');
    }
  };

  const openRoleModal = (user: UserInfo) => {
    setSelectedUser(user);
    setTargetRole(user.role);
  };

  const handleSaveRole = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUser) return;
    setIsUpdating(true);
    setError(null);
    try {
      await api.changeUserRole(selectedUser.id, targetRole);
      setSuccessMsg(`Role for ${selectedUser.employee_id} successfully updated to ${targetRole}.`);
      setSelectedUser(null);
      loadUsers();
    } catch (err: any) {
      setError(err.message || 'Failed to update user role.');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="user-management-container">
      <div className="page-header-block">
        <div>
          <h1 className="page-title">Users &amp; Roles Management</h1>
          <p className="page-subtitle">
            Enterprise Role-Based Access Control (RBAC) &amp; Status Governance (ADMIN ONLY)
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="header-provenance-tag">
            PostgreSQL Users Table
          </span>
        </div>
      </div>

      {successMsg && (
        <div className="alert alert-success" style={{ marginBottom: '16px' }}>
          <span>✓</span>
          <div>{successMsg}</div>
          <button className="btn-close-alert" onClick={() => setSuccessMsg(null)}>✕</button>
        </div>
      )}

      {error && (
        <div className="alert alert-danger" style={{ marginBottom: '16px' }}>
          <span>⛔</span>
          <div>{error}</div>
          <button className="btn-close-alert" onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="table-surface" style={{ padding: '12px 18px', marginBottom: '16px' }}>
        <form onSubmit={handleSearchSubmit} className="filter-form-flex" style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="search-wrap" style={{ flex: 1, minWidth: '260px' }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search by Employee ID, Name, Email, or CPSE..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-secondary">Search</button>

          <div className="role-filter-group" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '13px', fontWeight: 600 }}>Filter Role:</label>
            <select
              className="form-input select-role"
              value={roleFilter}
              onChange={(e) => {
                setRoleFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="ALL">All Roles</option>
              <option value="ADMIN">ADMIN</option>
              <option value="REVIEWER">REVIEWER</option>
              <option value="OFFICER">OFFICER</option>
            </select>
          </div>
        </form>
      </div>

      {/* Users Table */}
      <div className="table-surface">
        <div className="table-surface-header">
          <div>
            <div className="table-surface-title">Authorized Personnel Directory ({total} Total)</div>
            <div className="table-surface-subtitle">Spring Security &amp; JWT protected identities</div>
          </div>
          <span className="cpse-badge">RBAC Enforced</span>
        </div>

        {loading ? (
          <div className="dashboard-loading py-5">
            <div className="spinner"></div>
            <p>Querying PostgreSQL users database...</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Full Name</th>
                  <th>Official Email</th>
                  <th>CPSE Tenant</th>
                  <th>Assigned Role</th>
                  <th>Status</th>
                  <th>Last Login</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users && users.length > 0 ? (
                  users.map((u) => (
                    <tr key={u.id}>
                      <td><strong className="code-id">{u.employee_id}</strong></td>
                      <td>{u.name}</td>
                      <td>{u.email}</td>
                      <td><span className="cpse-badge">{u.cpse_name || 'CENTRAL'}</span></td>
                      <td>
                        <span className={`badge ${u.role === 'ADMIN' ? 'badge-admin' : u.role === 'REVIEWER' ? 'badge-reviewer' : 'badge-officer'}`}>
                          {u.role}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>
                          {u.is_active ? 'ACTIVE' : 'INACTIVE'}
                        </span>
                      </td>
                      <td>
                        {u.last_login ? new Date(u.last_login).toLocaleString() : <span className="text-muted">Never</span>}
                      </td>
                      <td>
                        <div className="action-buttons-inline">
                          <button
                            type="button"
                            className="btn btn-sm btn-secondary"
                            onClick={() => openRoleModal(u)}
                          >
                            Change Role
                          </button>
                          <button
                            type="button"
                            className={`btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-approve'}`}
                            onClick={() => handleToggleStatus(u)}
                          >
                            {u.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="text-center text-muted py-4">No user records found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination-bar">
            <button
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
              className="btn btn-secondary btn-sm"
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
            >
              Next &rarr;
            </button>
          </div>
        )}
      </div>

      {/* Change Role Modal */}
      {selectedUser && (
        <div className="modal-overlay">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3 className="modal-title">Change Role Authorization</h3>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setSelectedUser(null)}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveRole} className="modal-form">
              <p className="modal-notice">
                Updating role permissions for <strong>{selectedUser.name}</strong> ({selectedUser.employee_id}).
                This event is audited under enterprise compliance.
              </p>

              <div className="form-group">
                <label>Select Authorized Role</label>
                <select
                  className="form-input"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                >
                  <option value="ADMIN">ADMIN — Full System Access, RBAC & Configuration</option>
                  <option value="REVIEWER">REVIEWER — Technical Audit & Review Approvals</option>
                  <option value="OFFICER">OFFICER — Material Ingestion & Operational Access</option>
                </select>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setSelectedUser(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isUpdating}
                >
                  {isUpdating ? 'Saving...' : 'Apply Role Change'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
