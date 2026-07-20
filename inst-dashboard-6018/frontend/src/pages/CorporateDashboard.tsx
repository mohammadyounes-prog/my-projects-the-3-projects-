import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';
import InfoIcon from '../shared/components/InfoIcon.tsx';
import KPIRadarChart from '../shared/charts/KPIRadarChart.tsx';
import CompetencyHeatmap from '../components/charts/CompetencyHeatmap.tsx';

const AdminView = () => {
    const { t } = useTranslation();
    const [stats, setStats] = useState<any>(null);
    const [bankHealth, setBankHealth] = useState<any>(null);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/corporate/hr-stats`)
            .then(r => setStats(r.data))
            .catch(e => console.error("AdminView stats error:", e));
        
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/corporate/bank-health`)
            .then(r => setBankHealth(r.data))
            .catch(e => console.error("Bank health error:", e));
    }, []);

    if (!stats || !bankHealth) return <div>{t('common.loading')}</div>;

    // ... inside AdminView return block:
    return (
        <div>
            {/* ... Existing Widgets ... */}
            
            <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px', marginTop: '20px' }}>
                <h2 style={{ display: 'flex', alignItems: 'center' }}>
                    {t('dashboard.bank_health_title', 'Question Bank Health')}
                    <InfoIcon desc={t('dashboard.bank_health_desc', 'Question bank composition.')} benefit={t('dashboard.bank_health_benefit', 'Ensure balanced assessments.')} />
                </h2>
                <div style={{ display: 'flex', gap: '40px' }}>
                    <div style={{ width: '300px' }}>
                        <h4>{t('dashboard.difficulty_distribution', 'Difficulty Distribution')}</h4>
                        <PieChart width={300} height={200}>
                            <Pie data={bankHealth.difficulty} dataKey="count" nameKey="label" cx="50%" cy="50%" outerRadius={60} fill="#8884d8">
                                {bankHealth.difficulty.map((entry: any, index: number) => <Cell key={index} fill={['#52c41a', '#faad14', '#f5222d'][index]} />)}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </div>
                    <div style={{ width: '300px' }}>
                        <h4>{t('dashboard.discrimination_index', 'Discrimination Index')}</h4>
                        <PieChart width={300} height={200}>
                            <Pie data={bankHealth.discrimination} dataKey="count" nameKey="label" cx="50%" cy="50%" outerRadius={60} fill="#82ca9d">
                                {bankHealth.discrimination.map((entry: any, index: number) => <Cell key={index} fill={['#1890ff', '#faad14', '#8c8c8c'][index]} />)}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </div>
                </div>
            </div>
        </div>
    );

    // Mock data for heatmap
    const heatmapData = [
        { competency: 'Python', role: 'Engineer', score: 85 },
        { competency: 'Communication', role: 'Engineer', score: 60 },
        { competency: 'Project Mgmt', role: 'Engineer', score: 40 },
        { competency: 'Python', role: 'Sales', score: 30 },
        { competency: 'Communication', role: 'Sales', score: 90 },
        { competency: 'Project Mgmt', role: 'Sales', score: 70 },
    ];

    return (
        <div>
            <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                <div style={{ flex: '1', padding: '20px', borderRadius: '12px', border: '1px solid #722ed1', background: '#f9f0ff' }}>
                    <h3 style={{ display: 'flex', alignItems: 'center' }}>
                        {t('corporate.onboarding_speed')}
                        <InfoIcon desc={t('corporate.onboarding_desc')} benefit={t('corporate.onboarding_benefit')} />
                    </h3>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{stats.onboarding_days} {t('corporate.days')}</div>
                </div>
                <div style={{ flex: '1', padding: '20px', borderRadius: '12px', border: '1px solid #fa8c16', background: '#fff7e6' }}>
                    <h3 style={{ display: 'flex', alignItems: 'center' }}>
                        {t('corporate.skill_gap')}
                        <InfoIcon desc={t('corporate.skill_gap_desc')} benefit={t('corporate.skill_gap_benefit')} />
                    </h3>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{stats.skill_gap}%</div>
                </div>
            </div>
            
            <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                <div style={{ flex: '1' }}>
                    <KPIRadarChart data={stats} />
                </div>
                <div style={{ flex: '1' }}>
                    <CompetencyHeatmap data={heatmapData} />
                </div>
            </div>

            <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px' }}>
                <h2 style={{ display: 'flex', alignItems: 'center' }}>
                    {t('corporate.performance_by_dept')}
                    <InfoIcon desc={t('corporate.dept_perf_desc')} benefit={t('corporate.dept_perf_benefit')} />
                </h2>
                <div style={{ height: '300px', width: '100%' }}>
                    <BarChart width={500} height={300} data={stats.dept_performance}>
                        <XAxis dataKey="dept" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="score" fill="#722ed1" />
                    </BarChart>
                </div>
            </div>
        </div>
    );
};

