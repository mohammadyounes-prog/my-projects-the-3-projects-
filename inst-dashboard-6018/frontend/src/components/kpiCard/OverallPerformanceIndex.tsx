import React from 'react';
import { useTranslation } from 'react-i18next';
import HelpTooltip from '../common/HelpTooltip.tsx';

interface Props {
  value?: number;
  trend?: string;
  loading?: boolean;
  insight?: string;
  breakdown?: { academic: number; operational: number; quality: number };
}

const OverallPerformanceIndex: React.FC<Props> = ({ 
  value = 0, 
  trend = "↑ 0%", 
  loading = false, 
  insight = "", 
  breakdown = { academic: 0, operational: 0, quality: 0 } 
}) => {
  const { t } = useTranslation();
  
  const getHealthColor = (val: number) => {
    if (val === 0) return '#cbd5e1';
    if (val >= 80) return 'var(--nebula-success)';
    if (val >= 60) return 'var(--nebula-warning)';
    return 'var(--nebula-danger)';
  };

  const healthColor = getHealthColor(value);
  const target = 85;
  const gap = value - target;

  const renderProgressBar = (label: string, val: number) => (
    <div className="kpi-card nebula-glass-card nebula-glow-border" style={{ marginBottom: '8px', textAlign: 'left' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75em', color: 'var(--nebula-text-muted)' }}>
        <span>{label}</span>
        <span>{val}%</span>
      </div>
      <div style={{ width: '100%', height: '6px', backgroundColor: '#f0f0f0', borderRadius: '3px' }}>
        <div style={{ width: `${val}%`, height: '100%', backgroundColor: getHealthColor(val), borderRadius: '3px' }} />
      </div>
    </div>
  );

  return (
    <div style={{ 
      border: `1px solid ${healthColor}`, 
      boxShadow: '0 4px 15px rgba(0, 0, 0, 0.05)', 
      borderRadius: '1rem', 
      padding: '24px', 
      width: '100%',
      boxSizing: 'border-box',
       
      textAlign: 'center',
      color: 'var(--nebula-text)',
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
      <h3 style={{ fontSize: '0.875rem', color: 'var(--nebula-accent-cyan)', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', margin: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontFamily: 'var(--nebula-font-display), sans-serif' }}>
        <span>🏆</span> {t('dashboard.performance_index')}
        <HelpTooltip 
          title={t('dashboard.performance_index_title', 'Overall Performance Index')} 
          description={t('dashboard.performance_index_desc', 'A weighted composite of Academic, Operational, and Quality metrics.')} 
          benefit={t('dashboard.performance_index_benefit', 'Quickly assess the institutional pulse and identify systemic performance gaps.')}
        />
      </h3>
      <p style={{ fontSize: '2.5rem', fontWeight: '800', margin: '4px 0', color: healthColor, fontFamily: 'var(--nebula-font-display), sans-serif' }}>
        {loading ? t('common.loading') : `${value}%`}
      </p>
      
      {/* Sub-Score Drill-Down */}
      <div style={{ margin: '8px 0' }}>
        {renderProgressBar(t('dashboard.academic', 'Academic'), breakdown.academic)}
        {renderProgressBar(t('dashboard.operational', 'Operational'), breakdown.operational)}
        {renderProgressBar(t('dashboard.quality', 'Quality'), breakdown.quality)}
      </div>

      {/* Gap to Target Indicator */}
      <div style={{ fontSize: '0.8rem', color: 'var(--nebula-text-muted)', fontWeight: '500' }}>
        Target: {target}% | <span style={{ color: gap >= 0 ? 'var(--nebula-success)' : 'var(--nebula-danger)', fontWeight: '700' }}>
          {gap >= 0 ? '+' : ''}{gap}%
        </span>
      </div>

      {/* Actionable Insight */}
      {insight && (
        <div style={{ fontSize: '0.75rem', backgroundColor: '#f0f9ff', color: '#0369a1', padding: '8px 12px', borderRadius: '0.5rem', border: '1px solid #bae6fd', textAlign: 'left' }}>
          <strong>{t('dashboard.insight', 'Insight:')}</strong> {insight}
        </div>
      )}

      <div style={{ 
        display: 'inline-block',
        padding: '4px 12px',
        borderRadius: '20px',
        backgroundColor: trend.startsWith('↑') ? 'var(--nebula-success-dim)' : 'var(--nebula-danger-dim)',
        color: trend.startsWith('↑') ? 'var(--nebula-success)' : 'var(--nebula-danger)',
        fontWeight: '700',
        fontSize: '0.8rem',
        alignSelf: 'center'
      }}>
        {trend}
      </div>
    </div>
  );
};

export default OverallPerformanceIndex;
