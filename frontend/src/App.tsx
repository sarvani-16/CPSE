import React, { useEffect, useState } from 'react';
import { BrowserRouter } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './context/AuthContext';
import { AppRoutes } from './routes/AppRoutes';
import { api } from './services/api';

const ServerStatusIndicator: React.FC = () => {
  const [status, setStatus] = useState<'idle' | 'waking' | 'ready'>('idle');
  const [details, setDetails] = useState<string>('');

  useEffect(() => {
    // 1. Immediate silent warm-up ping on application mount to awaken Render free-tier container
    api.warmup().catch(() => {});

    // 2. Keep-alive ping every 9 minutes while browser tab is active (prevents Render 15-min idle spin-down)
    const keepAlive = setInterval(() => {
      api.warmup().catch(() => {});
    }, 9 * 60 * 1000);

    // 3. Listen to cloud wake-up & reconnection events dispatched from api.ts
    const handleWakingUp = (e: any) => {
      const attempt = e.detail?.attempt || 1;
      const maxRetries = e.detail?.maxRetries || 3;
      setStatus('waking');
      setDetails(`Cloud server waking up from idle state (Render free tier) — Connecting (attempt ${attempt}/${maxRetries})...`);
    };

    const handleReady = () => {
      setStatus('ready');
      setDetails('Cloud server connected successfully.');
      setTimeout(() => {
        setStatus('idle');
      }, 3500);
    };

    window.addEventListener('server-waking-up', handleWakingUp);
    window.addEventListener('server-ready', handleReady);

    return () => {
      clearInterval(keepAlive);
      window.removeEventListener('server-waking-up', handleWakingUp);
      window.removeEventListener('server-ready', handleReady);
    };
  }, []);

  if (status === 'idle') return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: '14px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 9999,
        padding: '10px 18px',
        borderRadius: '6px',
        fontSize: '13px',
        fontWeight: 600,
        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        transition: 'all 0.3s ease',
        backgroundColor: status === 'waking' ? '#FEF3C7' : '#D1FAE5',
        color: status === 'waking' ? '#92400E' : '#065F46',
        border: `1px solid ${status === 'waking' ? '#FCD34D' : '#6EE7B7'}`
      }}
    >
      <span style={{ fontSize: '15px' }}>{status === 'waking' ? '⏳' : '✅'}</span>
      <span>{details}</span>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ServerStatusIndicator />
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
};
