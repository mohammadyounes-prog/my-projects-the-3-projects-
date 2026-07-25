import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher.tsx'; 

const EducationalLayout = () => {
  const { t } = useTranslation();
  const location = useLocation();

  return (
    <div className="dashboard-container nebula-motion-page" style={{ padding: '24px 20px 40px', maxWidth: '1400px', margin: '0 auto', boxSizing: 'border-box' }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        gap: '12px', 
        padding: '6px', 
        backgroundColor: 'var(--nebula-bg-glass)',
        backdropFilter: 'blur(12px)',
        border: '1px solid var(--nebula-border)', 
        borderRadius: '0.75rem', 
        marginBottom: '28px',
        boxShadow: 'var(--nebula-shadow-glass)',
        maxWidth: '320px'
      }}>
        <NavLink 
          to="/educational/admins" 
          style={({ isActive }) => ({ 
            textDecoration: 'none', 
            color: isActive ? 'var(--nebula-accent-cyan)' : 'var(--nebula-text-muted)', 
            backgroundColor: isActive ? 'var(--nebula-accent-cyan-dim)' : 'transparent',
            fontWeight: '600', 
            fontSize: '0.9rem',
            fontFamily: 'var(--nebula-font-display)',
            padding: '8px 18px',
            borderRadius: 'var(--nebula-radius-sm)',
            transition: 'all 0.2s ease',
            textAlign: 'center',
            flex: 1,
            border: isActive ? '1px solid var(--nebula-accent-cyan)' : '1px solid transparent',
            boxShadow: isActive ? 'inset 0 -2px 0 var(--nebula-accent-cyan)' : 'none'
          })}
        >
          {t('educational.admins', 'Admins')}
        </NavLink>
        <NavLink 
          to="/educational/instructors" 
          style={({ isActive }) => ({ 
            textDecoration: 'none', 
            color: isActive ? 'var(--nebula-accent-cyan)' : 'var(--nebula-text-muted)', 
            backgroundColor: isActive ? 'var(--nebula-accent-cyan-dim)' : 'transparent',
            fontWeight: '600', 
            fontSize: '0.9rem',
            fontFamily: 'var(--nebula-font-display)',
            padding: '8px 18px',
            borderRadius: 'var(--nebula-radius-sm)',
            transition: 'all 0.2s ease',
            textAlign: 'center',
            flex: 1,
            border: isActive ? '1px solid var(--nebula-accent-cyan)' : '1px solid transparent',
            boxShadow: isActive ? 'inset 0 -2px 0 var(--nebula-accent-cyan)' : 'none'
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
