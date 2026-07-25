import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine
} from 'recharts';

const ExamQualityChart = () => {
  const { t } = useTranslation();
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/exam-quality`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching exam quality data:", err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>{t('common.loading', 'Loading...')}</div>;

  return (
    <div style={{ width: '100%', height: '450px', padding: '20px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: 'var(--nebula-bg-glass)' }}>
      <h3>{t('charts.exam_quality_title', 'Exam Difficulty vs. Discrimination')}</h3>
      <ResponsiveContainer width="100%" height="80%">
        <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            type="number" 
            dataKey="difficulty" 
            name={t('charts.difficulty', 'Difficulty')} 
            domain={[0, 1]}
            label={{ value: t('charts.difficulty', 'Difficulty (0=Hard, 1=Easy)'), position: 'bottom', offset: 0 }} 
          />
          <YAxis 
            type="number" 
            dataKey="discrimination" 
            name={t('charts.discrimination', 'Discrimination')} 
            domain={[-0.5, 1]}
            label={{ value: t('charts.discrimination', 'Discrimination'), angle: -90, position: 'left' }} 
          />
          <ZAxis type="string" dataKey="exam" name="Exam" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Legend />
          <ReferenceLine y={0.2} stroke="red" strokeDasharray="3 3" label="Threshold" />
          <Scatter name="Exams" data={data} fill="var(--nebula-accent-purple)" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ExamQualityChart;
