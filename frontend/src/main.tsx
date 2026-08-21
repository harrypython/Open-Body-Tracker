import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import './i18n/config'
import { AuthProvider } from './contexts/AuthContext'
import { UnitProvider } from './contexts/UnitContext'
import { AppRouter } from './router'
import { Header } from './components/Header'

const AppContent: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <main>
        <AppRouter />
      </main>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <UnitProvider defaultSystem="metric">
        <AppContent />
      </UnitProvider>
    </AuthProvider>
  </React.StrictMode>,
)
