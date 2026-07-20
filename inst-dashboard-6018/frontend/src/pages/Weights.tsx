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
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h1>{t('common.weights_config', 'Indexes Weights Configuration')}</h1>
      <p>{t('weights.description', 'Adjust how much each index contributes to the Overall Performance Score. The sum must be exactly 1.0.')}</p>
      
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>{t('weights.lo_weight', 'LO Attainment Weight')}</label>
        <input 
          type="number" 
          step="0.05" 
          max="1"
          min="0"
          value={weights.lo_attainment} 
          onChange={(e) => setWeights({...weights, lo_attainment: e.target.value})}
          style={{ width: '100%', padding: '8px' }}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>{t('weights.pass_rate_weight', 'Pass Rate Weight')}</label>
        <input 
          type="number" 
          step="0.05" 
          max="1"
          min="0"
          value={weights.pass_rate} 
          onChange={(e) => setWeights({...weights, pass_rate: e.target.value})}
          style={{ width: '100%', padding: '8px' }}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>{t('weights.exam_quality_weight', 'Exam Quality Weight')}</label>
        <input 
          type="number" 
          step="0.05" 
          max="1"
          min="0"
          value={weights.exam_quality} 
          onChange={(e) => setWeights({...weights, exam_quality: e.target.value})}
          style={{ width: '100%', padding: '8px' }}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>{t('weights.bank_health_weight', 'Question Bank Health Weight')}</label>
        <input 
          type="number" 
          step="0.05" 
          max="1"
          min="0"
          value={weights.question_bank} 
          onChange={(e) => setWeights({...weights, question_bank: e.target.value})}
          style={{ width: '100%', padding: '8px' }}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <button 
          onClick={handleSave} 
          disabled={saving || !isValid}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: !isValid ? '#ccc' : '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: !isValid ? 'not-allowed' : 'pointer'
          }}
        >
          {saving ? 'Saving...' : 'Save Weights'}
        </button>

        <div style={{ 
          padding: '10px 15px', 
          border: '1px solid #ddd', 
          borderRadius: '4px', 
          backgroundColor: !isValid ? '#fff0f0' : '#f0fff0',
          fontWeight: 'bold',
          color: !isValid ? 'red' : 'green'
        }}>
          Total Sum: {total.toFixed(2)}
        </div>
      </div>

      {message && <p style={{ marginTop: '20px', color: message.includes('Error') ? 'red' : 'green', fontWeight: 'bold' }}>{message}</p>}
    </div>
  );
};

export default WeightsPage;
