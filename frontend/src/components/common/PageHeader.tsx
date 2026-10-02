import React from 'react';

interface BreadcrumbProps {
  items: Array<{ label: string; href?: string; active?: boolean }>;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => (
  <nav aria-label="Breadcrumb" className="breadcrumb-nav">
    <ol className="breadcrumb-list">
      {items.map((item, idx) => (
        <li key={idx} className={`breadcrumb-item ${item.active ? 'active' : ''}`}>
          {item.active || !item.href ? (
            <span aria-current={item.active ? 'page' : undefined}>{item.label}</span>
          ) : (
            <a href={item.href}>{item.label}</a>
          )}
          {idx < items.length - 1 && <span className="breadcrumb-sep">/</span>}
        </li>
      ))}
    </ol>
  </nav>
);

interface PageHeaderProps {
  title: string;
  subtitle: string;
  provenanceLabel?: string;
  actionButton?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  provenanceLabel,
  actionButton,
}) => (
  <div className="page-header-wrapper">
    <div className="page-header-text">
      <h2 className="section-title">{title}</h2>
      <p className="section-subtitle">{subtitle}</p>
    </div>
    <div className="page-header-actions">
      {provenanceLabel && (
        <div className="provenance-tag">
          <span>{provenanceLabel}</span>
        </div>
      )}
      {actionButton}
    </div>
  </div>
);
