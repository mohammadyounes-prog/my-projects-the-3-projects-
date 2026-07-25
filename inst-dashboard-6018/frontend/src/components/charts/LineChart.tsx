import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import HelpTooltip from '../common/HelpTooltip.tsx';

interface DataPoint {
  date: string;
  attainment: number;
}

interface Props {
  data?: DataPoint[];
  loading?: boolean;
}

const LineChart: React.FC<Props> = ({ data = [], loading = false }) => {
  const { t } = useTranslation();

  if (loading) {
    return (
      <div style={{ width: '100%', height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--nebula-border)' }}>
        <p>Loading trend data...</p>
      </div>
    );
  }

  return (
    <div style={{
      border: '1px solid rgba(148,163,184,0.1)',
      boxShadow: '0 2px 4px var(--nebula-border-strong)',
      borderRadius: '8px',
      padding: '20px',
      width: '100%',
      boxSizing: 'border-box',
      backgroundColor: 'var(--nebula-bg-glass)'
    }}>
      <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>
        {t('dashboard.lo_attainment_trend', 'LO Attainment Trend')}
        <HelpTooltip 
          title={t('dashboard.performance_trends', 'Performance Trends')} 
          description={t('dashboard.trend_desc', 'Visualizes KPI performance over time.')} 
          benefit={t('dashboard.trend_benefit', 'Helps managers identify if institutional initiatives are yielding long-term improvements.')}
        />
      </h3>
      <div style={{ width: '100%', height: '250px', minWidth: '200px', minHeight: '200px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsLineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--nebula-border)" />
            <XAxis 
              dataKey="date" 
              fontSize={12} 
              tick={{ fill: 'var(--nebula-text-muted)' }}
              tickLine={{ stroke: 'var(--nebula-border)' }}
            />
            <YAxis 
              domain={[0, 100]} 
              fontSize={12} 
              tick={{ fill: 'var(--nebula-text-muted)' }}
              tickLine={{ stroke: 'var(--nebula-border)' }}
              unit="%"
            />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--nebula-bg-glass)', border: '1px solid var(--nebula-border)', borderRadius: '4px' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="attainment" 
              name="Avg Attainment %" 
              stroke="var(--nebula-accent-cyan)" 
              strokeWidth={3}
              dot={{ r: 4, fill: 'var(--nebula-accent-cyan)', strokeWidth: 2, stroke: 'var(--nebula-bg-glass)' }}
              activeDot={{ r: 6 }}
            />
          </RechartsLineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default LineChart;
