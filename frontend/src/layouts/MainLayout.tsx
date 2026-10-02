import React, { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Breadcrumb } from '../components/common/PageHeader';
import {
  LayoutDashboard,
  Package,
  UploadCloud,
  GitCompare,
  Search,
  CheckSquare,
  Layers,
  BarChart3,
  FileText,
  Users,
  Cpu,
  Clock,
  History,
  Settings,
  Building2,
  Database,
  Bell,
  LogOut,
  ChevronDown,
  Shield,
} from 'lucide-react';

interface NavCategory {
  title: string;
  items: Array<{
    to: string;
    label: string;
    icon: React.ReactNode;
  }>;
}

export const MainLayout: React.FC = () => {
  const { user, role, logout, forbiddenMessage, clearForbiddenMessage } = useAuth();
  const [showProfileMenu, setShowProfileMenu] = useState<boolean>(false);
  const location = useLocation();
  const navigate = useNavigate();

  if (!user) {
    return null;
  }

  // Define categorized navigation items based on user role
  const getNavCategories = (): NavCategory[] => {
    switch (role) {
      case 'ADMIN':
        return [
          {
            title: 'Workspace',
            items: [
              { to: '/admin/dashboard', label: 'Dashboard', icon: <LayoutDashboard size={16} /> },
              { to: '/admin/materials', label: 'Master Catalog', icon: <Package size={16} /> },
              { to: '/admin/data-management', label: 'Ingestion Pipeline', icon: <Database size={16} /> },
            ],
          },
          {
            title: 'Governance',
            items: [
              { to: '/admin/reviews', label: 'Review Management', icon: <CheckSquare size={16} /> },
              { to: '/admin/canonical-materials', label: 'Canonical Materials', icon: <Layers size={16} /> },
              { to: '/admin/taxonomy', label: 'UNSPSC Taxonomy', icon: <Layers size={16} /> },
              { to: '/admin/cpse-sources', label: 'CPSE Sources', icon: <Building2 size={16} /> },
            ],
          },
          {
            title: 'Analytics & Compliance',
            items: [
              { to: '/admin/analytics', label: 'Analytics', icon: <BarChart3 size={16} /> },
              { to: '/admin/reports', label: 'Reports & Export', icon: <FileText size={16} /> },
            ],
          },
          {
            title: 'Administration',
            items: [
              { to: '/admin/users', label: 'User Management', icon: <Users size={16} /> },
              { to: '/admin/model-status', label: 'AI/ML Engine Status', icon: <Cpu size={16} /> },
              { to: '/admin/jobs', label: 'Processing Jobs', icon: <Clock size={16} /> },
              { to: '/admin/audit-logs', label: 'Audit Logs', icon: <History size={16} /> },
              { to: '/admin/settings', label: 'System Settings', icon: <Settings size={16} /> },
            ],
          },
        ];
      case 'REVIEWER':
        return [
          {
            title: 'Workspace',
            items: [
              { to: '/reviewer/dashboard', label: 'Dashboard', icon: <LayoutDashboard size={16} /> },
              { to: '/reviewer/materials', label: 'Master Catalog', icon: <Package size={16} /> },
              { to: '/reviewer/matching', label: 'AI Matching Engine', icon: <GitCompare size={16} /> },
              { to: '/reviewer/duplicates', label: 'Potential Duplicates', icon: <Search size={16} /> },
            ],
          },
          {
            title: 'Governance',
            items: [
              { to: '/reviewer/reviews', label: 'Review Center', icon: <CheckSquare size={16} /> },
              { to: '/reviewer/harmonized', label: 'Harmonized Materials', icon: <Layers size={16} /> },
              { to: '/reviewer/canonical-materials', label: 'Canonical Materials', icon: <Layers size={16} /> },
            ],
          },
          {
            title: 'Analytics & Compliance',
            items: [
              { to: '/reviewer/analytics', label: 'Harmonization Analytics', icon: <BarChart3 size={16} /> },
              { to: '/reviewer/audit', label: 'Audit Trail', icon: <History size={16} /> },
              { to: '/reviewer/reports', label: 'Reports', icon: <FileText size={16} /> },
            ],
          },
        ];
      case 'OFFICER':
      default:
        return [
          {
            title: 'Workspace',
            items: [
              { to: '/user/dashboard', label: 'Dashboard', icon: <LayoutDashboard size={16} /> },
              { to: '/user/materials', label: 'Master Catalog', icon: <Package size={16} /> },
              { to: '/user/upload', label: 'Upload Materials', icon: <UploadCloud size={16} /> },
              { to: '/user/matching', label: 'AI Matching', icon: <GitCompare size={16} /> },
              { to: '/user/duplicates', label: 'Potential Duplicates', icon: <Search size={16} /> },
            ],
          },
          {
            title: 'Governance',
            items: [
              { to: '/user/review-queue', label: 'Review Queue', icon: <CheckSquare size={16} /> },
              { to: '/user/canonical-materials', label: 'Canonical Materials', icon: <Layers size={16} /> },
            ],
          },
          {
            title: 'Analytics & Reporting',
            items: [
              { to: '/user/analytics', label: 'Analytics', icon: <BarChart3 size={16} /> },
              { to: '/user/reports', label: 'Reports', icon: <FileText size={16} /> },
            ],
          },
        ];
    }
  };

  const navCategories = getNavCategories();

  // Compute breadcrumbs from current path
  const getBreadcrumbs = () => {
    const path = location.pathname;
    const baseHref = role === 'ADMIN' ? '/admin/dashboard' : role === 'REVIEWER' ? '/reviewer/dashboard' : '/user/dashboard';
    const base = [{ label: 'Portal', href: baseHref }];

    const breadcrumbMap: Record<string, { group: string; label: string }> = {
      '/admin/dashboard': { group: 'Administration', label: 'System Administration' },
      '/admin/users': { group: 'Administration', label: 'User Management & RBAC' },
      '/admin/materials': { group: 'Material Master', label: 'Master Catalog' },
      '/admin/cpse-sources': { group: 'CPSE Sources', label: 'Source Equivalence' },
      '/admin/data-management': { group: 'Ingestion Pipeline', label: 'Data Ingestion Jobs' },
      '/admin/reviews': { group: 'Review Center', label: 'Review Management' },
      '/admin/canonical-materials': { group: 'Harmonization', label: 'Canonical Materials (NMM)' },
      '/admin/taxonomy': { group: 'Taxonomy', label: 'UNSPSC Taxonomy' },
      '/admin/model-status': { group: 'AI Engine', label: 'Model Topology & Health' },
      '/admin/analytics': { group: 'Analytics', label: 'Harmonization Analytics' },
      '/admin/jobs': { group: 'Ingestion', label: 'Processing Jobs' },
      '/admin/audit-logs': { group: 'Compliance', label: 'Audit Logs' },
      '/admin/reports': { group: 'Compliance', label: 'Audit Reports & Export' },
      '/admin/settings': { group: 'Governance', label: 'System Settings' },

      '/reviewer/dashboard': { group: 'Reviewer Workspace', label: 'Review Center' },
      '/reviewer/materials': { group: 'Material Master', label: 'Master Catalog' },
      '/reviewer/matching': { group: 'Harmonization', label: 'AI Matching Engine' },
      '/reviewer/reviews': { group: 'Review Center', label: 'Validation Queue' },
      '/reviewer/duplicates': { group: 'Harmonization', label: 'Potential Duplicates' },
      '/reviewer/harmonized': { group: 'Harmonization', label: 'Harmonized Materials' },
      '/reviewer/canonical-materials': { group: 'Harmonization', label: 'Canonical Materials' },
      '/reviewer/analytics': { group: 'Analytics', label: 'Harmonization Analytics' },
      '/reviewer/audit': { group: 'Compliance', label: 'Audit Trail' },
      '/reviewer/reports': { group: 'Compliance', label: 'Reports' },

      '/user/dashboard': { group: 'Operations Workspace', label: 'Material Operations' },
      '/user/materials': { group: 'Material Master', label: 'Master Catalog' },
      '/user/upload': { group: 'Ingestion', label: 'Upload Materials' },
      '/user/matching': { group: 'Harmonization', label: 'AI Matching Engine' },
      '/user/duplicates': { group: 'Harmonization', label: 'Potential Duplicates' },
      '/user/review-queue': { group: 'Review Center', label: 'Review Queue' },
      '/user/canonical-materials': { group: 'Harmonization', label: 'Canonical Materials' },
      '/user/analytics': { group: 'Analytics', label: 'Harmonization Analytics' },
      '/user/reports': { group: 'Compliance', label: 'Reports' },
    };

    const match = breadcrumbMap[path];
    if (match) {
      return [...base, { label: match.group }, { label: match.label, active: true }];
    }
    return [...base, { label: 'Current Page', active: true }];
  };

  const handleSignOut = async () => {
    setShowProfileMenu(false);
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="app-container">
      {/* Sidebar (Deep Navy #0F2942) */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-brand-row">
            <div className="sidebar-logo-icon">M</div>
            <div className="sidebar-brand-text">
              <span className="sidebar-title">SIH26099 Portal</span>
              <span className="sidebar-subtitle">CPSE Material Master</span>
            </div>
          </div>
          <div className="sidebar-role-indicator">
            <span className="role-chip-label">ROLE</span>
            <span className={`badge ${role === 'ADMIN' ? 'badge-admin' : role === 'REVIEWER' ? 'badge-reviewer' : 'badge-officer'}`}>
              {role}
            </span>
          </div>
        </div>

        {/* Categorized Nav Scroll Area */}
        <div className="nav-scroll-area">
          {navCategories.map((category) => (
            <div key={category.title} style={{ marginBottom: '14px' }}>
              <div className="nav-category-header">{category.title}</div>
              <ul className="nav-list">
                {category.items.map((item) => (
                  <li key={item.to}>
                    <NavLink
                      to={item.to}
                      className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                      onClick={() => clearForbiddenMessage()}
                    >
                      <span className="nav-icon">{item.icon}</span>
                      <span>{item.label}</span>
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Sidebar Footer */}
        <div className="sidebar-footer">
          <div className="footer-status-row">
            <span className="status-dot active"></span>
            <span>Security: Active (JWT)</span>
          </div>
          <div className="user-tenant-info">
            <small>{user.name?.split(' ')[0]} • {user.cpse_name || 'CPSE'}</small>
          </div>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            style={{ width: '100%', marginTop: '6px', background: 'rgba(255,255,255,0.08)', color: '#FFFFFF', borderColor: 'rgba(255,255,255,0.15)' }}
            onClick={handleSignOut}
          >
            <LogOut size={13} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Top Header strictly matching Section 14 */}
        <header className="top-bar">
          <div className="top-bar-branding">
            <div className="gov-seal-icon">
              <Shield size={20} />
            </div>
            <div>
              <div className="top-bar-title">SIH26099</div>
              <div className="top-bar-subtitle">
                AI-Driven Standardization &amp; Harmonization of Material Codes Across CPSEs
              </div>
            </div>
          </div>

          <div className="top-bar-actions">
            {/* Global Search Bar */}
            <div className="global-search-wrap">
              <Search size={14} color="var(--text-muted)" />
              <input
                type="text"
                className="global-search-input"
                placeholder="Search catalog, codes..."
              />
              <span className="search-shortcut-badge">Ctrl+K</span>
            </div>

            {/* Notifications Icon */}
            <button
              type="button"
              className="header-action-btn"
              title="System Notifications"
            >
              <Bell size={16} />
              <span className="unread-indicator-dot"></span>
            </button>

            {/* Profile Pill & Dropdown */}
            <div className="user-profile-menu-wrap">
              <button
                type="button"
                className="user-profile-btn"
                onClick={() => setShowProfileMenu(!showProfileMenu)}
              >
                <div className="user-avatar-initials">
                  {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="user-meta-compact">
                  <span className="user-display-name">{user.name}</span>
                  <span className="user-role-badge">{role}</span>
                </div>
                <ChevronDown size={12} className="dropdown-caret" />
              </button>

              {showProfileMenu && (
                <div className="profile-dropdown-card">
                  <div className="dropdown-user-header">
                    <strong>{user.name}</strong>
                    <small>{user.email}</small>
                    <span className="cpse-badge" style={{ marginTop: '4px', alignSelf: 'flex-start' }}>
                      {user.cpse_name || 'Consortium'}
                    </span>
                  </div>
                  <hr className="dropdown-divider" />
                  <div className="dropdown-items">
                    <div>Employee ID: <code>{user.employee_id}</code></div>
                    <div>Assigned Role: <strong>{user.role}</strong></div>
                    <div>Tenant CPSE: <strong>{user.cpse_name || 'All CPSEs'}</strong></div>
                  </div>
                  <hr className="dropdown-divider" />
                  <button
                    type="button"
                    className="dropdown-signout-btn"
                    onClick={handleSignOut}
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Global Breadcrumb */}
        <div style={{ padding: '12px 32px 0 32px' }}>
          <Breadcrumb items={getBreadcrumbs()} />
        </div>

        {/* Global Alert for Forbidden Access */}
        {forbiddenMessage && (
          <div className="alert alert-danger" style={{ margin: '12px 32px 0 32px' }}>
            <span>🛡️</span>
            <div>{forbiddenMessage}</div>
            <button className="btn-close-alert" onClick={clearForbiddenMessage}>✕</button>
          </div>
        )}

        {/* Dynamic Body */}
        <div className="workspace-body">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
