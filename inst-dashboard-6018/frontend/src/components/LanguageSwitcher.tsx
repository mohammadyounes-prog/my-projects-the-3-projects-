// frontend/src/components/LanguageSwitcher.tsx
import React from 'react';
import { useTranslation } from 'react-i18next';

const applyDocumentDirection = (lng: string) => {
  const dir = lng === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.dir = dir;
  document.documentElement.lang = lng;
  document.body.className = dir;
};

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();
  const active = (i18n.language || 'en').startsWith('ar') ? 'ar' : 'en';

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    applyDocumentDirection(lng);
  };

  const btnStyle = (lng: string): React.CSSProperties => ({
    paddingBlock: '5px',
    paddingInline: '10px',
    cursor: active === lng ? 'default' : 'pointer',
    border: '1px solid var(--suite-border, var(--nebula-border))',
    borderRadius: 'var(--suite-radius-sm, 4px)',
    backgroundColor: active === lng ? 'var(--suite-primary, #2c5282)' : 'var(--suite-surface-raised, var(--nebula-bg-glass))',
    color: active === lng ? 'var(--suite-on-primary, var(--nebula-bg-glass))' : 'var(--suite-text, #333)',
    fontFamily: 'var(--font-body, inherit)',
    fontWeight: 600,
  });

  return (
    <div
      className="language-switcher"
      role="group"
      aria-label="Language"
      style={{ display: 'flex', gap: '10px', alignItems: 'center' }}
    >
      <button
        type="button"
        onClick={() => changeLanguage('en')}
        disabled={active === 'en'}
        aria-pressed={active === 'en'}
        style={btnStyle('en')}
      >
        EN
      </button>
      <button
        type="button"
        onClick={() => changeLanguage('ar')}
        disabled={active === 'ar'}
        aria-pressed={active === 'ar'}
        style={btnStyle('ar')}
      >
        AR
      </button>
    </div>
  );
};

export default LanguageSwitcher;
