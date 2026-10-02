import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, UserInfo, getStoredToken, getStoredUser, setStoredSession, clearStoredSession } from '../services/api';

interface AuthContextType {
  user: UserInfo | null;
  token: string | null;
  role: 'ADMIN' | 'REVIEWER' | 'OFFICER' | null;
  employeeId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  sessionExpiredMessage: string | null;
  forbiddenMessage: string | null;
  login: (username: string, password: string) => Promise<UserInfo>;
  register: (payload: { employee_id: string; name: string; email: string; password: string; cpse_name: string }) => Promise<UserInfo>;
  logout: () => Promise<void>;
  clearSessionExpiredMessage: () => void;
  clearForbiddenMessage: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [user, setUser] = useState<UserInfo | null>(getStoredUser());
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [sessionExpiredMessage, setSessionExpiredMessage] = useState<string | null>(null);
  const [forbiddenMessage, setForbiddenMessage] = useState<string | null>(null);

  useEffect(() => {
    // Validate current token with backend on mount
    const initAuth = async () => {
      const storedToken = getStoredToken();
      if (storedToken) {
        try {
          const profile = await api.getMe();
          setUser(profile);
          setToken(storedToken);
        } catch {
          // Token invalid or expired
          clearStoredSession();
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();

    // Listen to custom global auth events from API client
    const handleSessionExpired = (e: any) => {
      clearStoredSession();
      setToken(null);
      setUser(null);
      setSessionExpiredMessage(e.detail?.message || 'Your session has expired. Please sign in again.');
    };

    const handleForbidden = (e: any) => {
      setForbiddenMessage(e.detail?.message || 'Access Restricted: You do not have permission to access this resource.');
    };

    window.addEventListener('session-expired', handleSessionExpired);
    window.addEventListener('forbidden-access', handleForbidden);

    return () => {
      window.removeEventListener('session-expired', handleSessionExpired);
      window.removeEventListener('forbidden-access', handleForbidden);
    };
  }, []);

  const login = async (username: string, password: string): Promise<UserInfo> => {
    setSessionExpiredMessage(null);
    setForbiddenMessage(null);
    const resp = await api.login({ username, password });
    setStoredSession(resp.token, resp.user);
    setToken(resp.token);
    setUser(resp.user);
    return resp.user;
  };

  const register = async (payload: { employee_id: string; name: string; email: string; password: string; cpse_name: string }): Promise<UserInfo> => {
    const newUser = await api.register(payload);
    return newUser;
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (e) {
      console.warn('Logout API error:', e);
    } finally {
      clearStoredSession();
      setToken(null);
      setUser(null);
    }
  };

  const clearSessionExpiredMessage = () => setSessionExpiredMessage(null);
  const clearForbiddenMessage = () => setForbiddenMessage(null);

  const value: AuthContextType = {
    user,
    token,
    role: user?.role || null,
    employeeId: user?.employee_id || null,
    isAuthenticated: !!token && !!user,
    isLoading,
    sessionExpiredMessage,
    forbiddenMessage,
    login,
    register,
    logout,
    clearSessionExpiredMessage,
    clearForbiddenMessage,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
