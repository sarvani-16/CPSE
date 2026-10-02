import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Shield, Layers, Cpu, AlertTriangle, History, KeyRound } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login, register, user, isAuthenticated, sessionExpiredMessage, clearSessionExpiredMessage } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(() => {
    return new URLSearchParams(window.location.search).get('testSuccess') || null;
  });

  useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'ADMIN') {
        navigate('/admin/dashboard', { replace: true });
      } else if (user.role === 'REVIEWER') {
        navigate('/reviewer/dashboard', { replace: true });
      } else {
        navigate('/user/dashboard', { replace: true });
      }
    }
  }, [isAuthenticated, user, navigate]);

  // Register Modal State
  const [showRegisterModal, setShowRegisterModal] = useState(() => {
    return new URLSearchParams(window.location.search).get('register') === 'true';
  });
  const [regFullName, setRegFullName] = useState('');
  const [regEmployeeId, setRegEmployeeId] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regCpse, setRegCpse] = useState('ONGC');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [regError, setRegError] = useState<string | null>(() => {
    return new URLSearchParams(window.location.search).get('testError') || null;
  });
  const [isRegistering, setIsRegistering] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setErrorMessage('Please enter both Employee ID / Email and Password.');
      return;
    }

    setErrorMessage(null);
    setSuccessMessage(null);
    setIsSubmitting(true);

    try {
      const authUser = await login(username.trim(), password);
      if (authUser.role === 'ADMIN') {
        navigate('/admin/dashboard', { replace: true });
      } else if (authUser.role === 'REVIEWER') {
        navigate('/reviewer/dashboard', { replace: true });
      } else {
        navigate('/user/dashboard', { replace: true });
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickFill = (empId: string, devPass: string) => {
    setUsername(empId);
    setPassword(devPass);
    setErrorMessage(null);
    if (sessionExpiredMessage) clearSessionExpiredMessage();
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegError(null);

    if (!regFullName.trim()) {
      setRegError('Full name is required.');
      return;
    }

    if (!regEmployeeId.trim()) {
      setRegError('Employee ID is required.');
      return;
    }

    if (!regCpse || !regCpse.trim()) {
      setRegError('Please select a CPSE.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!regEmail.trim() || !emailRegex.test(regEmail.trim())) {
      setRegError('Please enter a valid official email address.');
      return;
    }

    if (!regPassword || regPassword.length < 6) {
      setRegError('Password must contain at least 6 characters.');
      return;
    }

    if (regPassword !== regConfirmPassword) {
      setRegError('Passwords do not match.');
      return;
    }

    setIsRegistering(true);
    try {
      const newUser = await register({
        employee_id: regEmployeeId.trim(),
        name: regFullName.trim(),
        email: regEmail.trim(),
        cpse_name: regCpse.trim(),
        password: regPassword,
      });

      setShowRegisterModal(false);
      setSuccessMessage('Account created successfully. Please sign in.');
      setUsername(newUser.employee_id);
      setPassword('');
      setRegFullName('');
      setRegEmployeeId('');
      setRegEmail('');
      setRegPassword('');
      setRegConfirmPassword('');
    } catch (err: any) {
      setRegError(err.message || 'Registration failed. Check details.');
    } finally {
      setIsRegistering(false);
    }
  };

  return (
    <div className="login-split-wrapper">
      {/* Left 45% Navy Brand Panel */}
      <div className="login-brand-panel">
        <div className="login-brand-header">
          <div className="login-brand-badge">SIH26099 • ENTERPRISE FRAMEWORK</div>
          <h1 className="login-brand-title">
            National Material Master Codification &amp; Harmonization Platform
          </h1>
          <p className="login-brand-desc">
            AI-powered standardization of material codes, cross-CPSE equivalence mapping, and duplicate prevention across India&apos;s Central Public Sector Enterprises.
          </p>
        </div>

        {/* 4 Value Pillars */}
        <div className="login-pillars-grid">
          <div className="login-pillar-card">
            <div className="pillar-icon-row">
              <Layers size={16} />
              <span>Cross-CPSE Harmonization</span>
            </div>
            <div className="pillar-desc">
              Unified codification across ONGC, IOCL, BHEL, NTPC, GAIL, and SAIL.
            </div>
          </div>

          <div className="login-pillar-card">
            <div className="pillar-icon-row">
              <Cpu size={16} />
              <span>Hybrid AI Matching</span>
            </div>
            <div className="pillar-desc">
              TF-IDF, RapidFuzz lexical matching, and SentenceTransformer semantic vectors.
            </div>
          </div>

          <div className="login-pillar-card">
            <div className="pillar-icon-row">
              <AlertTriangle size={16} />
              <span>Technical Conflict Guard</span>
            </div>
            <div className="pillar-desc">
              Automatic prevention of non-interchangeable schedule, pressure, or grade collisions.
            </div>
          </div>

          <div className="login-pillar-card">
            <div className="pillar-icon-row">
              <History size={16} />
              <span>Immutable Audit Trail</span>
            </div>
            <div className="pillar-desc">
              Full provenance and chain-of-custody tracking for public accountability.
            </div>
          </div>
        </div>

        <div className="login-brand-footer">
          Smart India Hackathon SIH26099 • Ministry of Heavy Industries &amp; Public Enterprises
        </div>
      </div>

      {/* Right 55% Form Panel */}
      <div className="login-form-panel">
        <div className="login-card-surface">
          <div className="login-card-header">
            <h2 className="login-welcome-title">Sign In to Enterprise Workspace</h2>
            <p className="login-welcome-sub">
              Enter your official credentials to access the CPSE material portal
            </p>
          </div>

          {sessionExpiredMessage && (
            <div className="alert alert-warning" style={{ marginBottom: '16px' }}>
              <span>⚠️</span>
              <div>
                <strong>Session Terminated:</strong> {sessionExpiredMessage}
              </div>
            </div>
          )}

          {errorMessage && (
            <div className="alert alert-danger" style={{ marginBottom: '16px' }}>
              <span>⛔</span>
              <div>{errorMessage}</div>
            </div>
          )}

          {successMessage && (
            <div className="alert alert-success" style={{ marginBottom: '16px' }}>
              <span>✓</span>
              <div>{successMessage}</div>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="username">
                Official Employee ID or Government Email
              </label>
              <input
                id="username"
                type="text"
                className="form-input"
                placeholder="e.g., ADM001, REV001, USR001 or name@cpse.gov.in"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">
                Secure Password
              </label>
              <div className="password-wrap">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  placeholder="Enter your confidential password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  className="btn-show-pass"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            <div className="login-options-row">
              <label className="remember-label">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span>Remember this terminal</span>
              </label>
              <a
                href="#forgot"
                className="forgot-pass-link"
                onClick={(e) => {
                  e.preventDefault();
                  alert('For password resets, contact your nodal CPSE Security Administrator.');
                }}
              >
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              className="btn-signin-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Authenticating...' : 'Sign In to Workspace'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <button
              type="button"
              className="btn-link"
              style={{ fontSize: '12.5px', color: 'var(--color-info)' }}
              onClick={() => setShowRegisterModal(true)}
            >
              Register New Account (Officer)
            </button>
          </div>

          {/* Quick Demo Fill Section */}
          <div className="quick-fill-block">
            <div className="quick-fill-label">
              <KeyRound size={13} />
              <span>Development / Demonstration Credentials</span>
            </div>
            <div className="quick-fill-buttons">
              <button
                type="button"
                className="btn-quick-fill"
                onClick={() => handleQuickFill('USR001', 'officer123')}
                title="Procurement Officer role"
              >
                Officer (USR001)
              </button>
            </div>
          </div>

          <div className="authorized-personnel-tag">
            Authorized personnel only. All transactions are logged under strict audit governance.
          </div>
        </div>
      </div>

      {/* Registration Modal */}
      {showRegisterModal && (
        <div
          className="modal-overlay"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.7)',
            backdropFilter: 'blur(3px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2100,
            padding: '20px'
          }}
          onClick={(e) => { if (e.target === e.currentTarget) setShowRegisterModal(false); }}
        >
          <div
            className="modal-dialog register-modal-dialog"
            style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #CBD5E1',
              borderRadius: '8px',
              boxShadow: '0 25px 50px -12px rgba(15, 23, 42, 0.4), 0 12px 24px -8px rgba(15, 23, 42, 0.25)',
              width: '100%',
              maxWidth: '520px',
              overflow: 'hidden',
              position: 'relative',
              zIndex: 2101
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              className="modal-header"
              style={{
                backgroundColor: '#FFFFFF',
                borderBottom: '1px solid #CBD5E1',
                padding: '18px 24px 14px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <h3 className="modal-title" style={{ color: '#0F172A', fontSize: '18px', fontWeight: 700, margin: 0 }}>
                Register Enterprise Account
              </h3>
              <button
                type="button"
                className="modal-close-btn"
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#64748B',
                  fontSize: '18px',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  lineHeight: 1
                }}
                onClick={() => setShowRegisterModal(false)}
              >
                ✕
              </button>
            </div>

            <div
              className="modal-body"
              style={{
                backgroundColor: '#FFFFFF',
                padding: '20px 24px 24px 24px'
              }}
            >
              <form onSubmit={handleRegisterSubmit} noValidate style={{ backgroundColor: '#FFFFFF' }}>
                <p style={{ fontSize: '12.5px', color: '#64748B', marginBottom: '14px', lineHeight: 1.45 }}>
                  Official accounts are granted standard <strong>OFFICER</strong> privileges by default.
                  Elevated privileges require System Administrator authorization.
                </p>

                {regError && (
                  <div className="alert alert-danger" style={{ marginBottom: '12px' }}>
                    {regError}
                  </div>
                )}

                <div className="form-group" style={{ marginBottom: '14px', backgroundColor: '#FFFFFF' }}>
                  <label className="form-label" style={{ color: '#334155', fontSize: '13px', fontWeight: 600, marginBottom: '5px', display: 'block' }}>
                    Full Official Name
                  </label>
                  <input
                    type="text"
                    className="form-input"
                    style={{ backgroundColor: '#F8FAFC', border: '1px solid #CBD5E1', color: '#0F172A', borderRadius: '4px', width: '100%', padding: '8px 12px' }}
                    placeholder="e.g. Ramesh Kumar"
                    value={regFullName}
                    onChange={(e) => setRegFullName(e.target.value)}
                    required
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '14px', backgroundColor: '#FFFFFF' }}>
                  <div className="form-group" style={{ marginBottom: 0, backgroundColor: '#FFFFFF' }}>
                    <label className="form-label" style={{ color: '#334155', fontSize: '13px', fontWeight: 600, marginBottom: '5px', display: 'block' }}>
                      Official Employee ID
                    </label>
                    <input
                      type="text"
                      className="form-input"
                      style={{ backgroundColor: '#F8FAFC', border: '1px solid #CBD5E1', color: '#0F172A', borderRadius: '4px', width: '100%', padding: '8px 12px' }}
                      placeholder="e.g. EMP4012"
                      value={regEmployeeId}
                      onChange={(e) => setRegEmployeeId(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: 0, backgroundColor: '#FFFFFF' }}>
                    <label className="form-label" style={{ color: '#334155', fontSize: '13px', fontWeight: 600, marginBottom: '5px', display: 'block' }}>
                      Participating CPSE
                    </label>
                    <select
                      className="form-input"
                      style={{ backgroundColor: '#F8FAFC', border: '1px solid #CBD5E1', color: '#0F172A', borderRadius: '4px', width: '100%', padding: '8px 12px' }}
                      value={regCpse}
                      onChange={(e) => setRegCpse(e.target.value)}
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

                <div className="form-group" style={{ marginBottom: '14px', backgroundColor: '#FFFFFF' }}>
                  <label className="form-label" style={{ color: '#334155', fontSize: '13px', fontWeight: 600, marginBottom: '5px', display: 'block' }}>
                    Official Email Address
                  </label>
                  <input
                    type="email"
                    className="form-input"
                    style={{ backgroundColor: '#F8FAFC', border: '1px solid #CBD5E1', color: '#0F172A', borderRadius: '4px', width: '100%', padding: '8px 12px' }}
                    placeholder="name@cpse.co.in"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    required
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px', backgroundColor: '#FFFFFF' }}>
                  <div className="form-group" style={{ marginBottom: 0, backgroundColor: '#FFFFFF' }}>
                    <label className="form-label" style={{ color: '#334155', fontSize: '13px', fontWeight: 600, marginBottom: '5px', display: 'block' }}>
                      Password
                    </label>
                    <input
                      type="password"
                      className="form-input"
                      style={{ backgroundColor: '#F8FAFC', border: '1px solid #CBD5E1', color: '#0F172A', borderRadius: '4px', width: '100%', padding: '8px 12px' }}
                      placeholder="Minimum 6 characters"
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group" style={{ marginBottom: 0, backgroundColor: '#FFFFFF' }}>
                    <label className="form-label" style={{ color: '#334155', fontSize: '13px', fontWeight: 600, marginBottom: '5px', display: 'block' }}>
                      Confirm Password
                    </label>
                    <input
                      type="password"
                      className="form-input"
                      style={{ backgroundColor: '#F8FAFC', border: '1px solid #CBD5E1', color: '#0F172A', borderRadius: '4px', width: '100%', padding: '8px 12px' }}
                      placeholder="Re-enter password"
                      value={regConfirmPassword}
                      onChange={(e) => setRegConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="modal-footer" style={{ padding: '14px 0 0 0', display: 'flex', justifyContent: 'flex-end', gap: '8px', backgroundColor: '#FFFFFF' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowRegisterModal(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isRegistering}
                  >
                    {isRegistering ? 'Registering...' : 'Register Account'}
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
