import React from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Tooltip } from 'recharts';
import { useTranslation } from 'react-i18next';
import InfoIcon from '../components/InfoIcon.tsx';

interface Props {
  data: any;
}

const KPIRadarChart = ({ data }: Props) => {
  const { t } = useTranslation();

  if (!data) return null;

  const chartData = [
    { subject: t('dashboard.lo_attainment_title'), actual: data.avg_lo_attainment?.value || 0, target: data.avg_lo_attainment?.target || 90 },
    { subject: t('dashboard.pass_rate_title'), actual: data.pass_rate?.value || 0, target: data.pass_rate?.target || 90 },
    { subject: t('dashboard.exam_quality_title'), actual: data.exam_quality_index?.value || 0, target: data.exam_quality_index?.target || 90 },
    { subject: t('dashboard.question_bank_health'), actual: data.question_bank_health?.value || 0, target: data.question_bank_health?.target || 100 },
  ];

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px', background: '#fff' }}>
      <h3 style={{ display: 'flex', alignItems: 'center' }}>
        {t('radar.title')}
        <InfoIcon 
          desc={t('radar.desc')} 
          benefit={t('radar.benefit')} 
        />
      </h3>
      <div style={{ height: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Radar name={t('radar.actual')} dataKey="actual" stroke="#1677ff" fill="#1677ff" fillOpacity={0.6} />
            <Radar name={t('radar.target')} dataKey="target" stroke="#52c41a" fill="#52c41a" fillOpacity={0.1} strokeDasharray="5 5" />
            <Legend />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default KPIRadarChart;
