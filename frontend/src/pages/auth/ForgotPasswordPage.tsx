import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AuthLayout } from '../../layouts/AuthLayout';

export const ForgotPasswordPage: React.FC = () => {
  const [identifier, setIdentifier] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim()) return;
    setSubmitted(true);
  };

  return (
    <AuthLayout>
      <div className="login-card">
        <div className="login-header">
          <div className="login-badge">CREDENTIAL RECOVERY</div>
          <h2 className="login-title">Reset Enterprise Access</h2>
          <p className="login-subtitle">
            Provide your official Employee ID or registered email address.
          </p>
        </div>

        {submitted ? (
          <div className="alert alert-success">
            <span>✓</span>
            <div>
              <strong>Recovery Notice Issued:</strong> If the provided account exists, recovery instructions have been dispatched to your official CPSE administrator.
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label>Official Employee ID or Government Email</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. ADM001, REV001, USR001"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block btn-login">
              Submit Recovery Request
            </button>
          </form>
        )}

        <div className="login-footer-actions mt-3">
          <Link to="/login" className="btn-link">Return to Sign In</Link>
        </div>
      </div>
    </AuthLayout>
  );
};
