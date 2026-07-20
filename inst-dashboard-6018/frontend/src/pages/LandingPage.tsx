import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './LandingPage.css';
import LandingKpi from '../components/kpiCard/LandingKpi.tsx';

const LandingPage = () => {
  const { t } = useTranslation();
  const [kpis, setKpis] = useState<any | null>(null);

  useEffect(() => {
    axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/kpis`).then(r => setKpis(r.data));
  }, []);

  return (
    <div className="landing-page">
      {kpis && (
        <div className="landing-kpi-wrapper">
          <div className="landing-kpi-grid">
            <LandingKpi label={t('dashboard.performance_index_title')} value={`${kpis.overall_performance.value}%`} />
            <LandingKpi label={t('dashboard.lo_attainment_title')} value={`${kpis.avg_lo_attainment.value}%`} />
            <LandingKpi label={t('dashboard.pass_rate_title')} value={`${kpis.pass_rate.value}%`} />
          </div>
        </div>
      )}

      <div className="landing-hero">
        <h1 className="landing-title">{t('home.title', 'Welcome to TAMS Platform')}</h1>
        <p className="landing-subtitle">
          {t('home.subtitle', 'Your Ultimate Roadmap To Success')}
        </p>
      </div>
      
      <div className="landing-module-grid">
        <Link to="/educational/admins" className="landing-module-card">
          <div className="landing-module-icon">🎓</div>
          <h2 className="landing-module-title">{t('nav.dashboard')}</h2>
          <p>{t('home.dashboard_desc')}</p>
        </Link>
        <Link to="/corporate-dashboard" className="landing-module-card">
          <div className="landing-module-icon">🏢</div>
          <h2 className="landing-module-title">{t('nav.corporate')}</h2>
          <p>{t('home.corporate_desc')}</p>
        </Link>
        <Link to="/executive-dashboard" className="landing-module-card">
          <div className="landing-module-icon">📈</div>
          <h2 className="landing-module-title">{t('nav.executive')}</h2>
          <p>{t('home.executive_desc')}</p>
        </Link>
      </div>
    </div>
  );
};

export default LandingPage;
