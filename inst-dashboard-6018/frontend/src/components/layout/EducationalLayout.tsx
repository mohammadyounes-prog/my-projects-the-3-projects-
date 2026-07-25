import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher.tsx'; 

const EducationalLayout = () => {
  const { t } = useTranslation();
  const location = useLocation();

  return (
    <div className="dashboard-container suite-motion-page">
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        gap: '12px', 
        padding: '8px', 
        backgroundColor: 'var(--suite-surface-raised)', 
        border: '1px solid var(--suite-border)', 
        borderRadius: 'var(--suite-radius-md)', 
        marginBottom: '28px',
        boxShadow: 'var(--suite-shadow-1)',
        maxWidth: '360px'
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
