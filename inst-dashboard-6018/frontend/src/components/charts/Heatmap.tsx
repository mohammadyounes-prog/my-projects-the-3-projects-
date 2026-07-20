import React from 'react';
import {
  HeatMap,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Cell
} from 'recharts';

interface Props {
  data?: any[];
  loading?: boolean;
}

const Heatmap: React.FC<Props> = ({ data = [], loading = false }) => {
  if (loading) return <div>Loading heatmap...</div>;

  // Prepare data for ScatterChart (acting as a heatmap)
  // X: Exam, Y: LO, Z: Performance %
  const exams = Array.from(new Set(data.map(d => d.exam)));
  const los = Array.from(new Set(data.map(d => d.lo)));

  const formattedData = data.map(d => ({
    x: exams.indexOf(d.exam),
    y: los.indexOf(d.lo),
    z: d.value,
    exam: d.exam,
    lo: d.lo
  }));

  const getColor = (value: number) => {
    if (value < 40) return '#ff4d4f'; // Low
    if (value < 70) return '#faad14'; // Mid
    return '#52c41a'; // High
  };

  return (
    <div style={{ 
      border: '1px solid #e0e0e0', 
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
      borderRadius: '8px', 
      padding: '20px', 
      margin: '10px', 
      width: '100%', 
      backgroundColor: '#ffffff',
      height: '400px'
    }}>
      <h3>LO Performance Heatmap</h3>
      <div style={{ width: '100%', height: '300px', minWidth: '300px', minHeight: '200px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
          <XAxis 
            type="category" 
            dataKey="x" 
            name="Exam" 
            ticks={exams.map((_, i) => i)}
            tickFormatter={(i) => exams[i].substring(0, 10)}
            angle={-45}
            textAnchor="end"
          />
          <YAxis 
            type="category" 
            dataKey="y" 
            name="LO" 
            ticks={los.map((_, i) => i)}
            tickFormatter={(i) => los[i].substring(0, 10)}
          />
          <ZAxis type="number" dataKey="z" range={[100, 500]} name="Performance %" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Scatter data={formattedData}>
            {formattedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.z)} />
            ))}
          </Scatter>
        </ScatterChart>
        </ResponsiveContainer>
        </div>
        </div>
        );
        };
export default Heatmap;
