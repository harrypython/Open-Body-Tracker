import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { UnitToggle } from './ui/UnitToggle';
import { LanguageSwitcher } from './ui/LanguageSwitcher';
import { Button } from './ui/Button';

export const Header: React.FC = () => {
  const { t } = useTranslation();
  const { isAuthenticated, logout } = useAuth();

  return (
    <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Open Body Tracker
            </h1>
            {isAuthenticated && (
              <nav className="hidden md:flex items-center gap-4">
                <a
                  href="/dashboard"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
                >
                  {t('dashboard.title')}
                </a>
                <a
                  href="/settings"
                  className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
                >
                  {t('settings.title')}
                </a>
              </nav>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <UnitToggle />
            {isAuthenticated && (
              <Button variant="outline" size="sm" onClick={logout}>
                {t('auth.logout')}
              </Button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
