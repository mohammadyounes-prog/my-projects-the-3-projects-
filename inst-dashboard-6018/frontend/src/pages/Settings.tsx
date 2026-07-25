import React from 'react';
import { useTranslation } from 'react-i18next';

const SettingsPage = () => {
  const { t } = useTranslation();

  return (
    <div className="settings-page">
      <h1>{t('settings.title', 'Settings')}</h1>
      <p className="settings-stub">
        {t(
          'settings.not_configured',
          'Settings are not configured yet. This page will be available when configuration is enabled.'
        )}
      </p>
    </div>
  );
};

export default SettingsPage;
