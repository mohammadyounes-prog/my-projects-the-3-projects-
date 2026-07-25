import React, { useEffect, useMemo, useState } from 'react';
import { Outlet, useLocation, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher.tsx';
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

  /** Gateway: Home only. Module pages: primary module links (no Contact — B6). */
  const navItems: NavItem[] = useMemo(() => {
    const home: NavItem = { to: '/', labelKey: 'nav.home', fallback: 'Home' };
    if (isGateway) {
      return [home];
    }
    return [
      home,
      { to: '/educational/admins', labelKey: 'nav.dashboard', fallback: 'Educational' },
      { to: '/executive-dashboard', labelKey: 'nav.executive', fallback: 'Executive' },
      { to: '/corporate-dashboard', labelKey: 'nav.corporate', fallback: 'Corporate' },
      { to: '/weights', labelKey: 'nav.indexes_weight', fallback: 'Indexes Weight' },
      { to: '/settings', labelKey: 'nav.settings', fallback: 'Settings' },
    ];
  }, [isGateway]);

  return (
    <div dir={i18n.dir()} className={isRtl ? 'rtl-layout' : 'ltr-layout'} style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header className="app-header">
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
        <div style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', color: 'black' }}>
            <h3 style={{ marginBottom: '15px' }}>{t('nav.logout_confirm', 'Select an action')}</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <button onClick={performLogout} style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                {t('nav.logout', 'Logout')}
              </button>
              <button onClick={handleGoToHub} style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                {t('nav.back_to_hub', 'Back to Hub')}
              </button>
              <button onClick={() => setShowLogoutModal(false)} style={{ padding: '8px 16px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
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
