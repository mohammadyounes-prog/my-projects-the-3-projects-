import React, { useEffect, useMemo, useState } from 'react';
import { Outlet, useLocation, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher.tsx';
import { getRole, MODULE_LINKS, visibleModules } from '../../auth/roles.ts';
import './Layout.css';

type NavItem = { to: string; labelKey: string; fallback: string };

const Layout = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  useEffect(() => {
    document.documentElement.dir = i18n.dir();
    document.body.className = i18n.language === 'ar' ? 'rtl' : 'ltr';
  }, [i18n.language]);

  const performLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_name');
    localStorage.removeItem('role');
    setShowLogoutModal(false);
    window.location.href = '/login';
  };

  const handleGoToHub = () => {
    setShowLogoutModal(false);
    const hubUrl = process.env.REACT_APP_HUB_URL || 'http://localhost:6015';
    window.location.href = hubUrl;
  };

  const isRtl = i18n.dir() === 'rtl';
  const path = location.pathname;
  const isGateway = path === '/' || path === '/home';

  const footerModuleKey = useMemo(() => {
    if (path.startsWith('/educational')) return 'footer.module_educational';
    if (path.startsWith('/executive-dashboard')) return 'footer.module_executive';
    if (path.startsWith('/corporate-dashboard')) return 'footer.module_corporate';
    if (path.startsWith('/weights')) return 'footer.module_weights';
    if (path.startsWith('/settings')) return 'footer.module_settings';
    if (isGateway) return 'footer.module_gateway';
    return 'footer.module_gateway';
  }, [path, isGateway]);

  const footerModuleFallback = useMemo(() => {
    if (path.startsWith('/educational')) return 'Educational Analytics Module';
    if (path.startsWith('/executive-dashboard')) return 'Executive Strategic Module';
    if (path.startsWith('/corporate-dashboard')) return 'Corporate HR Intelligence Module';
    if (path.startsWith('/weights')) return 'Indexes Weight Module';
    if (path.startsWith('/settings')) return 'Settings';
    return 'Dashboard Gateway';
  }, [path]);

  /** Gateway: Home only. Module pages: role-filtered module links (no Contact — B6). */
  const navItems: NavItem[] = useMemo(() => {
    const home: NavItem = { to: '/', labelKey: 'nav.home', fallback: 'Home' };
    if (isGateway) {
      return [home];
    }
    const role = getRole();
    const moduleNav: NavItem[] = visibleModules(role).map((mod) => {
      const link = MODULE_LINKS[mod];
      return { to: link.to, labelKey: link.labelKey, fallback: link.fallback };
    });
    return [home, ...moduleNav];
  }, [isGateway]);

  return (
    <div dir={i18n.dir()} className={isRtl ? 'rtl-layout nebula-root' : 'ltr-layout nebula-root'} style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div className="nebula-neural-grid"></div>
      <header className="app-header nebula-motion-header">
        <nav className="app-nav">
          <Link to="/" className="app-brand" aria-label={`${t('brand.suite', 'TDM Systems')} — ${t('brand.product', 'Dashboard')}`}>
            <span className="brand-suite">{t('brand.suite', 'TDM Systems')}</span>
            <span className="brand-product">{t('brand.product', 'Dashboard')}</span>
          </Link>

          <div className={`nav-links${isGateway ? ' nav-links--gateway' : ''}`}>
            {navItems.map((item) => {
              let isActive = false;
              if (item.to === '/') {
                isActive = isGateway;
              } else if (item.to.startsWith('/educational')) {
                isActive = path.startsWith('/educational');
              } else {
                isActive = path === item.to || path.startsWith(`${item.to}/`);
              }
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={isActive ? 'nav-link-active' : undefined}
                >
                  {t(item.labelKey, item.fallback)}
                </Link>
              );
            })}
          </div>

          <div className="nav-actions">
            <LanguageSwitcher />
            <div className="user-name">
              {localStorage.getItem('user_name') || 'User'}
            </div>
            <button
              className="logout-btn"
              onClick={() => setShowLogoutModal(true)}
            >
              {t('nav.logout')}
            </button>
          </div>
        </nav>
      </header>

      {showLogoutModal && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0,0,0,0.6)' }}>
          <div style={{ backgroundColor: 'var(--nebula-bg-raised)', padding: '20px', borderRadius: '12px', border: '1px solid var(--nebula-border)', boxShadow: 'var(--nebula-shadow-2)', color: 'var(--nebula-text)', minWidth: '280px' }}>
            <h3 style={{ marginBottom: '15px' }}>{t('nav.logout_confirm', 'Select an action')}</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <button onClick={performLogout} style={{ padding: '8px 16px', backgroundColor: 'var(--nebula-danger)', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}>
                {t('nav.logout', 'Logout')}
              </button>
              <button onClick={handleGoToHub} style={{ padding: '8px 16px', backgroundColor: 'var(--nebula-accent-cyan)', color: 'var(--nebula-bg-deep)', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}>
                {t('nav.back_to_hub', 'Back to Hub')}
              </button>
              <button onClick={() => setShowLogoutModal(false)} style={{ padding: '8px 16px', backgroundColor: 'transparent', color: 'var(--nebula-text)', border: '1px solid var(--nebula-border)', borderRadius: '6px', cursor: 'pointer' }}>
                {t('common.cancel', 'Cancel')}
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="app-main">
        <Outlet />
      </main>

      <footer className="app-footer">
        {t('footer.copyright', '© 2026 Q-Bank Platform. All rights reserved.')} | {t(footerModuleKey, footerModuleFallback)}
      </footer>
    </div>
  );
};

export default Layout;
