import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthState, UserProfile } from '../types';

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: Partial<UserProfile> & { password: string }) => Promise<void>;
  updateUser: (data: Partial<UserProfile>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem('auth_token'),
    isAuthenticated: !!localStorage.getItem('auth_token'),
  });

  useEffect(() => {
    if (authState.token) {
      // TODO: Fetch user profile with token
      // For now, we just mark as authenticated
      setAuthState(prev => ({ ...prev, isAuthenticated: true }));
    }
  }, [authState.token]);

  const login = async (email: string, _password: string) => {
    // TODO: Implement actual API call
    // const response = await apiClient.post('/auth/login', { email, password });
    // const { access_token } = response.data;
    
    // Mock for now
    localStorage.setItem('auth_token', 'mock_token_' + email);
    setAuthState({
      user: { 
        id: '1', 
        email, 
        full_name: 'Test User',
        default_unit_system: 'metric'
      },
      token: 'mock_token_' + email,
      isAuthenticated: true,
    });
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  };

  const register = async (_data: Partial<UserProfile> & { password: string }) => {
    // TODO: Implement actual API call
    // await apiClient.post('/auth/register', data);
    console.log('Register:', _data);
  };

  const updateUser = (data: Partial<UserProfile>) => {
    setAuthState(prev => ({
      ...prev,
      user: prev.user ? { ...prev.user, ...data } : null,
    }));
  };

  return (
    <AuthContext.Provider value={{ ...authState, login, logout, register, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};
