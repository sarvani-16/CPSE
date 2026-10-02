import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { AuthLayout } from '../../layouts/AuthLayout';

export const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [employeeId, setEmployeeId] = useState('');
  const [email, setEmail] = useState('');
  const [cpseName, setCpseName] = useState('ONGC');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!fullName.trim() || !employeeId.trim() || !email.trim() || !password.trim()) {
      setError('All mandatory fields must be completed.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters in length.');
      return;
    }

    setIsSubmitting(true);
    try {
      await register({
        employee_id: employeeId.trim(),
        name: fullName.trim(),
        email: email.trim(),
        password: password,
        cpse_name: cpseName
      });
      setSuccess('Enterprise account created successfully! You may now sign in.');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please contact your CPSE IT administrator.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout>
      <div className="login-card">
        <div className="login-header">
          <div className="login-badge">CPSE ONBOARDING</div>
          <h2 className="login-title">Register Enterprise Account</h2>
          <p className="login-subtitle">
            Create an official account for CPSE Material Management &amp; Harmonization.
          </p>
        </div>

        {error && (
          <div className="alert alert-danger">
            <span>⚠️</span>
            <div>{error}</div>
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <span>✓</span>
            <div>{success}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <p className="modal-notice">
            New accounts are assigned <strong>OFFICER</strong> privileges by default. Elevated REVIEWER and ADMIN roles are assigned by the CPSE Nodal Administrator.
          </p>

          <div className="form-group">
            <label>Full Official Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Ramesh Kumar"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Official Employee ID</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. EMP4012"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Participating CPSE</label>
              <select
                className="form-input"
                value={cpseName}
                onChange={(e) => setCpseName(e.target.value)}
              >
                <option value="ONGC">ONGC - Oil &amp; Natural Gas</option>
                <option value="BHEL">BHEL - Heavy Electricals</option>
                <option value="IOCL">IOCL - Indian Oil Corp</option>
                <option value="NTPC">NTPC - Power Generation</option>
                <option value="SAIL">SAIL - Steel Authority</option>
                <option value="GAIL">GAIL - Gas Authority</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Official Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="name@cpse.co.in"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="Minimum 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                className="form-input"
                placeholder="Re-enter password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block btn-login"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Registering Account...' : 'Register Enterprise Account'}
          </button>
        </form>

        <div className="login-footer-actions mt-3">
          <Link to="/login" className="btn-link">Already registered? Sign In to Workspace</Link>
        </div>
      </div>
    </AuthLayout>
  );
};
