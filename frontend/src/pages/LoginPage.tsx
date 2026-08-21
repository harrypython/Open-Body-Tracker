import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import { Input } from './ui/Input';
import { Button } from './ui/Button';

export const LoginPage: React.FC = () => {
  const { t } = useTranslation();
  const { login } = useAuth();
  
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    
    try {
      await login(email, password);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            {t('auth.login')}
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <Input
            label={t('auth.email')}
            name="email"
            type="email"
            autoComplete="email"
            required
          />
          <Input
            label={t('auth.password')}
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
          <Button type="submit" variant="primary" className="w-full">
            {t('auth.login')}
          </Button>
        </form>
      </div>
    </div>
  );
};
