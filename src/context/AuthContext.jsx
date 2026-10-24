import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => {
    return localStorage.getItem('mindsync_token') || null;
  });

  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('mindsync_user');
    const storedToken = localStorage.getItem('mindsync_token');
    if (saved && storedToken) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    return null;
  });

  const [isLoadingAuth, setIsLoadingAuth] = useState(true);

  // Authenticated is strictly true only if a valid token and user exist
  const isAuthenticated = Boolean(token && user);

  // Verify JWT token with backend on initial mount
  useEffect(() => {
    let isMounted = true;

    const verifyToken = async () => {
      const storedToken = localStorage.getItem('mindsync_token');
      if (storedToken) {
        try {
          const profile = await authApi.getMe();
          if (isMounted && profile && profile.id) {
            setUser(profile);
            setToken(storedToken);
            localStorage.setItem('mindsync_user', JSON.stringify(profile));
          }
        } catch (err) {
          console.warn("Session expired or token invalid:", err?.message);
          if (isMounted) {
            setUser(null);
            setToken(null);
            localStorage.removeItem('mindsync_token');
            localStorage.removeItem('mindsync_user');
            localStorage.removeItem('mindsync_auth');
          }
        }
      } else {
        if (isMounted) {
          setUser(null);
          setToken(null);
        }
      }
      if (isMounted) {
        setIsLoadingAuth(false);
      }
    };

    verifyToken();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (email, password) => {
    // Clear any previous session cached data
    localStorage.removeItem('mindsync_items_v1');
    localStorage.removeItem('mindsync_reminders_v1');
    localStorage.removeItem('cognivault_items_v1');
    localStorage.removeItem('cognivault_reminders_v1');

    // Authenticate with MongoDB Atlas backend
    const data = await authApi.login(email, password);
    const jwtToken = data.token || data.access_token;
    setUser(data);
    setToken(jwtToken);
    localStorage.setItem('mindsync_token', jwtToken);
    localStorage.setItem('mindsync_user', JSON.stringify(data));
    localStorage.setItem('mindsync_auth', 'true');
    return data;
  };

  const signup = async (name, email, password) => {
    // Clear any previous session cached data
    localStorage.removeItem('mindsync_items_v1');
    localStorage.removeItem('mindsync_reminders_v1');
    localStorage.removeItem('cognivault_items_v1');
    localStorage.removeItem('cognivault_reminders_v1');

    // Register user in MongoDB Atlas backend
    const data = await authApi.signup(name, email, password);
    const jwtToken = data.token || data.access_token;
    setUser(data);
    setToken(jwtToken);
    localStorage.setItem('mindsync_token', jwtToken);
    localStorage.setItem('mindsync_user', JSON.stringify(data));
    localStorage.setItem('mindsync_auth', 'true');
    return data;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('mindsync_token');
    localStorage.removeItem('mindsync_user');
    localStorage.removeItem('mindsync_auth');
    localStorage.removeItem('mindsync_items_v1');
    localStorage.removeItem('mindsync_reminders_v1');
    localStorage.removeItem('cognivault_items_v1');
    localStorage.removeItem('cognivault_reminders_v1');
  };

  const updateProfile = async (updates) => {
    const updated = await authApi.updateProfile(updates);
    setUser(updated);
    localStorage.setItem('mindsync_user', JSON.stringify(updated));
    return updated;
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, isLoadingAuth, login, signup, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
