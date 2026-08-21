import { useTranslation } from 'react-i18next';

export const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => changeLanguage('en')}
        className={`px-2 py-1 text-sm rounded ${
          i18n.language === 'en'
            ? 'bg-blue-600 text-white'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => changeLanguage('pt')}
        className={`px-2 py-1 text-sm rounded ${
          i18n.language === 'pt'
            ? 'bg-blue-600 text-white'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
        }`}
      >
        PT
      </button>
    </div>
  );
};
