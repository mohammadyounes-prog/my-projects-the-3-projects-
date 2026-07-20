import React from 'react';
import { useTranslation } from 'react-i18next';
import HelpTooltip from '../common/HelpTooltip.tsx';

interface Props {
  value?: number;
  trend?: string;
  loading?: boolean;
}

const QuestionBankHealth: React.FC<Props> = ({ value = 0, trend = "↑ 0%", loading = false }) => {
  const { t } = useTranslation();

  const getHealthColor = (val: number) => {
    if (val >= 80) return '#52c41a';
    if (val >= 60) return '#faad14';
    return '#f5222d';
  };

  const healthColor = getHealthColor(value);
  const target = 80;
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
        {t('dashboard.question_bank_health', 'Question Bank Health')}
        <HelpTooltip 
          title={t('dashboard.bank_health_title', 'Question Bank Health')} 
          description={t('dashboard.bank_health_desc', 'Percentage of learning outcomes adequately covered by the question bank.')} 
          benefit={t('dashboard.bank_health_benefit', 'Ensures test validity by confirming all curriculum areas are properly assessed.')}
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

export default QuestionBankHealth;
