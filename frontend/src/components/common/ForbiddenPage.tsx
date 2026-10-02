import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const ForbiddenPage: React.FC<{ onReturnToDashboard?: () => void }> = ({ onReturnToDashboard }) => {
  const navigate = useNavigate();
  const { role } = useAuth();

  const handleReturn = () => {
    if (onReturnToDashboard) {
      onReturnToDashboard();
    } else {
      if (role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/user/dashboard');
      }
    }
  };

  return (
    <div className="forbidden-container">
      <div className="card forbidden-card">
        <div className="forbidden-icon">🛡️</div>
        <h2 className="forbidden-title">Access Restricted (HTTP 403)</h2>
        <p className="forbidden-message">
          You do not have permission to access this section.
        </p>
        <p className="forbidden-sub">
          Your assigned role (<strong>{role || 'UNAUTHENTICATED'}</strong>) does not grant privileges for this enterprise resource.
          Access control is strictly enforced by Spring Boot Security RBAC.
        </p>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleReturn}
        >
          Return to Authorized Dashboard
        </button>
      </div>
    </div>
  );
};
