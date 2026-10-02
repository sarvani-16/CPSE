import React from 'react';

export const AuthLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="login-wrapper">
      <header className="gov-ribbon">
        <div className="gov-ribbon-content">
          <span className="gov-emblem">🏛️</span>
          <div className="gov-text">
            <strong>National Material Master Harmonization Framework</strong>
            <span className="gov-sub">Smart India Hackathon • SIH26099 • Central Public Sector Enterprises</span>
          </div>
          <div className="gov-tag">
            <span className="secure-badge">🔒 Secure Enterprise Access</span>
          </div>
        </div>
      </header>

      <main className="login-container">
        {children}
      </main>

      <footer className="login-gov-footer">
        <p>Enterprise Material Harmonization &amp; Standardization Gateway • Government of India Initiative</p>
      </footer>
    </div>
  );
};
