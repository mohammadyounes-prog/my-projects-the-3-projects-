import React from 'react';
import { ResponsiveContainer, HeatMap, XAxis, YAxis, Tooltip, Cell, ZAxis, ScatterChart, Scatter } from 'recharts';
import { useTranslation } from 'react-i18next';
import InfoIcon from '../../shared/components/InfoIcon.tsx';

interface Props {
  data: any[];
}

const CompetencyHeatmap = ({ data }: Props) => {
  const { t } = useTranslation();

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px', background: '#fff' }}>
      <h3 style={{ display: 'flex', alignItems: 'center' }}>
        {t('corporate.competency_heatmap')}
        <InfoIcon 
          desc={t('corporate.heatmap_desc')} 
          benefit={t('corporate.heatmap_benefit')} 
        />
      </h3>
      <div style={{ height: '300px', width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis dataKey="competency" type="category" name={t('corporate.competency')} />
            <YAxis dataKey="role" type="category" name={t('corporate.role')} />
            <ZAxis dataKey="score" range={[100, 500]} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter name="Competency Score" data={data} fill="#8884d8">
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.score > 80 ? '#52c41a' : entry.score > 50 ? '#faad14' : '#ff4d4f'} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default CompetencyHeatmap;
