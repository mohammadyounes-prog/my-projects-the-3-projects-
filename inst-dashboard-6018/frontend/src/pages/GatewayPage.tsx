import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import './GatewayPage.css';
import LandingKpi from '../components/kpiCard/LandingKpi.tsx';
import { getRole, MODULE_LINKS, visibleModules, type ModuleId } from '../auth/roles.ts';

const GATEWAY_MODULE_META: Partial<
  Record<ModuleId, { icon: string; descKey: string }>
> = {
  educational: { icon: '🎓', descKey: 'home.dashboard_desc' },
  corporate: { icon: '🏢', descKey: 'home.corporate_desc' },
  executive: { icon: '📈', descKey: 'home.executive_desc' },
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
    <div className="gateway-page suite-motion-page">
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
