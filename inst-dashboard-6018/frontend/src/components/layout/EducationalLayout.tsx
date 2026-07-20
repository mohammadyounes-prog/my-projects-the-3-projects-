import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../LanguageSwitcher.tsx'; 

const EducationalLayout = () => {
  const { t } = useTranslation();
  const location = useLocation();

  return (
    <div>
      <div style={{ display: 'flex', gap: '30px', padding: '15px 0', borderBottom: '2px solid #eee', marginBottom: '30px' }}>
        <NavLink to="/educational/admins" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#1e3a8a' : '#666', fontWeight: isActive ? 'bold' : 'normal', fontSize: '1.25rem' })}>
          {t('educational.admins')}
        </NavLink>
        <NavLink to="/educational/instructors" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#1e3a8a' : '#666', fontWeight: isActive ? 'bold' : 'normal', fontSize: '1.25rem' })}>
          {t('educational.instructors')}
        </NavLink>
      </div>
      <Outlet key={location.pathname} />
    </div>
  );
};

export default EducationalLayout;
