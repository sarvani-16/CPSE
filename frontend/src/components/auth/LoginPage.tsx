import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ShieldCheck, Layers, Cpu, Activity, KeyRound } from 'lucide-react';

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
          <div className="login-brand-badge">
            <span className="badge-pulse-dot" />
            CPSE INTER-ENTERPRISE CONSORTIUM
          </div>
          <h1 className="login-brand-title">
            National Material Master
          </h1>
          <p className="login-brand-subtitle">
            AI-Driven Codification &amp; Cross-CPSE Harmonization Mesh
          </p>
        </div>

        {/* Dynamic Enterprise Mesh Graphic */}
        <div className="login-visual-container">
          <svg
            className="login-mesh-svg"
            viewBox="0 0 460 280"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="cyanLine" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#0284C7" stopOpacity="0.2" />
              </linearGradient>
              <linearGradient id="goldLine" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#F59E0B" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#D97706" stopOpacity="0.2" />
              </linearGradient>
              <linearGradient id="emeraldLine" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#34D399" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#059669" stopOpacity="0.2" />
              </linearGradient>
              <linearGradient id="indigoLine" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#818CF8" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#4F46E5" stopOpacity="0.2" />
              </linearGradient>
              <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.25" />
                <stop offset="60%" stopColor="#0284C7" stopOpacity="0.08" />
                <stop offset="100%" stopColor="#0284C7" stopOpacity="0" />
              </radialGradient>
              <filter id="nodeGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Orbiting Concentric Rings */}
            <circle cx="230" cy="140" r="115" stroke="rgba(56, 189, 248, 0.15)" strokeWidth="1" strokeDasharray="4 4" className="spin-slow" />
            <circle cx="230" cy="140" r="82" stroke="rgba(245, 158, 11, 0.16)" strokeWidth="1" strokeDasharray="6 3" className="spin-reverse" />
            <circle cx="230" cy="140" r="48" stroke="rgba(56, 189, 248, 0.28)" strokeWidth="1" />
            <circle cx="230" cy="140" r="40" fill="url(#coreGlow)" />

            {/* Mesh Links between Satellite Nodes */}
            <line x1="80" y1="50" x2="60" y2="140" stroke="rgba(255, 255, 255, 0.08)" strokeDasharray="3 3" />
            <line x1="60" y1="140" x2="80" y2="230" stroke="rgba(255, 255, 255, 0.08)" strokeDasharray="3 3" />
            <line x1="380" y1="50" x2="400" y2="140" stroke="rgba(255, 255, 255, 0.08)" strokeDasharray="3 3" />
            <line x1="400" y1="140" x2="380" y2="230" stroke="rgba(255, 255, 255, 0.08)" strokeDasharray="3 3" />
            <line x1="80" y1="50" x2="380" y2="50" stroke="rgba(56, 189, 248, 0.08)" strokeDasharray="4 4" />
            <line x1="80" y1="230" x2="380" y2="230" stroke="rgba(56, 189, 248, 0.08)" strokeDasharray="4 4" />

            {/* Radial High-Tech Data Highway Lines to Hub */}
            <line x1="80" y1="50" x2="230" y2="140" stroke="url(#goldLine)" strokeWidth="1.6" />
            <line x1="60" y1="140" x2="230" y2="140" stroke="url(#indigoLine)" strokeWidth="1.6" />
            <line x1="80" y1="230" x2="230" y2="140" stroke="url(#cyanLine)" strokeWidth="1.6" />
            <line x1="380" y1="50" x2="230" y2="140" stroke="url(#cyanLine)" strokeWidth="1.6" />
            <line x1="400" y1="140" x2="230" y2="140" stroke="url(#emeraldLine)" strokeWidth="1.6" />
            <line x1="380" y1="230" x2="230" y2="140" stroke="url(#goldLine)" strokeWidth="1.6" />

            {/* Data Pulse Nodes along routes */}
            <circle cx="155" cy="95" r="3" fill="#F59E0B" className="pulse-node" />
            <circle cx="145" cy="140" r="3" fill="#818CF8" className="pulse-node" />
            <circle cx="155" cy="185" r="3" fill="#38BDF8" className="pulse-node" />
            <circle cx="305" cy="95" r="3" fill="#38BDF8" className="pulse-node" />
            <circle cx="315" cy="140" r="3" fill="#34D399" className="pulse-node" />
            <circle cx="305" cy="185" r="3" fill="#F59E0B" className="pulse-node" />

            {/* Satellite CPSE Node 1: ONGC */}
            <g transform="translate(80, 50)">
              <circle r="20" fill="#0A1628" stroke="#F59E0B" strokeWidth="1.8" filter="url(#nodeGlow)" />
              <text textAnchor="middle" y="4" fill="#FFFFFF" fontSize="9.5" fontWeight="700" letterSpacing="0.5">ONGC</text>
              <rect x="-24" y="24" width="48" height="14" rx="3" fill="rgba(245, 158, 11, 0.12)" stroke="rgba(245, 158, 11, 0.3)" />
              <text textAnchor="middle" y="34" fill="#F59E0B" fontSize="7.5" fontWeight="600" letterSpacing="0.5">ENERGY</text>
            </g>

            {/* Satellite CPSE Node 2: IOCL */}
            <g transform="translate(60, 140)">
              <circle r="20" fill="#0A1628" stroke="#818CF8" strokeWidth="1.8" filter="url(#nodeGlow)" />
              <text textAnchor="middle" y="4" fill="#FFFFFF" fontSize="9.5" fontWeight="700" letterSpacing="0.5">IOCL</text>
              <rect x="-26" y="24" width="52" height="14" rx="3" fill="rgba(129, 140, 248, 0.12)" stroke="rgba(129, 140, 248, 0.3)" />
              <text textAnchor="middle" y="34" fill="#818CF8" fontSize="7.5" fontWeight="600" letterSpacing="0.5">REFINING</text>
            </g>

            {/* Satellite CPSE Node 3: SAIL */}
            <g transform="translate(80, 230)">
              <circle r="20" fill="#0A1628" stroke="#38BDF8" strokeWidth="1.8" filter="url(#nodeGlow)" />
              <text textAnchor="middle" y="4" fill="#FFFFFF" fontSize="9.5" fontWeight="700" letterSpacing="0.5">SAIL</text>
              <rect x="-22" y="24" width="44" height="14" rx="3" fill="rgba(56, 189, 248, 0.12)" stroke="rgba(56, 189, 248, 0.3)" />
              <text textAnchor="middle" y="34" fill="#38BDF8" fontSize="7.5" fontWeight="600" letterSpacing="0.5">STEEL</text>
            </g>

            {/* Satellite CPSE Node 4: BHEL */}
            <g transform="translate(380, 50)">
              <circle r="20" fill="#0A1628" stroke="#38BDF8" strokeWidth="1.8" filter="url(#nodeGlow)" />
              <text textAnchor="middle" y="4" fill="#FFFFFF" fontSize="9.5" fontWeight="700" letterSpacing="0.5">BHEL</text>
              <rect x="-28" y="24" width="56" height="14" rx="3" fill="rgba(56, 189, 248, 0.12)" stroke="rgba(56, 189, 248, 0.3)" />
              <text textAnchor="middle" y="34" fill="#38BDF8" fontSize="7.5" fontWeight="600" letterSpacing="0.5">ELECTRICAL</text>
            </g>

            {/* Satellite CPSE Node 5: GAIL */}
            <g transform="translate(400, 140)">
              <circle r="20" fill="#0A1628" stroke="#34D399" strokeWidth="1.8" filter="url(#nodeGlow)" />
              <text textAnchor="middle" y="4" fill="#FFFFFF" fontSize="9.5" fontWeight="700" letterSpacing="0.5">GAIL</text>
              <rect x="-22" y="24" width="44" height="14" rx="3" fill="rgba(52, 211, 153, 0.12)" stroke="rgba(52, 211, 153, 0.3)" />
              <text textAnchor="middle" y="34" fill="#34D399" fontSize="7.5" fontWeight="600" letterSpacing="0.5">GAS GRID</text>
            </g>

            {/* Satellite CPSE Node 6: NTPC */}
            <g transform="translate(380, 230)">
              <circle r="20" fill="#0A1628" stroke="#F59E0B" strokeWidth="1.8" filter="url(#nodeGlow)" />
              <text textAnchor="middle" y="4" fill="#FFFFFF" fontSize="9.5" fontWeight="700" letterSpacing="0.5">NTPC</text>
              <rect x="-22" y="24" width="44" height="14" rx="3" fill="rgba(245, 158, 11, 0.12)" stroke="rgba(245, 158, 11, 0.3)" />
              <text textAnchor="middle" y="34" fill="#F59E0B" fontSize="7.5" fontWeight="600" letterSpacing="0.5">POWER</text>
            </g>

            {/* Central National Hub Core */}
            <g transform="translate(230, 140)">
              <circle r="34" fill="#071220" stroke="#38BDF8" strokeWidth="2.2" filter="url(#nodeGlow)" />
              <circle r="28" fill="none" stroke="rgba(245, 158, 11, 0.4)" strokeWidth="1" strokeDasharray="3 3" />
              <polygon points="0,-12 10,-5 10,7 0,13 -10,7 -10,-5" fill="none" stroke="#F59E0B" strokeWidth="1.5" />
              <circle cx="0" cy="0" r="3" fill="#38BDF8" />
              <text textAnchor="middle" y="20" fill="#F8FAFC" fontSize="8" fontWeight="800" letterSpacing="1">NATIONAL</text>
              <text textAnchor="middle" y="27" fill="#38BDF8" fontSize="6.5" fontWeight="700" letterSpacing="0.8">MASTER</text>
            </g>

            {/* Telemetry labels */}
            <rect x="175" y="10" width="110" height="16" rx="4" fill="rgba(15, 23, 42, 0.85)" stroke="rgba(56, 189, 248, 0.25)" />
            <text x="230" y="21.5" textAnchor="middle" fill="#38BDF8" fontSize="8" fontWeight="700" letterSpacing="0.8">DATA MESH ACTIVE</text>

            <rect x="165" y="258" width="130" height="16" rx="4" fill="rgba(15, 23, 42, 0.85)" stroke="rgba(245, 158, 11, 0.25)" />
            <text x="230" y="269.5" textAnchor="middle" fill="#F59E0B" fontSize="8" fontWeight="700" letterSpacing="0.8">6 ENTERPRISES LINKED</text>
          </svg>
        </div>

        {/* Minimalist 4 Feature Glass Badges */}
        <div className="login-feature-strip">
          <div className="login-feature-chip">
            <div className="feature-chip-icon">
              <Layers size={16} />
            </div>
            <div className="feature-chip-text">
              <div className="feature-chip-title">Cross-CPSE Sync</div>
              <div className="feature-chip-sub">Equivalence Mesh</div>
            </div>
          </div>

          <div className="login-feature-chip">
            <div className="feature-chip-icon gold">
              <Cpu size={16} />
            </div>
            <div className="feature-chip-text">
              <div className="feature-chip-title">Hybrid AI Engine</div>
              <div className="feature-chip-sub">Vector + Lexical</div>
            </div>
          </div>

          <div className="login-feature-chip">
            <div className="feature-chip-icon emerald">
              <ShieldCheck size={16} />
            </div>
            <div className="feature-chip-text">
              <div className="feature-chip-title">Conflict Guard</div>
              <div className="feature-chip-sub">Zero Collision</div>
            </div>
          </div>

          <div className="login-feature-chip">
            <div className="feature-chip-icon indigo">
              <Activity size={16} />
            </div>
            <div className="feature-chip-text">
              <div className="feature-chip-title">Immutable Audit</div>
              <div className="feature-chip-sub">Provable Lineage</div>
            </div>
          </div>
        </div>

        {/* Clean Status Footer */}
        <div className="login-brand-footer">
          <div className="login-footer-badge">
            <span className="footer-live-dot" />
            Verified Enterprise Portal
          </div>
          <div className="login-footer-meta">
            SIH26099 • Ministry of Heavy Industries
          </div>
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
