import React from 'react';

export const EmptyState: React.FC<{ message?: string; actionLabel?: string; onAction?: () => void }> = ({
  message = 'No records found.',
  actionLabel,
  onAction,
}) => (
  <div className="empty-state-box">
    <div className="empty-icon">📁</div>
    <p className="empty-text">{message}</p>
    {actionLabel && onAction && (
      <button className="btn btn-secondary btn-sm mt-2" onClick={onAction}>
        {actionLabel}
      </button>
    )}
  </div>
);

export const LoadingState: React.FC<{ message?: string }> = ({
  message = 'Loading enterprise records from PostgreSQL...',
}) => (
  <div className="loading-state-box">
    <div className="spinner"></div>
    <p className="loading-text">{message}</p>
  </div>
);

export const ErrorState: React.FC<{ error?: string; onRetry?: () => void }> = ({
  error = 'Unable to complete request. Please verify network or service status.',
  onRetry,
}) => (
  <div className="alert alert-danger error-state-box">
    <span>⛔</span>
    <div className="error-text-wrap">
      <strong>Enterprise Request Failed:</strong>
      <p>{error}</p>
    </div>
    {onRetry && (
      <button className="btn btn-secondary btn-sm ml-auto" onClick={onRetry}>
        Retry
      </button>
    )}
  </div>
);
