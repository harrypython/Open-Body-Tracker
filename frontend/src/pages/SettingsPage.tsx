import { useTranslation } from 'react-i18next';

export const SettingsPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        {t('settings.title')}
      </h1>
      
      <div className="max-w-2xl space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            {t('settings.language')}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Language settings are available in the header.
          </p>
        </div>
        
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            {t('settings.unitSystem')}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Unit system toggle is available in the header.
          </p>
        </div>
      </div>
    </div>
  );
};
