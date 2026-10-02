import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const norm = (status || '').toUpperCase();

  if (norm === 'APPROVED' || norm === 'ACTIVE' || norm === 'COMPLETED' || norm === 'OPERATIONAL' || norm === 'CONNECTED') {
    return <span className="badge badge-success">✓ {status}</span>;
  }
  if (norm === 'NEEDS_REVIEW' || norm === 'REVIEW' || norm === 'PENDING' || norm === 'PROCESSING') {
    return <span className="badge badge-warn">! {status}</span>;
  }
  if (norm === 'REJECTED' || norm === 'INACTIVE' || norm === 'FAILED' || norm === 'CONFLICT_DETECTED') {
    return <span className="badge badge-danger">× {status}</span>;
  }
  return <span className="badge badge-outline">{status}</span>;
};
