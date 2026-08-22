import { useTranslation } from 'react-i18next';
import ProfileForm from '../components/forms/ProfileForm';

export const ProfilePage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{t('profile.title')}</h1>
      <ProfileForm />
    </div>
  );
};
