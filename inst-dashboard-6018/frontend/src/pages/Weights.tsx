import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const WeightsPage = () => {
  const { t } = useTranslation();
  const [weights, setWeights] = useState({
    lo_attainment: 0.3,
    pass_rate: 0.3,
    exam_quality: 0.2,
    question_bank: 0.2
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    axios.get(`${process.env.REACT_APP_API_BASE_URL}/settings/weights`)
      .then(res => {
        if (Object.keys(res.data).length > 0) {
          // Ensure all keys exist even if old DB data only had 3
          setWeights(prev => ({...prev, ...res.data}));
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching weights:", err);
        setLoading(false);
      });
  }, []);

  const total = parseFloat(weights.lo_attainment || 0) + 
                parseFloat(weights.pass_rate || 0) + 
                parseFloat(weights.exam_quality || 0) +
                parseFloat(weights.question_bank || 0);
  const isValid = Math.abs(total - 1.0) < 0.001;

  const handleSave = () => {
    if (!isValid) {
      setMessage("Error: The total sum of weights must be exactly 1.0");
      return;
    }

    setSaving(true);
    axios.post(`${process.env.REACT_APP_API_BASE_URL}/settings/weights`, weights)
      .then(() => {
        setMessage("Weights saved successfully!");
        setSaving(false);
      })
      .catch(err => {
        setMessage("Error saving weights: " + err.message);
        setSaving(false);
      });
  };

  if (loading) return <div>Loading settings...</div>;

  return (
    <div className="dashboard-container nebula-motion-page">
      <div className="dashboard-section" style={{ maxWidth: '680px', marginInline: 'auto' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--nebula-accent-cyan)', display: 'block', marginBottom: '0.5rem' }}>
          Analytics Configuration
        </span>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.75rem', fontWeight: '700', color: 'var(--nebula-text)', margin: '0 0 0.5rem' }}>
          {t('common.weights_config', 'Indexes Weights Configuration')}
        </h1>
        <p style={{ color: 'var(--nebula-text-muted)', fontSize: '0.9rem', marginBottom: '1.75rem', lineHeight: '1.5' }}>
          {t('weights.description', 'Adjust how much each index contributes to the Overall Performance Score. The sum must be exactly 1.0.')}
        </p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--nebula-accent-cyan)' }}>
              {t('weights.lo_weight', 'LO Attainment Weight')}
            </label>
            <input 
              type="number" 
              step="0.05" 
              max="1"
              min="0"
              value={weights.lo_attainment} 
              onChange={(e) => setWeights({...weights, lo_attainment: parseFloat(e.target.value) || 0})}
              style={{ width: '100%', boxSizing: 'border-box', padding: '0.75rem', borderRadius: 'var(--nebula-radius-sm)', border: '1px solid var(--nebula-border)', fontFamily: 'var(--font-body)', fontSize: '1rem' }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--nebula-accent-cyan)' }}>
              {t('weights.pass_rate_weight', 'Pass Rate Weight')}
            </label>
            <input 
              type="number" 
              step="0.05" 
              max="1"
              min="0"
              value={weights.pass_rate} 
              onChange={(e) => setWeights({...weights, pass_rate: parseFloat(e.target.value) || 0})}
              style={{ width: '100%', boxSizing: 'border-box', padding: '0.75rem', borderRadius: 'var(--nebula-radius-sm)', border: '1px solid var(--nebula-border)', fontFamily: 'var(--font-body)', fontSize: '1rem' }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--nebula-accent-cyan)' }}>
              {t('weights.exam_quality_weight', 'Exam Quality Weight')}
            </label>
            <input 
              type="number" 
              step="0.05" 
              max="1"
              min="0"
              value={weights.exam_quality} 
              onChange={(e) => setWeights({...weights, exam_quality: parseFloat(e.target.value) || 0})}
              style={{ width: '100%', boxSizing: 'border-box', padding: '0.75rem', borderRadius: 'var(--nebula-radius-sm)', border: '1px solid var(--nebula-border)', fontFamily: 'var(--font-body)', fontSize: '1rem' }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--nebula-accent-cyan)' }}>
              {t('weights.bank_health_weight', 'Question Bank Health Weight')}
            </label>
            <input 
              type="number" 
              step="0.05" 
              max="1"
              min="0"
              value={weights.question_bank} 
              onChange={(e) => setWeights({...weights, question_bank: parseFloat(e.target.value) || 0})}
              style={{ width: '100%', boxSizing: 'border-box', padding: '0.75rem', borderRadius: 'var(--nebula-radius-sm)', border: '1px solid var(--nebula-border)', fontFamily: 'var(--font-body)', fontSize: '1rem' }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', padding: '1.25rem', backgroundColor: 'var(--nebula-bg-input)', borderRadius: 'var(--nebula-radius-md)', border: '1px solid var(--nebula-border)' }}>
          <button 
            onClick={handleSave} 
            disabled={saving || !isValid}
            style={{ 
              padding: '0.75rem 1.5rem', 
              backgroundColor: !isValid ? 'var(--nebula-text-muted)' : 'var(--nebula-accent-cyan)', 
              color: 'var(--nebula-on-accent)', 
              border: 'none', 
              borderRadius: 'var(--nebula-radius-sm)',
              fontWeight: '600',
              cursor: !isValid ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s'
            }}
          >
            {saving ? 'Saving...' : 'Save Weights'}
          </button>

          <div style={{ 
            padding: '0.5rem 1rem', 
            borderRadius: 'var(--nebula-radius-sm)', 
            backgroundColor: !isValid ? 'var(--nebula-danger-dim)' : 'var(--nebula-success-dim)',
            border: `1px solid ${!isValid ? 'var(--nebula-danger)' : 'var(--nebula-success)'}`,
            fontWeight: '700',
            fontSize: '0.9rem',
            color: !isValid ? 'var(--nebula-danger)' : 'var(--nebula-success)'
          }}>
            Total Sum: {total.toFixed(2)}
          </div>
        </div>

        {message && (
          <p style={{ marginTop: '1rem', color: message.includes('Error') ? 'var(--nebula-danger)' : 'var(--nebula-success)', fontWeight: '600', fontSize: '0.9rem' }}>
            {message}
          </p>
        )}
      </div>
    </div>
  );
};

export default WeightsPage;
