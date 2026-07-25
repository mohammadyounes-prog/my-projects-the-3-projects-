import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../components/LanguageSwitcher.tsx';

declare var process: any;

const LoginPage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (localStorage.getItem('token')) {
      navigate('/');
    }
  }, [navigate]);

  useEffect(() => {
    const dir = i18n.dir();
    document.documentElement.dir = dir;
    document.documentElement.lang = i18n.language?.startsWith('ar') ? 'ar' : 'en';
    document.body.className = dir;
  }, [i18n, i18n.language]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/auth/login`, formData);

      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('role', response.data.role);
      localStorage.setItem('user_name', response.data.name);

      navigate('/');
    } catch (err: any) {
      setError(t('login.error', 'Invalid username or password'));
      setLoading(false);
    }
  };

  const isRtl = i18n.dir() === 'rtl';

  return (
    <div
      dir={i18n.dir()}
      className={isRtl ? 'rtl-layout' : 'ltr-layout'}
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: 'var(--font-body)',
        backgroundColor: 'var(--color-bg-app, var(--suite-surface, #f8fafc))',
      }}
    >
      <header
        style={{
          display: 'flex',
          justifyContent: 'flex-end',
          alignItems: 'center',
          paddingBlock: 'var(--space-md, 1rem)',
          paddingInline: 'var(--space-lg, 1.5rem)',
        }}
      >
        <LanguageSwitcher />
      </header>

      <div
        style={{
          maxWidth: '400px',
          width: '100%',
          marginBlock: '1.5rem',
          marginInline: 'auto',
          padding: 'var(--space-lg, 1.5rem)',
          border: '1px solid var(--suite-border, #ddd)',
          borderRadius: 'var(--suite-radius-md, 8px)',
          backgroundColor: 'var(--suite-surface-raised, #fff)',
          boxShadow: 'var(--suite-shadow-1)',
          textAlign: 'start',
        }}
      >
        <h1
          style={{
            fontFamily: 'var(--font-display)',
            color: 'var(--suite-primary, #2c5282)',
            marginTop: 0,
          }}
        >
          {t('login.title', 'Login')}
        </h1>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '15px' }}>
            <label htmlFor="login-username">{t('login.username', 'Username/Email')}</label>
            <input
              id="login-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '8px',
                marginTop: '5px',
                borderRadius: 'var(--suite-radius-sm, 4px)',
                border: '1px solid var(--suite-border, #ccc)',
                fontFamily: 'var(--font-body)',
              }}
              required
            />
          </div>
          <div style={{ marginBottom: '15px' }}>
            <label htmlFor="login-password">{t('login.password', 'Password')}</label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '8px',
                marginTop: '5px',
                borderRadius: 'var(--suite-radius-sm, 4px)',
                border: '1px solid var(--suite-border, #ccc)',
                fontFamily: 'var(--font-body)',
              }}
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: 'var(--suite-primary, #2c5282)',
              color: 'var(--suite-on-primary, #fff)',
              border: 'none',
              borderRadius: 'var(--suite-radius-sm, 4px)',
              fontFamily: 'var(--font-body)',
              fontWeight: 600,
              cursor: loading ? 'wait' : 'pointer',
            }}
          >
            {loading ? t('common.loading', 'Loading...') : t('login.login_button', 'Login')}
          </button>
        </form>
        {error && (
          <p style={{ color: 'var(--suite-danger, #dc2626)', marginTop: '15px' }}>{error}</p>
        )}
      </div>
    </div>
  );
};

export default LoginPage;
