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
    if (val >= 75) return '#52c41a';
    if (val >= 50) return '#faad14';
    return '#f5222d';
  };

  const healthColor = getHealthColor(value);
  const target = 85;
  const gap = value - target;

  const renderProgressBar = (label: string, val: number) => (
    <div style={{ marginBottom: '8px', textAlign: 'left' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75em', color: '#666' }}>
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
      boxShadow: '0 4px 6px rgba(0,0,0,0.05)', 
      borderRadius: '12px', 
      padding: '24px', 
      margin: '15px', 
      width: '280px',
      backgroundColor: '#ffffff', 
      textAlign: 'center',
      color: '#333',
      transition: 'transform 0.3s ease, box-shadow 0.3s ease',
      cursor: 'pointer'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-5px)';
      e.currentTarget.style.boxShadow = `0 8px 16px ${healthColor}33`;
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.05)';
    }}>
      <h3 style={{ fontSize: '1.2em', color: '#0050b3', fontWeight: '700', textTransform: 'uppercase', marginBottom: '10px' }}>
        {t('dashboard.performance_index')}
        <HelpTooltip 
          title={t('dashboard.performance_index_title', 'Overall Performance Index')} 
          description={t('dashboard.performance_index_desc', 'A weighted composite of Academic, Operational, and Quality metrics.')} 
          benefit={t('dashboard.performance_index_benefit', 'Quickly assess the institutional pulse and identify systemic performance gaps.')}
        />
      </h3>
      <p style={{ fontSize: '2.5em', fontWeight: '700', margin: '10px 0', color: healthColor }}>
        {loading ? t('common.loading') : `${value}%`}
      </p>
      
      {/* Sub-Score Drill-Down */}
      <div style={{ margin: '15px 0' }}>
        {renderProgressBar(t('dashboard.academic', 'Academic'), breakdown.academic)}
        {renderProgressBar(t('dashboard.operational', 'Operational'), breakdown.operational)}
        {renderProgressBar(t('dashboard.quality', 'Quality'), breakdown.quality)}
      </div>

      {/* Gap to Target Indicator */}
      <div style={{ fontSize: '0.85em', color: '#666', marginBottom: '10px' }}>
        Target: {target}% | <span style={{ color: gap >= 0 ? '#52c41a' : '#f5222d' }}>
          {gap >= 0 ? '+' : ''}{gap}%
        </span>
      </div>

      {/* Actionable Insight */}
      {insight && (
        <div style={{ fontSize: '0.85em', backgroundColor: '#f0f7ff', color: '#0050b3', padding: '8px', borderRadius: '6px', marginBottom: '15px' }}>
          <strong>{t('dashboard.insight', 'Insight:')}</strong> {insight}
        </div>
      )}

      <div style={{ 
        display: 'inline-block',
        padding: '4px 12px',
        borderRadius: '20px',
        backgroundColor: trend.startsWith('↑') ? '#f6ffed' : '#fff1f0',
        color: trend.startsWith('↑') ? '#52c41a' : '#f5222d',
        fontWeight: '600',
        fontSize: '0.9em'
      }}>
        {trend}
      </div>
    </div>
  );
};

export default OverallPerformanceIndex;
