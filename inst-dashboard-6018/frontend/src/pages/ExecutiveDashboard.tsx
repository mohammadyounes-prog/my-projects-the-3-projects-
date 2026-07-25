import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import i18n from '../i18n/index.ts';
import axios from 'axios';
import { ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import InfoIcon from '../shared/components/InfoIcon.tsx';
import KPIRadarChart from '../shared/charts/KPIRadarChart.tsx';

// Placeholder components for the strategic view
const StrategicKPICard = ({ title, value, desc, benefit, color, children }: { title: string; value: string; desc: string; benefit: string; color: string; children?: React.ReactNode }) => (
    <div style={{ flex: '1', minWidth: '300px', padding: '20px', borderRadius: '12px', border: `1px solid ${color}`, backgroundColor: `${color}10` }}>
        <h4 style={{ margin: '0 0 10px 0', color: color, display: 'flex', alignItems: 'center' }}>
            {title}
            <InfoIcon desc={desc} benefit={benefit} />
        </h4>
        <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px' }}>{value}</div>
        <div style={{ height: '100px' }}>{children}</div>
    </div>
);
const AIInsightCard = ({ isVisible, onClose }: { isVisible: boolean, onClose: () => void }) => {
    const { t, i18n } = useTranslation();
    const [advice, setAdvice] = useState<string>('');
    const [currentLang, setCurrentLang] = useState(i18n.language);

    useEffect(() => {
        const handleLanguageChange = () => setCurrentLang(i18n.language);
        i18n.on('languageChanged', handleLanguageChange);
        return () => i18n.off('languageChanged', handleLanguageChange);
    }, [i18n]);

    const fetchAdvice = () => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/ai-advice-history?lang=${currentLang}&t=${Date.now()}`)
            .then(r => setAdvice(r.data.advice))
            .catch(e => console.error("Error fetching advice:", e));
    };

    useEffect(() => {
        fetchAdvice();
    }, [currentLang]);

    if (!isVisible) return null;

    return (
        <div style={{ padding: '20px', border: '1px solid var(--nebula-accent-cyan)', borderRadius: '12px', background: 'var(--nebula-bg-glass)', backdropFilter: 'blur(8px)', marginBottom: '20px', position: 'relative' }}>
            <button 
                onClick={onClose}
                style={{ position: 'absolute', top: '10px', right: '10px', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '18px', fontWeight: 'bold', color: 'var(--nebula-text-muted)' }}
            >
                &times;
            </button>
            <h3 style={{ color: 'var(--nebula-accent-cyan)', marginRight: '20px' }}>{t('dashboard.ai_insight_title')}</h3>
            <p style={{ whiteSpace: 'pre-wrap', color: 'var(--nebula-text)' }}>{advice || t('common.loading')}</p>
        </div>
    );
};

const ExecutiveDashboard = () => {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState<any>(null);
    const [bankCoverage, setBankCoverage] = useState<any[]>([]);
    const [kpiData, setKpiData] = useState<any>(null);
    const [isInsightVisible, setIsInsightVisible] = useState(true);

    // Dummy data for sparklines
    const interventionData = [{name: 'Sem 1', val: 5}, {name: 'Sem 2', val: 8}, {name: 'Sem 3', val: 12}];
    const hoursData = [{name: 'Jan', val: 100}, {name: 'Feb', val: 300}, {name: 'Mar', val: 1240}];

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/executive-stats?lang=${i18n.language}`).then(r => setStats(r.data));
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/bank-coverage`).then(r => setBankCoverage(r.data));
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/kpis`).then(r => setKpiData(r.data));
        setLoading(false);
    }, [i18n.language]);

    if (loading || !stats) return <div>{t('common.loading')}</div>;

    return (
        <div style={{ padding: '20px' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h1>{t('executive.title')}</h1>
                {!isInsightVisible && (
                    <button 
                        onClick={() => setIsInsightVisible(true)}
                        style={{ padding: '8px 16px', background: 'var(--nebula-accent-cyan)', color: 'var(--nebula-bg-glass)', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                    >
                        {t('dashboard.show_ai_insight')}
                    </button>
                )}
            </div>
            
            <AIInsightCard isVisible={isInsightVisible} onClose={() => setIsInsightVisible(false)} />

            {kpiData && (
                <div style={{ marginBottom: '30px', height: '400px' }}>
                    <KPIRadarChart data={kpiData} />
                </div>
            )}

            {/* 1. Strategic ROI Section */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', marginBottom: '30px' }}>
                <StrategicKPICard 
                    title={t('executive.prep_hours_title')}
                    value={`${stats.prep_hours_saved.value} ${stats.prep_hours_saved.unit}`} 
                    desc={t('executive.prep_hours_desc')}
                    benefit={t('executive.prep_hours_benefit')}
                    color="var(--nebula-accent-cyan)" 
                >
                    <ResponsiveContainer width="100%" height="100%"><LineChart data={hoursData}><Line type="monotone" dataKey="val" stroke="var(--nebula-accent-cyan)" strokeWidth={2} /></LineChart></ResponsiveContainer>
                </StrategicKPICard>

                <StrategicKPICard 
                    title={t('executive.accreditation_title')}
                    value={`${stats.accreditation_readiness.value}${stats.accreditation_readiness.unit}`} 
                    desc={t('executive.accreditation_desc')}
                    benefit={t('executive.accreditation_benefit')}
                    color="var(--nebula-success)" 
                >
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie data={[{val: stats.accreditation_readiness.value}, {val: 100 - stats.accreditation_readiness.value}]} dataKey="val" innerRadius={30} outerRadius={40}>
                                <Cell fill="var(--nebula-success)" /><Cell fill="var(--nebula-border)" />
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                </StrategicKPICard>

                <StrategicKPICard 
                    title={t('executive.intervention_title')}
                    value={`${stats.intervention_efficiency.value} ${stats.intervention_efficiency.unit}`} 
                    desc={t('executive.intervention_desc')}
                    benefit={t('executive.intervention_benefit')}
                    color="var(--nebula-warning)" 
                >
                    <ResponsiveContainer width="100%" height="100%"><LineChart data={interventionData}><Line type="monotone" dataKey="val" stroke="var(--nebula-warning)" strokeWidth={2} /></LineChart></ResponsiveContainer>
                </StrategicKPICard>
            </div>

            {/* 2. Strategic Insights Area */}
            <div style={{ padding: '20px', border: '1px solid var(--nebula-border)', borderRadius: '12px' }}>
                <h2>{t('executive.resource_allocation_title')}</h2>
                <p>{t('executive.resource_allocation_desc')}</p>
                <div style={{ height: '300px' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={bankCoverage.filter(c => c.count < 10)}>
                            <XAxis dataKey="lo" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="count" fill="var(--nebula-danger)" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default ExecutiveDashboard;
