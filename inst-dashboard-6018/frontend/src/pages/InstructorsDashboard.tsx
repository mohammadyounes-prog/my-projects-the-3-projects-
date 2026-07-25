import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import axios from 'axios';
import SearchableSelect from '../components/SearchableSelect.tsx';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip as RechartsTooltip } from 'recharts';

// Helper functions for date handling
const parseDate = (dateStr: string) => {
  if (!dateStr) return null;
  // Use UTC to avoid timezone shifts
  const [year, month, day] = dateStr.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  console.log("Parsed date for", dateStr, ":", date);
  return date;
};

const formatDate = (date: Date | null) => {
  if (!date) return '';
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const InstructorsDashboard = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [filters, setFilters] = useState(() => {
    const saved = sessionStorage.getItem('dashboard_filters');
    const today = new Date().toISOString().split('T')[0];
    const initialFilters = saved ? JSON.parse(saved) : {
      faculty: '',
      major: '',
      course: '',
      class: '',
      fromDate: '',
      toDate: '',
      exam: ''
    };
    
    // Apply today as default if dates are missing
    if (!initialFilters.fromDate) initialFilters.fromDate = today;
    if (!initialFilters.toDate) initialFilters.toDate = today;
    
    return initialFilters;
  });

  const [options, setOptions] = useState(() => {
    const saved = sessionStorage.getItem('dashboard_options');
    return saved ? JSON.parse(saved) : {
      faculties: [],
      majors: [],
      courses: [],
      classes: [],
      exams: []
    };
  });

  const [selectedExam, setSelectedExam] = useState<any>(null);
  const [attendanceStatus, setAttendanceStatus] = useState('All');
  const [riskSummary, setRiskSummary] = useState({ stable: 0, at_risk: 0, critical: 0 });

  const [triggerFetch, setTriggerFetch] = useState(false);
  const [step, setStep] = useState(1);
  const [maxStep, setMaxStep] = useState(1);

  useEffect(() => {
    // Fetch Risk Summary
    axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/students/risk-summary`)
      .then(res => setRiskSummary(res.data))
      .catch(err => console.error("Error fetching risk summary:", err));
  }, []);

  useEffect(() => {
    // sessionStorage.removeItem('dashboard_filters'); // Removed to allow state persistence
    // sessionStorage.removeItem('dashboard_options');
  }, []);

  useEffect(() => {
    // Always save state to session storage when filters or options change.
    sessionStorage.setItem('dashboard_filters', JSON.stringify(filters));
    sessionStorage.setItem('dashboard_options', JSON.stringify(options));
  }, [filters, options]);

  useEffect(() => {
    if (options.faculties.length > 0) return;
    const username = localStorage.getItem('user_name') || '';
    const fetchFaculties = async () => {
        try {
            const res = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/faculty/list?username=${username}`);
            setOptions(prev => ({ ...prev, faculties: res.data }));
        } catch (e) { console.error(e); }
    };
    fetchFaculties();
  }, []);

  useEffect(() => {
    if (options.majors.length > 0 || !filters.faculty) return;
    const username = localStorage.getItem('user_name') || '';
    const loadMajors = async () => {
      const res = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/major/list?username=${username}&faculty_id=${filters.faculty}`);
      setOptions(prev => ({ ...prev, majors: res.data, courses: [], classes: [], exams: [] }));
    };
    loadMajors();
  }, [filters.faculty]);

  useEffect(() => {
    if (options.courses.length > 0 || !filters.major) return;
    const username = localStorage.getItem('user_name');
    if (!username) return;
    const loadCourses = async () => {
      try {
        const res = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/course/list?username=${username}&major_id=${filters.major}`);
        setOptions(prev => ({ ...prev, courses: res.data, classes: [], exams: [] }));
      } catch (err) { console.error("Error loading courses:", err); }
    };
    loadCourses();
  }, [filters.major]);

  useEffect(() => {
    if (options.classes.length > 0 || !filters.course) return;
    const username = localStorage.getItem('user_name') || '';
    const loadClasses = async () => {
      const res = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/class/list?username=${username}&course_id=${filters.course}`);
      setOptions(prev => ({ ...prev, classes: res.data, exams: [] }));
    };
    loadClasses();
  }, [filters.course]);

  const [errors, setErrors] = useState<Record<string, boolean>>({});

  const handleExecute = () => {
    const newErrors = {
      faculty: !filters.faculty,
      major: !filters.major,
      course: !filters.course,
      class: !filters.class
    };

    if (Object.values(newErrors).some(err => err)) {
      setErrors(newErrors);
      return;
    }

    setErrors({});
    setTriggerFetch(!triggerFetch);
    setStep(2);
    setMaxStep(2); 
    navigate('exams-marks');
  };

  const getFilterStyle = (key: string): React.CSSProperties => ({
    padding: '10px',
    borderRadius: '4px',
    border: errors[key] ? '2px solid red' : '1px solid var(--nebula-border)',
    width: '100%',
    boxSizing: 'border-box'
  });

  const handleDataLoaded = (count: number) => {
    if (count === 0) {
      alert("No exams found for the selected criteria.");
    }
  };

  const handleStepClick = (targetStep: number) => {
    if (targetStep <= maxStep) {
        setStep(targetStep);
        if (targetStep === 1) navigate('/educational/instructors');  
        else navigate('exams-marks');
    }
  };

  const promoteStep = (newStep: number) => {
    setStep(newStep);
    setMaxStep(3);
  };

  const filterStyle: React.CSSProperties = {
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid var(--nebula-border)',
    width: '100%',
    boxSizing: 'border-box'
  };

  return (
    <div className="dashboard-container nebula-motion-page" style={{ maxWidth: '1400px', width: '100%', margin: '0 auto', boxSizing: 'border-box' }}>
      {/* 1. NAVIGATION STEP TABS */}
      <div style={{ display: 'flex', marginBottom: '28px', gap: '14px', flexWrap: 'wrap' }}>
        {['exam_selection', 'choose_exam', 'exam_results'].map((s, i) => {
          const stepIndex = i + 1;
          const isActive = step === stepIndex;
          const isVisited = stepIndex <= maxStep;
          return (
            <div 
              key={s} 
              onClick={() => handleStepClick(stepIndex)}
              style={{ 
                padding: '12px 24px', 
                background: isActive ? 'var(--nebula-accent-cyan)' : (isVisited ? 'var(--nebula-accent-cyan-dim)' : 'var(--nebula-bg-glass)'), 
                color: isVisited || isActive ? 'var(--nebula-bg-glass)' : 'var(--nebula-text-muted)',
                border: isVisited || isActive ? '1px solid var(--nebula-accent-cyan)' : '1px solid var(--nebula-border)',
                borderRadius: '0.75rem',
                flex: '1 1 200px',
                textAlign: 'center',
                cursor: isVisited ? 'pointer' : 'default',
                fontSize: '14px',
                fontWeight: '700',
                fontFamily: 'var(--nebula-font-display), sans-serif',
                boxShadow: isActive ? '0 4px 15px var(--nebula-shadow-glass)' : 'none',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <span style={{ 
                display: 'inline-flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                width: '22px', 
                height: '22px', 
                borderRadius: '50%', 
                backgroundColor: isActive || isVisited ? 'rgba(255,255,255,0.2)' : 'var(--nebula-bg-input)',
                fontSize: '12px',
                fontWeight: '700'
              }}>
                {stepIndex}
              </span>
              {t(`instructor.${s}`, s.replace('_', ' '))}
            </div>
          );
        })}
      </div>

      {step === 1 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', width: '100%' }}>
          {/* Top Row: Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', width: '100%' }}>
            {[
              { label: t('instructor.risk.stable', 'Stable Students'), count: riskSummary.stable ?? 0, color: 'var(--nebula-success)', bg: 'var(--nebula-success-dim)', borderColor: 'var(--nebula-success)' },
              { label: t('instructor.risk.at_risk', 'At Risk Students'), count: riskSummary.at_risk ?? 0, color: 'var(--nebula-warning)', bg: 'var(--nebula-warning-dim)', borderColor: 'var(--nebula-warning)' },
              { label: t('instructor.risk.critical', 'Critical Risk Students'), count: riskSummary.critical ?? 0, color: 'var(--nebula-danger)', bg: 'var(--nebula-danger-dim)', borderColor: 'var(--nebula-danger)' }
            ].map((item, i) => (
              <div 
                key={i} 
                style={{ 
                  background: 'transparent', 
                  padding: '24px', 
                  borderRadius: '1.25rem', 
                  border: `1px solid ${item.borderColor}`, 
                  borderTop: `5px solid ${item.color}`, 
                  boxShadow: '0 4px 15px var(--nebula-border)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '8px'
                }}
              >
                <div style={{ color: 'var(--nebula-text-muted)', fontSize: '13px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {item.label}
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: '36px', fontWeight: '800', color: 'var(--nebula-text)', fontFamily: 'var(--nebula-font-display), sans-serif' }}>
                    {item.count}
                  </div>
                  <span style={{ fontSize: '12px', fontWeight: '600', color: item.color, backgroundColor: item.bg, padding: '4px 10px', borderRadius: '20px' }}>
                    {item.label.split(' ')[0]}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom Row: 2-Column Grid for Filter Form (Left) & Risk Chart (Right) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '28px', width: '100%' }}>
            {/* Filter Form Card */}
            <div style={{ 
              backgroundColor: 'var(--nebula-bg-glass)', 
              padding: '28px', 
              borderRadius: '1.25rem', 
              border: '1px solid var(--nebula-border)', 
              boxShadow: '0 4px 15px var(--nebula-shadow-glass)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}>
              <div>
                <h3 style={{ fontFamily: 'var(--nebula-font-display), sans-serif', fontSize: '1.25rem', fontWeight: '700', color: 'var(--nebula-text)', margin: '0 0 4px' }}>
                  {t('instructor.exam_filtration', 'Exam Filter & Parameters')}
                </h3>
                <p style={{ color: 'var(--nebula-text-muted)', fontSize: '0.875rem', margin: '0 0 24px' }}>
                  Select parameters to narrow down exam results and analytics.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '20px' }}>
                  <div style={getFilterStyle('faculty')}>
                    <SearchableSelect
                      options={options.faculties}
                      value={filters.faculty}
                      onChange={(val: string) => { setFilters({...filters, faculty: val}); setErrors({...errors, faculty: false})}}
                      placeholder={t('instructor.select_grade', 'Select Grade')}
                    />
                  </div>
                  <div style={getFilterStyle('major')}>
                    <SearchableSelect
                      options={options.majors}
                      value={filters.major}
                      onChange={(val: string) => { setFilters({...filters, major: val}); setErrors({...errors, major: false})}}
                      placeholder={t('instructor.select_section', 'Select Section')}
                    />
                  </div>
                  <div style={getFilterStyle('course')}>
                    <SearchableSelect 
                      options={options.courses}
                      value={filters.course}
                      onChange={(val: string) => { setFilters({...filters, course: val}); setErrors({...errors, course: false})}}
                      placeholder={t('instructor.select_material', 'Select Material')}
                    />
                  </div>
                  <div style={getFilterStyle('class')}>
                    <SearchableSelect
                      options={options.classes}
                      value={filters.class}
                      onChange={(val: string) => { setFilters({...filters, class: val}); setErrors({...errors, class: false})}}
                      placeholder={t('instructor.select_division', 'Select Division')}
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <label style={{ fontSize: '13px', fontWeight: '600', color: 'var(--nebula-accent-cyan)', marginBottom: '6px' }}>
                      {t('instructor.from_date', 'From Date')}
                    </label>
                    <DatePicker
                      selected={parseDate(filters.fromDate)}
                      onChange={(date: Date | null) => setFilters({...filters, fromDate: formatDate(date)})}
                      dateFormat="yyyy-MM-dd"
                      placeholderText=""
                      className="custom-datepicker"
                      wrapperClassName="datePickerWrapper"
                    />
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <label style={{ fontSize: '13px', fontWeight: '600', color: 'var(--nebula-accent-cyan)', marginBottom: '6px' }}>
                      {t('instructor.to_date', 'To Date')}
                    </label>
                    <DatePicker
                      selected={parseDate(filters.toDate)}
                      onChange={(date: Date | null) => setFilters({...filters, toDate: formatDate(date)})}
                      dateFormat="yyyy-MM-dd"
                      placeholderText=""
                      className="custom-datepicker"
                      wrapperClassName="datePickerWrapper"
                    />
                  </div>
                </div>
              </div>

              <button 
                onClick={handleExecute}
                style={{ 
                  width: '100%', 
                  padding: '14px 28px', 
                  backgroundColor: 'var(--nebula-accent-cyan)', 
                  color: 'var(--nebula-bg-glass)', 
                  border: 'none', 
                  borderRadius: '0.75rem', 
                  fontFamily: 'var(--nebula-font-body), sans-serif',
                  fontWeight: '700', 
                  fontSize: '1rem',
                  cursor: 'pointer', 
                  boxShadow: '0 4px 15px rgba(44, 82, 130, 0.25)',
                  transition: 'all 0.2s ease'
                }}
              >
                {t('instructor.exam_filtration', 'Execute Exam Filtration')} &rarr;
              </button>
            </div>

            {/* Risk Distribution Pie Chart Card */}
            <div style={{ 
              backgroundColor: 'var(--nebula-bg-glass)', 
              padding: '28px', 
              borderRadius: '1.25rem', 
              border: '1px solid var(--nebula-border)', 
              minHeight: '380px', 
              boxShadow: '0 4px 15px var(--nebula-shadow-glass)',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <h3 style={{ fontFamily: 'var(--nebula-font-display), sans-serif', fontSize: '1.25rem', fontWeight: '700', color: 'var(--nebula-text)', margin: '0 0 4px', textAlign: 'start' }}>
                {t('instructor.risk.distribution_title', 'Student Risk Distribution')}
              </h3>
              <p style={{ color: 'var(--nebula-text-muted)', fontSize: '0.875rem', margin: '0 0 20px', textAlign: 'start' }}>
                Visual breakdown of student performance indicators.
              </p>

              <div style={{ flex: 1, minHeight: '260px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={[
                        { name: t('instructor.risk.stable', 'Stable'), value: riskSummary.stable ?? 0, color: 'var(--nebula-success)' },
                        { name: t('instructor.risk.at_risk', 'At Risk'), value: riskSummary.at_risk ?? 0, color: 'var(--nebula-warning)' },
                        { name: t('instructor.risk.critical', 'Critical'), value: riskSummary.critical ?? 0, color: 'var(--nebula-danger)' }
                      ]}
                      cx="50%"
                      cy="45%"
                      outerRadius={95}
                      innerRadius={45}
                      fill="var(--nebula-accent-purple)"
                      dataKey="value"
                      label
                    >
                      {[
                        { color: 'var(--nebula-success)' },
                        { color: 'var(--nebula-warning)' },
                        { color: 'var(--nebula-danger)' }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sub-nav tabs for Exams & Marks vs Learning Outcomes */}
      <div style={{ display: 'flex', gap: '24px', borderBottom: '2px solid var(--nebula-border)', marginTop: '32px', marginBottom: '24px' }}>
        <NavLink to="exams-marks" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--nebula-accent-cyan)' : 'var(--nebula-text-muted)', paddingBottom: '12px', fontWeight: isActive ? '700' : '600', borderBottom: isActive ? '3px solid var(--nebula-accent-cyan)' : 'none', marginBottom: '-2px', fontFamily: 'var(--nebula-font-display), sans-serif', fontSize: '1rem' })}>
          {t('instructor.exams_marks', 'Exams and Marks')}
        </NavLink>
        <NavLink to="learning-outcomes" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? 'var(--nebula-accent-cyan)' : 'var(--nebula-text-muted)', paddingBottom: '12px', fontWeight: isActive ? '700' : '600', borderBottom: isActive ? '3px solid var(--nebula-accent-cyan)' : 'none', marginBottom: '-2px', fontFamily: 'var(--nebula-font-display), sans-serif', fontSize: '1rem' })}>
          {t('instructor.learning_outcomes', 'Learning Outcomes')}
        </NavLink>
      </div>

      {/* 2. OPTIONAL CONTEXT */}
      {step === 3 && selectedExam && (
        <div style={{ marginBottom: '24px', padding: '24px', backgroundColor: 'var(--nebula-bg-glass)', borderRadius: '0.75rem', border: '1px solid var(--nebula-border)' }}>
          <div style={{ marginBottom: '16px', fontSize: '14px', lineHeight: '1.6', color: 'var(--nebula-text)' }}>
            <strong>{t('instructor.exam_name', 'Exam Name')}:</strong> {selectedExam.name} | 
            <strong> {t('instructor.date', 'Date')}:</strong> {selectedExam.date ? selectedExam.date.split('T')[0] : ''} | 
            <strong> {t('instructor.status', 'Status')}:</strong> {selectedExam.status} | 
            <strong> {t('instructor.applicants', 'Applicants')}:</strong> {selectedExam.applicants || 0} | 
            <strong> {t('instructor.examinees', 'Examinees')}:</strong> {selectedExam.examinees || 0}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', gap: '15px' }}>
              {['All', 'Attended', 'Not Attended', 'In Exam'].map(status => (
                <label key={status} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', fontSize: '14px', fontWeight: '500' }}>
                  <input 
                    type="radio" 
                    name="attendanceStatus" 
                    value={status} 
                    checked={attendanceStatus === status}
                    onChange={(e) => setAttendanceStatus(e.target.value)}
                    style={{ marginRight: '6px' }} 
                  />
                  {t(`instructor.${status.toLowerCase().replace(/\s+/g, '_')}`, status)}
                </label>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <span style={{ fontSize: '13px', color: 'var(--nebula-text-muted)' }}>Display 10 records per page</span>
              <input type="text" placeholder="Search..." style={{ padding: '6px 12px', border: '1px solid var(--nebula-border-strong)', borderRadius: '0.5rem', fontSize: '14px' }} />
            </div>
          </div>
        </div>
      )}

      {/* 3. CONTENT AREA */}
      <div style={{ marginTop: '20px' }}>
        <Outlet context={{ filters, triggerFetch, promoteStep, step, onDataLoaded: handleDataLoaded, selectedExam, setSelectedExam, attendanceStatus, setAttendanceStatus }} />
      </div>
    </div>
  );
};

export default InstructorsDashboard;
