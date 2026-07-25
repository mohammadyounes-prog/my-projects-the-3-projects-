import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import i18next from 'i18next';
// ... rest of imports
import OverallPerformanceIndex from '../components/kpiCard/OverallPerformanceIndex.tsx';
import AvgLOAttainment from '../components/kpiCard/AvgLOAttainment.tsx';
import InstitutionalPassRate from '../components/kpiCard/InstitutionalPassRate.tsx';
import ExamQualityIndex from '../components/kpiCard/ExamQualityIndex.tsx';
import QuestionBankHealth from '../components/kpiCard/QuestionBankHealth.tsx';
import KPIRadarChart from '../shared/charts/KPIRadarChart.tsx';
import LineChart from '../components/charts/LineChart.tsx';
import Heatmap from '../components/charts/Heatmap.tsx';
import DistractorChart from '../components/charts/DistractorChart.tsx';
import ExamQualityDistributionChart from '../components/charts/ExamQualityDistributionChart.tsx';
import PassRateTrendChart from '../components/charts/PassRateTrendChart.tsx';
import BankCoverageChart from '../components/charts/BankCoverageChart.tsx';
import './Dashboard.css';

const DashboardPage = () => {
  const { t } = useTranslation();
  const [kpis, setKpis] = useState<any | null>(null);
  const [atRisk, setAtRisk] = useState<any[]>([]);
  const [loBreakdown, setLoBreakdown] = useState<any[]>([]);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [examQualityData, setExamQualityData] = useState<any[]>([]);
  const [distractorData, setDistractorData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAi, setLoadingAi] = useState(false);
  const [aiAdvice, setAiAdvice] = useState<string | null>(null);

  useEffect(() => {
    const base = process.env.REACT_APP_API_BASE_URL;
    if (!base) {
      setLoading(false);
      return;
    }

    const get = (path: string) =>
      axios.get(`${base}${path}`).then((r) => r.data).catch(() => null);

    Promise.all([
      get('/data/kpis'),
      get('/data/at-risk-students'),
      get('/data/lo-attainment'),
      get('/data/lo-attainment-trend'),
      get('/data/exam-quality'),
      get('/data/distractor-analysis'),
      get('/data/heatmap-data'),
    ]).then(([kpiData, risk, lo, trend, examQ, distractor, heatmap]) => {
      if (kpiData) setKpis(kpiData);
      if (Array.isArray(risk)) setAtRisk(risk);
      if (Array.isArray(lo)) setLoBreakdown(lo);
      if (Array.isArray(trend)) setTrendData(trend);
      if (Array.isArray(examQ)) setExamQualityData(examQ);
      if (Array.isArray(distractor)) setDistractorData(distractor);
      if (Array.isArray(heatmap)) setHeatmapData(heatmap);
    }).finally(() => setLoading(false));
  }, []);


  const fetchAiAdvice = async () => {
    setLoadingAi(true);
    try {
        const lang = i18next.language || 'en';
        const r = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/ai-advice`, { params: { lang } });
        setAiAdvice(r.data.advice);
    } catch (e) {
        console.error(e);
        setAiAdvice("Failed to fetch AI advice.");
    } finally {
        setLoadingAi(false);
    }
  };

  const kpiMetric = (key: string) => kpis?.[key] ?? null;
  const kpiValue = (key: string) => kpiMetric(key)?.value;
  const kpiTrend = (key: string) => {
    const m = kpiMetric(key);
    if (!m) return undefined;
    const arrow = m.trend === 'up' ? '↑' : m.trend === 'down' ? '↓' : '→';
    const delta = m.delta ?? 0;
    return `${arrow} ${delta}%`;
  };

  const topLOs = loBreakdown.slice(0, 5);
  const bottomLOs = [...loBreakdown].reverse().slice(0, 5);

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>{t('dashboard.title')}</h1>
        <button className="ai-advice-btn" onClick={fetchAiAdvice} disabled={loadingAi}>
            {loadingAi ? t('common.loading') : t('dashboard.ai_advice_btn', 'TDM-AI-Advice')}
        </button>
      </div>

      {aiAdvice && (
        <div className="ai-insight-box">
            <button className="close-ai-btn" onClick={() => setAiAdvice(null)}>&times;</button>
            <h3>{t('dashboard.ai_insight_title', 'AI-Powered Insight')}</h3>
            <pre className="ai-advice-text">{aiAdvice}</pre>
        </div>
      )}
      
      {/* 1. Top Section: 4 Main KPI Indexes (Institutional Pulse) */}
      <div className="dashboard-section">
        <h2>{t('dashboard.institutional_pulse', 'Institutional Pulse')}</h2>
        <div className="kpi-grid">
          <AvgLOAttainment value={kpiValue('avg_lo_attainment')} loading={loading} trend={kpiTrend('avg_lo_attainment')} />
          <InstitutionalPassRate value={kpiValue('pass_rate')} loading={loading} trend={kpiTrend('pass_rate')} />
          <ExamQualityIndex value={kpiValue('exam_quality_index')} loading={loading} trend={kpiTrend('exam_quality_index')} />
          <QuestionBankHealth value={kpiValue('question_bank_health')} loading={loading} trend={kpiTrend('question_bank_health')} />
          <OverallPerformanceIndex 
            value={kpiValue('overall_performance')} 
            loading={loading} 
            trend={kpiTrend('overall_performance')} 
            insight={kpiMetric('overall_performance')?.insight}
            breakdown={kpiMetric('overall_performance')?.breakdown}
          />
        </div>
      </div>
      
      {/* 2. Analytical Charts Section (Diagnostic Details) */}
      <div className="dashboard-section">
        <h2>{t('dashboard.analytical_insights', 'Analytical Insights')}</h2>
        
        <div className="charts-grid">
            <div className="chart-wrapper"><KPIRadarChart data={kpis} /></div>
            <div className="chart-wrapper"><LineChart data={trendData} loading={loading} /></div>
        </div>
        
        <div className="charts-grid">
            <div className="chart-wrapper">
                <h3>{t('dashboard.lo_trend', 'LO Attainment Trend')}</h3>
                <PassRateTrendChart data={trendData} />
            </div>
            <div className="chart-wrapper">
                <h3>{t('dashboard.exam_quality', 'Exam Quality Index')}</h3>
                <ExamQualityDistributionChart data={examQualityData} />
            </div>
            <div className="chart-wrapper">
                <DistractorChart data={distractorData} />
            </div>
        </div>
      </div>
      
      {/* 3. Areas for Action */}
      <div className="dashboard-section">
        <h2>{t('dashboard_ext.areas_for_action', 'Areas for Action')}</h2>
        <div className="action-grid">
          
          {/* At-Risk Students Card */}
          <div className="action-card at-risk">
            <h3>{t('dashboard.at_risk_students')}</h3>
            {loading ? <p>{t('common.loading')}</p> : (
              <div className="action-list">
                {atRisk.slice(0, 5).map(s => (
                  <div key={s.id} className="action-item">
                    <span>{s.name}</span>
                    <span className="action-value">{s.avg_score}%</span>
                    <span className="action-meta">{t('dashboard.critical_los', 'Critical')}: {s.critical_los.length} LOs</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* LO Priority Card */}
          <div className="action-card priority-lo">
            <h3>{t('dashboard.priority_lo', 'Priority LO Improvement')}</h3>
            {loBreakdown.length > 0 ? (
              <div className="action-list">
                {bottomLOs.map(lo => (
                  <div key={lo.name} className="action-item">
                    <span>{lo.name}</span>
                    <span className="action-value">{lo.attainment}%</span>
                  </div>
                ))}
              </div>
            ) : <p>{t('dashboard.all_lo_performing', 'All LOs performing well.')}</p>}
          </div>
        </div>
      </div>
    </div>
  );

};
export default DashboardPage;
