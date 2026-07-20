import React from 'react';

interface LandingKpiProps {
  label: string;
  value: string | number;
}

const LandingKpi: React.FC<LandingKpiProps> = ({ label, value }) => {
  return (
    <div className="landing-kpi-card" style={{ textAlign: 'center', padding: '1rem' }}>
      <span className="landing-kpi-label" style={{ 
        display: 'block', 
        fontSize: '1.2rem', 
        textTransform: 'uppercase', 
        color: '#0050b3', 
        marginBottom: '0.5rem',
        fontWeight: '700'
      }}>
        {label}
      </span>
      <span className="landing-kpi-value" style={{ 
        fontSize: '2.5rem', 
        fontWeight: '800', 
        color: '#3b82f6' 
      }}>
        {value}
      </span>
    </div>
  );
};

export default LandingKpi;
