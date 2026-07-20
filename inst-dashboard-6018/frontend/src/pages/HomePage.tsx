import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './HomePage.css';

const HomePage = () => {
  const { t } = useTranslation();

  return (
    <div className="home-page">
      <div className="home-hero">
        <h1 className="home-title">{t('home.title', 'Welcome to TAM Platform')}</h1>
        <p className="home-subtitle">
          {t('home.subtitle', 'Please select a module to get started')}
        </p>
      </div>
      
      <div className="module-grid">
        <Link to="/educational/admins" className="module-card">
          <div className="module-icon">🎓</div>
          <h2 className="module-title">{t('nav.dashboard')}</h2>
        </Link>
        <Link to="/corporate-dashboard" className="module-card">
          <div className="module-icon">🏢</div>
          <h2 className="module-title">{t('nav.corporate')}</h2>
        </Link>
        <Link to="/executive-dashboard" className="module-card">
          <div className="module-icon">📈</div>
          <h2 className="module-title">{t('nav.executive')}</h2>
        </Link>
      </div>
    </div>
  );
};

export default HomePage;
