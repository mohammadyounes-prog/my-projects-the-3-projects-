import React from 'react';
import { useTranslation } from 'react-i18next';

const SettingsPage = () => {
  const { t } = useTranslation();

  return (
    <div className="dashboard-container suite-motion-page">
      <div className="dashboard-section" style={{ maxWidth: '700px', marginInline: 'auto' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--suite-primary)', display: 'block', marginBottom: '0.5rem' }}>
          {t('brand.suite', 'TDM Systems')} Settings
        </span>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.75rem', fontWeight: '700', color: 'var(--suite-text)', margin: '0 0 1rem' }}>
          {t('settings.title', 'Settings & Preferences')}
        </h1>
        <div style={{ backgroundColor: 'var(--suite-primary-soft)', border: '1px solid var(--suite-border)', padding: '1.25rem', borderRadius: 'var(--suite-radius-md)' }}>
          <p className="settings-stub" style={{ margin: 0, color: 'var(--suite-text-muted)', fontSize: '0.95rem' }}>
            {t(
              'settings.not_configured',
              'System settings & integration parameters are managed globally. Advanced configuration features will be active upon tenant deployment.'
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
