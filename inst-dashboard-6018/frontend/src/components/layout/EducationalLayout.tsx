import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher.tsx'; 

const EducationalLayout = () => {
  const { t } = useTranslation();
  const location = useLocation();

  return (
    <div className="dashboard-container suite-motion-page" style={{ padding: '24px 20px 40px', maxWidth: '1400px', margin: '0 auto', boxSizing: 'border-box' }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        gap: '12px', 
        padding: '6px', 
        backgroundColor: '#ffffff', 
        border: '1px solid rgba(0, 0, 0, 0.08)', 
        borderRadius: '0.75rem', 
        marginBottom: '28px',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.04)',
        maxWidth: '320px'
      }}>
        <NavLink 
          to="/educational/admins" 
          style={({ isActive }) => ({ 
            textDecoration: 'none', 
            color: isActive ? 'var(--suite-on-primary)' : 'var(--suite-text-muted)', 
            backgroundColor: isActive ? 'var(--suite-primary)' : 'transparent',
            fontWeight: '600', 
            fontSize: '0.9rem',
            fontFamily: 'var(--font-display)',
            padding: '8px 18px',
            borderRadius: 'var(--suite-radius-sm)',
            transition: 'all 0.2s ease',
            textAlign: 'center',
            flex: 1
          })}
        >
          {t('educational.admins', 'Admins')}
        </NavLink>
        <NavLink 
          to="/educational/instructors" 
          style={({ isActive }) => ({ 
            textDecoration: 'none', 
            color: isActive ? 'var(--suite-on-primary)' : 'var(--suite-text-muted)', 
            backgroundColor: isActive ? 'var(--suite-primary)' : 'transparent',
            fontWeight: '600', 
            fontSize: '0.9rem',
            fontFamily: 'var(--font-display)',
            padding: '8px 18px',
            borderRadius: 'var(--suite-radius-sm)',
            transition: 'all 0.2s ease',
            textAlign: 'center',
            flex: 1
          })}
        >
          {t('educational.instructors', 'Instructors')}
        </NavLink>
      </div>
      <Outlet key={location.pathname} />
    </div>
  );
};

export default EducationalLayout;
