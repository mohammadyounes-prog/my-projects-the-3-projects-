import React from 'react';
import { useTranslation } from 'react-i18next';
import HelpTooltip from '../common/HelpTooltip.tsx';

interface Props {
  value?: number;
  trend?: string;
  loading?: boolean;
}

const InstitutionalPassRate: React.FC<Props> = ({ value = 0, trend = "↑ 0%", loading = false }) => {
  const { t } = useTranslation();

  const getHealthColor = (val: number) => {
    if (val === 0) return '#cbd5e1';
    if (val >= 80) return '#10b981';
    if (val >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const healthColor = getHealthColor(value);
  const target = 80;
  const gap = value - target;

  return (
    <div style={{ 
      border: `1px solid ${healthColor}`, 
      boxShadow: '0 4px 15px rgba(0, 0, 0, 0.05)', 
      borderRadius: '1rem', 
      padding: '24px', 
      width: '100%',
      boxSizing: 'border-box',
      backgroundColor: '#ffffff', 
      textAlign: 'center',
      color: '#1e293b',
      transition: 'all 0.2s ease',
      cursor: 'pointer',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      gap: '12px'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
      e.currentTarget.style.boxShadow = `0 10px 25px rgba(0, 0, 0, 0.08)`;
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.05)';
    }}>
      <h3 style={{ fontSize: '0.875rem', color: '#2c5282', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', margin: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontFamily: '"Space Grotesk", sans-serif' }}>
        <span>🎓</span> {t('dashboard.pass_rate')}
        <HelpTooltip 
          title={t('dashboard.pass_rate_title', 'Pass Rate')} 
          description={t('dashboard.pass_rate_desc', 'Percentage of students meeting the success threshold in assessments.')} 
          benefit={t('dashboard.pass_rate_benefit', 'Tracks institutional teaching effectiveness and student success trends.')}
        />
      </h3>
      <p style={{ fontSize: '2.5rem', fontWeight: '800', margin: '4px 0', color: healthColor, fontFamily: '"Space Grotesk", sans-serif' }}>
        {loading ? t('common.loading') : `${value}%`}
      </p>

      <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '500' }}>
        Target: {target}% | <span style={{ color: gap >= 0 ? '#10b981' : '#ef4444', fontWeight: '700' }}>
          {gap >= 0 ? '+' : ''}{gap}%
        </span>
      </div>

      <div style={{ 
        display: 'inline-block',
        padding: '4px 12px',
        borderRadius: '20px',
        backgroundColor: trend.startsWith('↑') ? '#ecfdf5' : '#fef2f2',
        color: trend.startsWith('↑') ? '#10b981' : '#ef4444',
        fontWeight: '700',
        fontSize: '0.8rem',
        alignSelf: 'center'
      }}>
        {trend}
      </div>
    </div>
  );
};

export default InstitutionalPassRate;
