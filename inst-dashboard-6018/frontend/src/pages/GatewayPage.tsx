import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './GatewayPage.css';
import LandingKpi from '../components/kpiCard/LandingKpi.tsx';

const MODULES = [
  {
    to: '/educational/admins',
    icon: '🎓',
    titleKey: 'nav.dashboard',
    descKey: 'home.dashboard_desc',
  },
  {
    to: '/corporate-dashboard',
    icon: '🏢',
    titleKey: 'nav.corporate',
    descKey: 'home.corporate_desc',
  },
  {
    to: '/executive-dashboard',
    icon: '📈',
    titleKey: 'nav.executive',
    descKey: 'home.executive_desc',
  },
] as const;

/**
 * Shared gateway for `/` and `/home` — module cards + suite chrome.
 * SSO may still land on `/home`; both routes render this same layout.
 */
const GatewayPage = () => {
  const { t } = useTranslation();
  const [kpis, setKpis] = useState<any | null>(null);

  useEffect(() => {
    const base = process.env.REACT_APP_API_BASE_URL;
    if (!base) return;
    axios
      .get(`${base}/data/kpis`)
      .then((r) => setKpis(r.data))
      .catch(() => {
        /* KPI strip is optional — gateway works without it */
      });
  }, []);

  return (
    <div className="gateway-page suite-motion-page">
      {kpis && (
        <div className="gateway-kpi-strip" aria-label={t('nav.dashboard')}>
          <div className="gateway-kpi-grid">
            <LandingKpi
              label={t('dashboard.performance_index_title')}
              value={`${kpis.overall_performance.value}%`}
            />
            <LandingKpi
              label={t('dashboard.lo_attainment_title')}
              value={`${kpis.avg_lo_attainment.value}%`}
            />
            <LandingKpi
              label={t('dashboard.pass_rate_title')}
              value={`${kpis.pass_rate.value}%`}
            />
          </div>
        </div>
      )}

      <header className="gateway-hero">
        <p className="gateway-brand">{t('home.brand', 'TDM Systems')}</p>
        <h1 className="gateway-title">{t('home.title', 'Welcome to TAMS Platform')}</h1>
        <p className="gateway-subtitle">
          {t('home.subtitle', 'Please select a module to get started')}
        </p>
      </header>

      <div className="gateway-module-grid">
        {MODULES.map((mod, index) => (
          <Link
            key={mod.to}
            to={mod.to}
            className="gateway-module-card suite-motion-card suite-card-hover"
            style={{ animationDelay: `${index * 80}ms` }}
          >
            <div className="gateway-module-icon" aria-hidden>
              {mod.icon}
            </div>
            <h2 className="gateway-module-title">{t(mod.titleKey)}</h2>
            <p className="gateway-module-desc">{t(mod.descKey)}</p>
            <span className="gateway-module-cta">{t('home.open', 'Open')}</span>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default GatewayPage;
