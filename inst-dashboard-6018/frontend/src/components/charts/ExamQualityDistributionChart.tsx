import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { useTranslation } from 'react-i18next';
import HelpTooltip from '../common/HelpTooltip.tsx';

interface Props {
  data: any[];
}

const ExamQualityDistributionChart: React.FC<Props> = ({ data }) => {
  const { t } = useTranslation();

  // Data mapping: difficulty vs discrimination
  const chartData = data.map(item => ({
    name: item.exam,
    difficulty: item.difficulty * 100,
    discrimination: item.discrimination * 100
  }));

  return (
    <div style={{ width: '100%', height: '400px', backgroundColor: '#fff', padding: '20px', borderRadius: '12px', border: '1px solid #e0e0e0' }}>
      <h3 style={{ textAlign: 'center', marginBottom: '10px' }}>
        {t('dashboard.exam_quality_dist', 'Exam Quality Matrix')}
        <HelpTooltip 
          title={t('dashboard.exam_quality_dist', 'Exam Quality Matrix')} 
          description={t('dashboard.exam_quality_dist_desc', 'Plots exam difficulty against discrimination power.')} 
          benefit={t('dashboard.exam_quality_dist_benefit', 'Helps identify low-quality assessments that need review for better student differentiation.')}
        />
      </h3>
      <div style={{ width: '100%', height: 300, minWidth: 0, minHeight: 200 }}>
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" dataKey="difficulty" name="Difficulty" unit="%" label={{ value: 'Difficulty', position: 'bottom' }} />
            <YAxis type="number" dataKey="discrimination" name="Discrimination" unit="%" label={{ value: 'Discrimination', angle: -90, position: 'insideLeft' }} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter name="Exams" data={chartData} fill="#8884d8">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.discrimination > 20 ? '#52c41a' : '#f5222d'} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ExamQualityDistributionChart;
