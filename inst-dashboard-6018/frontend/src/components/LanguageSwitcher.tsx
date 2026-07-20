// frontend/src/components/LanguageSwitcher.tsx
import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px', alignItems: 'center' }}>
      <button 
        onClick={() => changeLanguage('en')} 
        disabled={i18n.language === 'en'}
        style={{ 
          padding: '5px 10px', 
          cursor: 'pointer', 
          border: '1px solid #ccc', 
          borderRadius: '4px',
          backgroundColor: i18n.language === 'en' ? '#007bff' : 'white',
          color: i18n.language === 'en' ? 'white' : '#333'
        }}
      >
        EN
      </button>
      <button 
        onClick={() => changeLanguage('ar')} 
        disabled={i18n.language === 'ar'}
        style={{ 
          padding: '5px 10px', 
          cursor: 'pointer', 
          border: '1px solid #ccc', 
          borderRadius: '4px',
          backgroundColor: i18n.language === 'ar' ? '#007bff' : 'white',
          color: i18n.language === 'ar' ? 'white' : '#333'
        }}
      >
        AR
      </button>
    </div>
  );
};

export default LanguageSwitcher;
