import { useContext, useEffect, useState } from 'react';
import { createContext, ReactNode } from 'react';

import { LanguageSwitcher } from '../components/ui/LanguageSwitcher';
import { UnitToggle } from '../components/ui/UnitToggle';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { AppRouter } from '../router';

// --- Context definitions ---

export type User = {
  id: string;
  email: string;
  fullName: string;
  height: number;
  unit: 'metric' | 'imperial';
};

export type AuthContextValue = {
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    // Mock API call – replace with real authentication request.
    const fakeUser: User = {
      id: '1',
      email,
      fullName: 'John Doe',
      height: 180,
      unit: 'metric',
    };
    setUser(fakeUser);
  };

  const logout = () => setUser(null);

  const contextValue: AuthContextValue = {
    isAuthenticated: !!user,
    user,
    login,
    logout,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

// --- Custom hook for consuming the context ---

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};

// --- App component that ties everything together ---

export const MainApp: React.FC = () => {
  return (
    <AuthProvider>
      <Header />
      <main className="min-h-screen bg-gray-100 dark:bg-gray-900">
        <AppRouter />
      </main>
      <Footer />
    </AuthProvider>
  );
};
