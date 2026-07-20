import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher.tsx'; 
import { Link } from 'react-router-dom';
import './Layout.css'; 

const Layout = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
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
    window.location.href = 'http://localhost:3700'; // Assuming this is the Hub URL
  };

  const isRtl = i18n.dir() === 'rtl';

  return (
    <div dir={i18n.dir()} className={isRtl ? 'rtl-layout' : 'ltr-layout'} style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}> 
      <header className="app-header">
        <nav className="app-nav">
          <div className="app-brand">
            <span className="brand-line-1">Testing and Assessment</span>
            <span className="brand-line-2">&nbsp;&nbsp;&nbsp;&nbsp;Management Solution</span>
          </div>

          <div className="nav-links">
            <Link to="/">{t('nav.home', 'Home')}</Link>
            <Link to="/educational/admins">{t('nav.dashboard')}</Link>
            <Link to="/executive-dashboard">{t('nav.executive')}</Link>
            <Link to="/corporate-dashboard">{t('nav.corporate')}</Link>
            <Link to="/weights">{t('nav.indexes_weight')}</Link>
            <Link to="/settings">{t('nav.settings')}</Link>
            <Link to="/contact">{t('nav.contact', 'Contact Us')}</Link>
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
        {t('footer.copyright', '© 2026 Q-Bank Platform. All rights reserved.')} | {t('footer.module', 'Corporate HR Intelligence Module')}
      </footer>
    </div>
  );
};

export default Layout;
