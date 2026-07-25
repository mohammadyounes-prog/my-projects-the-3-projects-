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
      className={isRtl ? 'rtl-layout nebula-motion-page' : 'ltr-layout nebula-motion-page'}
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: 'var(--nebula-font-body)',
        backgroundColor: 'var(--nebula-bg-deep)',
        background: 'var(--nebula-gradient-hero)',
        color: 'var(--nebula-text)'
      }}
    >
      <header
        style={{
          display: 'flex',
          justifyContent: 'flex-end',
          alignItems: 'center',
          paddingBlock: 'var(--nebula-space-3)',
          paddingInline: 'var(--nebula-space-5)',
        }}
      >
        <LanguageSwitcher />
      </header>

      <div
        className="nebula-glass-card nebula-motion-card"
        style={{
          maxWidth: '400px',
          width: '100%',
          marginBlock: '1.5rem',
          marginInline: 'auto',
          padding: 'var(--nebula-space-5)',
          textAlign: 'start',
        }}
      >
        <h1
          style={{
            fontFamily: 'var(--nebula-font-display)',
            color: 'var(--nebula-accent-cyan)',
            marginTop: 0,
            textShadow: 'var(--nebula-glow-cyan-sm)',
            textAlign: 'center'
          }}
        >
          {t('login.title', 'Login')}
        </h1>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nebula-space-4)' }}>
          <div>
            <label htmlFor="login-username" style={{ color: 'var(--nebula-text-muted)', fontSize: '0.9rem', marginBottom: '8px', display: 'block' }}>{t('login.username', 'Username/Email')}</label>
            <input
              id="login-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '12px',
                borderRadius: 'var(--nebula-radius-sm)',
                border: '1px solid var(--nebula-border)',
                backgroundColor: 'var(--nebula-bg-input)',
                color: 'var(--nebula-text)',
                fontFamily: 'var(--nebula-font-body)',
                outline: 'none',
                transition: 'border-color var(--nebula-duration-fast), box-shadow var(--nebula-duration-fast)'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--nebula-accent-cyan)';
                e.target.style.boxShadow = 'var(--nebula-glow-cyan-sm)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--nebula-border)';
                e.target.style.boxShadow = 'none';
              }}
              required
            />
          </div>
          <div>
            <label htmlFor="login-password" style={{ color: 'var(--nebula-text-muted)', fontSize: '0.9rem', marginBottom: '8px', display: 'block' }}>{t('login.password', 'Password')}</label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '12px',
                borderRadius: 'var(--nebula-radius-sm)',
                border: '1px solid var(--nebula-border)',
                backgroundColor: 'var(--nebula-bg-input)',
                color: 'var(--nebula-text)',
                fontFamily: 'var(--nebula-font-body)',
                outline: 'none',
                transition: 'border-color var(--nebula-duration-fast), box-shadow var(--nebula-duration-fast)'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--nebula-accent-cyan)';
                e.target.style.boxShadow = 'var(--nebula-glow-cyan-sm)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--nebula-border)';
                e.target.style.boxShadow = 'none';
              }}
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px',
              background: 'var(--nebula-gradient-btn)',
              color: 'var(--nebula-on-accent)',
              border: 'none',
              borderRadius: 'var(--nebula-radius-sm)',
              fontFamily: 'var(--nebula-font-body)',
              fontWeight: 700,
              cursor: loading ? 'wait' : 'pointer',
              marginTop: '8px',
              transition: 'transform var(--nebula-duration-fast), box-shadow var(--nebula-duration-fast)',
              boxShadow: 'var(--nebula-glow-cyan-sm)'
            }}
            onMouseOver={(e) => {
              if(!loading) e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseOut={(e) => {
              if(!loading) e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            {loading ? t('common.loading', 'Loading...') : t('login.login_button', 'Login')}
          </button>
        </form>
        {error && (
          <p style={{ color: 'var(--nebula-danger)', marginTop: '15px', textAlign: 'center' }}>{error}</p>
        )}
      </div>
    </div>
  );
};

export default LoginPage;
