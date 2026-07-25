import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTranslation } from 'react-i18next';
import HelpTooltip from '../common/HelpTooltip.tsx';

interface Props {
  data: any[];
}

const PassRateTrendChart: React.FC<Props> = ({ data }) => {
  const { t } = useTranslation();

  return (
    <div style={{ width: '100%', height: '400px', backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e0e0e0' }}>
      <h3 style={{ textAlign: 'center', marginBottom: '10px' }}>
        {t('dashboard.pass_rate_trend', 'Pass Rate Trend')}
        <HelpTooltip 
          title={t('dashboard.pass_rate_trend', 'Pass Rate Trend')} 
          description={t('dashboard.pass_rate_trend_desc', 'Visualizes historical pass rate progression.')} 
          benefit={t('dashboard.pass_rate_trend_benefit', 'Enables long-term monitoring of assessment difficulty and student success.')}
        />
      </h3>
      <div style={{ width: '100%', height: 300, minWidth: 0, minHeight: 200 }}>
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Line type="monotone" dataKey="attainment" stroke="#faad14" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default PassRateTrendChart;
