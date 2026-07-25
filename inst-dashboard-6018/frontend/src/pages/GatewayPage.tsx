import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './GatewayPage.css';
import LandingKpi from '../components/kpiCard/LandingKpi.tsx';
import { getRole, MODULE_LINKS, visibleModules, type ModuleId } from '../auth/roles.ts';

const GATEWAY_MODULE_META: Partial<
  Record<ModuleId, { icon: React.ReactNode; descKey: string }>
> = {
  educational: { 
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>, 
    descKey: 'home.dashboard_desc' 
  },
  corporate: { 
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M16 10h.01M8 10h.01M8 14h.01M12 14h.01M16 14h.01"/></svg>, 
    descKey: 'home.corporate_desc' 
  },
  executive: { 
    icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>, 
    descKey: 'home.executive_desc' 
  },
};

/** Gateway cards show the three product modules only (not Weights/Settings). */
const GATEWAY_CARD_ORDER: ModuleId[] = [
  'educational',
  'corporate',
  'executive',
];

/**
 * Shared gateway for `/` and `/home` — module cards + suite chrome.
 * SSO may still land on `/home`; both routes render this same layout.
 */
const GatewayPage = () => {
  const { t } = useTranslation();
  const [kpis, setKpis] = useState<any | null>(null);

  const modules = useMemo(() => {
    const allowed = new Set(visibleModules(getRole()));
    return GATEWAY_CARD_ORDER.filter((id) => allowed.has(id)).map((id) => {
      const link = MODULE_LINKS[id];
      const meta = GATEWAY_MODULE_META[id]!;
      return {
        to: link.to,
        icon: meta.icon,
        titleKey: link.labelKey,
        descKey: meta.descKey,
      };
    });
  }, []);

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
    <div className="gateway-page nebula-motion-page">
      {kpis?.overall_performance?.value != null && (
        <div className="gateway-kpi-strip" aria-label={t('nav.dashboard')}>
          <div className="gateway-kpi-grid">
            <LandingKpi
              label={t('dashboard.performance_index_title')}
              value={`${kpis.overall_performance?.value ?? 0}%`}
            />
            <LandingKpi
              label={t('dashboard.lo_attainment_title')}
              value={`${kpis.avg_lo_attainment?.value ?? 0}%`}
            />
            <LandingKpi
              label={t('dashboard.pass_rate_title')}
              value={`${kpis.pass_rate?.value ?? 0}%`}
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
        {modules.map((mod, index) => (
          <Link
            key={mod.to}
            to={mod.to}
            className="gateway-module-card nebula-motion-card"
            style={{ animationDelay: `${index * 60}ms` }}
          >
            <span className="gateway-module-icon" aria-hidden>
              {mod.icon}
            </span>
            <span className="gateway-module-body">
              <h2 className="gateway-module-title">{t(mod.titleKey)}</h2>
              <p className="gateway-module-desc">{t(mod.descKey)}</p>
            </span>
            <span className="gateway-module-chevron" aria-hidden>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 5l7 7-7 7"/></svg>
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default GatewayPage;