const EmployeeView = () => {
    const { t, i18n } = useTranslation();
    const lang = i18n.language;
    const [personality, setPersonality] = useState<any>(null);
    const [scorecard, setScorecard] = useState<any>(null);
    const [advancement, setAdvancement] = useState<any>(null);
    const [recommendations, setRecommendations] = useState<any>(null);
    const [feedback, setFeedback] = useState<any>(null);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/corporate/personality-insights/1?lang=${lang}`).then(r => setPersonality(r.data));
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/corporate/performance-scorecard/1?lang=${lang}`).then(r => setScorecard(r.data));
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/corporate/advancement-status/1?lang=${lang}`).then(r => setAdvancement(r.data));
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/corporate/development-recommendations/1?lang=${lang}`).then(r => setRecommendations(r.data));
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/corporate/feedback/1?lang=${lang}`).then(r => setFeedback(r.data));
    }, [lang]);

    if (!personality || !scorecard || !advancement || !recommendations || !feedback) return <div>{t('common.loading')}</div>;

    return (
        <div>
            {/* Advancement Widget */}
            <div style={{ padding: '20px', marginBottom: '20px', borderRadius: '12px', border: `1px solid ${advancement.is_ready ? '#52c41a' : '#faad14'}`, backgroundColor: advancement.is_ready ? '#f6ffed' : '#fff7e6' }}>
                <h3 style={{ color: advancement.is_ready ? '#389e0d' : '#d46b08', display: 'flex', alignItems: 'center' }}>
                    {t('corporate.advancement_title')}
                    <InfoIcon desc={t('corporate.advancement_desc')} benefit={t('corporate.advancement_benefit')} />
                </h3>
                <p><strong>{t('corporate.readiness_score')}:</strong> {advancement.readiness_score}/100</p>
                <p><strong>{t('corporate.recommendation')}:</strong> {advancement.recommendation}</p>
            </div>

            {/* 360-Degree Feedback Widget */}
            <div style={{ padding: '20px', marginBottom: '20px', border: '1px solid #ddd', borderRadius: '12px', background: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                <h2 style={{ display: 'flex', alignItems: 'center' }}>
                    {t('corporate.feedback_360')}
                    <InfoIcon desc={t('corporate.feedback_360_desc')} benefit={t('corporate.feedback_360_benefit')} />
                </h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    {feedback.feedback.map((item: any, index: number) => (
                        <div key={index} style={{ padding: '15px', borderRadius: '8px', background: '#f8f9fa', borderLeft: '4px solid #1677ff' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                <span style={{ fontWeight: 'bold' }}>{item.reviewer}</span>
                                <span style={{ color: '#888', fontSize: '0.9em' }}>{item.role}</span>
                            </div>
                            <p style={{ margin: 0, color: '#444', fontStyle: 'italic' }}>"{item.comment}"</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Development Recommendations Widget */}
            <div style={{ padding: '20px', marginBottom: '20px', border: '1px solid #ddd', borderRadius: '12px', background: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                <h2 style={{ display: 'flex', alignItems: 'center' }}>
                    {t('corporate.development_recommendations')}
                    <InfoIcon desc={t('corporate.dev_recommendations_desc')} benefit={t('corporate.dev_recommendations_benefit')} />
                </h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {recommendations.recommendations.map((rec: any, index: number) => (
                        <div key={index} style={{ padding: '15px', borderRadius: '8px', border: '1px solid #e8e8e8', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#fafafa' }}>
                            <div>
                                <div style={{ fontWeight: 'bold', fontSize: '16px' }}>{rec.task}</div>
                                <div style={{ fontSize: '0.9em', color: '#666' }}>{t('corporate.gap_area')}: {rec.gap}</div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                <span style={{ 
                                    padding: '4px 12px', borderRadius: '20px', fontSize: '0.8em', fontWeight: 'bold',
                                    backgroundColor: rec.priority === 'High' ? '#ffccc7' : '#fff7e6',
                                    color: rec.priority === 'High' ? '#cf1322' : '#d46b08'
                                }}>
                                    {rec.priority === 'High' ? t('corporate.priority_high') : t('corporate.priority_medium')}
                                </span>
                                <button style={{ padding: '6px 12px', backgroundColor: '#1677ff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                                    {t('corporate.action_start_training')}
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                <div style={{ flex: '1', padding: '20px', border: '1px solid #ddd', borderRadius: '12px' }}>
                    <h2 style={{ display: 'flex', alignItems: 'center' }}>
                        {t('corporate.personality_insights')}
                        <InfoIcon desc={t('corporate.personality_insights_desc')} benefit={t('corporate.personality_insights_benefit')} />
                    </h2>
                    <div style={{ height: '300px' }}>
                        <ResponsiveContainer width="100%" height={300} minWidth={200}>
                            <BarChart data={personality.traits} layout="vertical">
                                <XAxis type="number" domain={[0, 100]} />
                                <YAxis dataKey="trait" type="category" />
                                <Tooltip />
                                <Bar dataKey="score" fill="#1677ff" />
                            </BarChart>
                        </ResponsiveContainer>                    </div>
                </div>
            </div>

            <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px' }}>
                <h2 style={{ display: 'flex', alignItems: 'center' }}>
                    {t('corporate.performance_scorecard')}
                    <InfoIcon desc={t('corporate.performance_scorecard_desc')} benefit={t('corporate.performance_scorecard_benefit')} />
                </h2>
                <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
                    {scorecard.metrics.map((metric: any) => (
                        <div key={metric.label} style={{ textAlign: 'center', width: '150px' }}>
                            <ResponsiveContainer width="100%" height={150} minWidth={100} minHeight={100}>
                                <PieChart>
                                    <Pie data={[{val: metric.value}, {val: metric.target - metric.value}]} dataKey="val" innerRadius={40} outerRadius={60}>
                                        <Cell fill="#1890ff" /><Cell fill="#eee" />
                                    </Pie>
                                </PieChart>
                            </ResponsiveContainer>
                            <div style={{ fontWeight: 'bold' }}>{t(`corporate.${metric.label.toLowerCase().replace(' ', '_')}`, metric.label)}</div>
                            <div style={{ fontSize: '20px' }}>{metric.value}%</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// --- Main Corporate Dashboard ---

const CorporateDashboard = () => {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState<'admin' | 'employee'>('admin');

    return (
        <div style={{ padding: '20px' }}>
            <h1>{t('corporate.title')}</h1>
            
            <div style={{ marginBottom: '20px', borderBottom: '2px solid #eee' }}>
                <button 
                    onClick={() => setActiveTab('admin')}
                    className={`tab-button ${activeTab === 'admin' ? 'active' : ''}`}
                >
                    <span style={{ color: activeTab === 'admin' ? '#000' : 'inherit' }}>{t('corporate.admin_view')}</span>
                </button>
                <button 
                    onClick={() => setActiveTab('employee')}
                    className={`tab-button ${activeTab === 'employee' ? 'active' : ''}`}
                >
                    <span style={{ color: activeTab === 'employee' ? '#000' : 'inherit' }}>{t('corporate.employee_view')}</span>
                </button>
            </div>

            {activeTab === 'admin' ? <AdminView /> : <EmployeeView />}
        </div>
    );
};

export default CorporateDashboard;
