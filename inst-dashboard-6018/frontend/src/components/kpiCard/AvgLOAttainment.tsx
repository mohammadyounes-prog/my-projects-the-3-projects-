import React from 'react';
import { useTranslation } from 'react-i18next';
import HelpTooltip from '../common/HelpTooltip.tsx';

interface Props {
  value?: number;
  trend?: string;
  loading?: boolean;
}

const AvgLOAttainment: React.FC<Props> = ({ value = 0, trend = "↑ 0%", loading = false }) => {
  const { t } = useTranslation();

  const getHealthColor = (val: number) => {
    if (val >= 75) return '#52c41a';
    if (val >= 50) return '#faad14';
    return '#f5222d';
  };

  const healthColor = getHealthColor(value);
  const target = 75; // Academic benchmark
  const gap = value - target;

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
      cursor: 'pointer',
      overflow: 'visible'
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
        {t('dashboard.average_lo_attainment')}
        <HelpTooltip 
          title={t('dashboard.lo_attainment_title', 'LO Attainment')} 
          description={t('dashboard.lo_attainment_desc', 'Average success rate across all defined Learning Outcomes.')} 
          benefit={t('dashboard.lo_attainment_benefit', 'Identifies which curriculum areas require pedagogical adjustments.')}
        />
      </h3>
      <p style={{ fontSize: '2.5em', fontWeight: '700', margin: '10px 0', color: healthColor }}>
        {loading ? t('common.loading') : `${value}%`}
      </p>

      <div style={{ fontSize: '0.85em', color: '#666', marginBottom: '15px' }}>
        Target: {target}% | <span style={{ color: gap >= 0 ? '#52c41a' : '#f5222d' }}>
          {gap >= 0 ? '+' : ''}{gap}%
        </span>
      </div>

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

export default AvgLOAttainment;
