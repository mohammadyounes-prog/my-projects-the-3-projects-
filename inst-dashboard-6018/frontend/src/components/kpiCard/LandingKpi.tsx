import React from 'react';

interface LandingKpiProps {
  label: string;
  value: string | number;
}

const LandingKpi: React.FC<LandingKpiProps> = ({ label, value }) => {
  return (
    <div className="gateway-kpi-card">
      <span className="gateway-kpi-label">{label}</span>
      <span className="gateway-kpi-value">{value}</span>
    </div>
  );
};

export default LandingKpi;
