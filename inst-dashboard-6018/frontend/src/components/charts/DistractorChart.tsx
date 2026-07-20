import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { useTranslation } from 'react-i18next';
import HelpTooltip from '../common/HelpTooltip.tsx';

interface Props {
  data: { option: string; text: string; count: number }[];
}

const DistractorChart: React.FC<Props> = ({ data }) => {
  const { t } = useTranslation();

  // Helper to clean HTML/LaTeX from strings
  const cleanText = (text: string) => {
    return text.replace(/<[^>]*>?/gm, '').replace(/&nbsp;/g, ' ').trim();
  };

  // Ensure we always have A, B, C, D even if count is 0
  const allOptions = ['1', '2', '3', '4'];
  const formattedData = allOptions.map(opt => {
    const item = data.find(d => d.option === opt);
    return {
      option: opt,
      count: item ? item.count : 0,
      text: item ? cleanText(item.text) : t('common.no_data', 'No Data'),
      label: opt === '1' ? 'A' : opt === '2' ? 'B' : opt === '3' ? 'C' : opt === '4' ? 'D' : opt
    };
  });

  return (
    <div style={{ width: '100%', height: '300px', padding: '10px', background: '#fff', borderRadius: '8px', border: '1px solid #f0f0f0' }}>
      <h3 style={{ textAlign: 'center' }}>
        {t('translation:dashboard.distractor_analysis')}
        <HelpTooltip 
          title={t('translation:dashboard.distractor_analysis_title', 'Distractor Analysis')} 
          description={t('translation:dashboard.distractor_analysis_desc', 'Shows the frequency of incorrect options selected by students.')} 
          benefit={t('translation:dashboard.distractor_analysis_benefit', 'Helps identify poor quality distractors or common student misconceptions.')}
        />
      </h3>
      <ResponsiveContainer>
        <BarChart data={formattedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" />
          <YAxis allowDecimals={false} />
          {/* Tooltip uses the cleaned text */}
          <Tooltip content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload;
              return (
                <div style={{ background: '#fff', padding: '10px', border: '1px solid #ccc', fontSize: '12px' }}>
                  <p>{`Option ${data.label}: ${data.text}`}</p>
                  <p>{`Count: ${data.count}`}</p>
                </div>
              );
            }
            return null;
          }} />
          <Bar dataKey="count" fill="#ff4d4f">
            {formattedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#ff7875' : '#ff4d4f'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DistractorChart;
