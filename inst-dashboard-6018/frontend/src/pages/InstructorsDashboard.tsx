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
    border: errors[key] ? '2px solid red' : '1px solid #ccc',
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
    border: '1px solid #ccc',
    width: '100%',
    boxSizing: 'border-box'
  };

  return (
    <div style={{ padding: '20px' }}>
      
        {/* 1. NAVIGATION TABS - ALWAYS VISIBLE */}
      <div style={{ display: 'flex', marginBottom: '20px', gap: '10px' }}>
        {['exam_selection', 'choose_exam', 'exam_results'].map((s, i) => {
          const stepIndex = i + 1;
          const isActive = step === stepIndex;
          const isVisited = stepIndex <= maxStep;
          return (
            <div key={s} 
              onClick={() => handleStepClick(stepIndex)}
              style={{ 
                padding: '5px 15px', 
                background: isActive ? '#003366' : (isVisited ? '#1677ff' : '#ddd'), 
                color: 'white',
                borderRadius: '15px',
                flex: 1,
                textAlign: 'center',
                cursor: isVisited ? 'pointer' : 'default',
                fontSize: '14px'
              }}>
              {t(`instructor.step_${stepIndex}`, `Step ${stepIndex}`)}: {t(`instructor.${s}`, s.replace('_', ' '))}
            </div>
          );
        })}
      </div>

      {step === 1 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', gap: '20px' }}>
            {[
                { label: t('instructor.risk.stable', 'Stable'), count: riskSummary.stable, color: '#52c41a' },
                { label: t('instructor.risk.at_risk', 'At Risk'), count: riskSummary.at_risk, color: '#faad14' },
                { label: t('instructor.risk.critical', 'Critical'), count: riskSummary.critical, color: '#f5222d' }
            ].map((item, i) => (
                <div key={i} style={{ background: '#fff', padding: '15px', borderRadius: '8px', border: `1px solid ${item.color}`, flex: 1, textAlign: 'center' }}>
                    <div style={{ color: item.color, fontSize: '14px', fontWeight: 'bold' }}>{item.label}</div>
                    <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#003366' }}>{item.count}</div>
                </div>
            ))}
          </div>

          {/* Risk Distribution Pie Chart */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #ddd', height: '300px' }}>
            <h4 style={{ textAlign: 'center' }}>{t('instructor.risk.distribution_title', 'Student Risk Distribution')}</h4>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: t('instructor.risk.stable', 'Stable'), value: riskSummary.stable, color: '#52c41a' },
                    { name: t('instructor.risk.at_risk', 'At Risk'), value: riskSummary.at_risk, color: '#faad14' },
                    { name: t('instructor.risk.critical', 'Critical'), value: riskSummary.critical, color: '#f5222d' }
                  ]}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label
                >
                  {[
                    { color: '#52c41a' },
                    { color: '#faad14' },
                    { color: '#f5222d' }
                  ].map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: '20px', borderBottom: '1px solid #ddd', marginBottom: '20px' }}>
        <NavLink to="exams-marks" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#1677ff' : '#666', paddingBottom: '10px', fontWeight: isActive ? 'bold' : 'normal' })}>
          {t('instructor.exams_marks', 'Exams and Marks')}
        </NavLink>
        <NavLink to="learning-outcomes" style={({ isActive }) => ({ textDecoration: 'none', color: isActive ? '#1677ff' : '#666', paddingBottom: '10px', fontWeight: isActive ? 'bold' : 'normal' })}>
          {t('instructor.learning_outcomes', 'Learning Outcomes')}
        </NavLink>
      </div>

      {/* 2. OPTIONAL CONTEXT - Conditionally rendered, but does not wrap navigation */}
      {step === 3 && selectedExam && (
        <div style={{ marginBottom: '20px', padding: '15px', background: '#f9f9f9', borderRadius: '8px', border: '1px solid #eee' }}>
          <div style={{ marginBottom: '15px', fontSize: '14px', lineHeight: '1.6' }}>
            <strong>{t('instructor.exam_name', 'Exam Name')}:</strong> {selectedExam.name} | 
            <strong>{t('instructor.date', 'Date')}:</strong> {selectedExam.date ? selectedExam.date.split('T')[0] : ''} | 
            <strong>{t('instructor.status', 'Status')}:</strong> {selectedExam.status} | 
            <strong>{t('instructor.applicants', 'Applicants')}:</strong> {selectedExam.applicants || 0} | 
            <strong>{t('instructor.examinees', 'Examinees')}:</strong> {selectedExam.examinees || 0}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '15px' }}>
              {['All', 'Attended', 'Not Attended', 'In Exam'].map(status => (
                <label key={status} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', fontSize: '14px' }}>
                  <input 
                    type="radio" 
                    name="attendanceStatus" 
                    value={status} 
                    checked={attendanceStatus === status}
                    onChange={(e) => setAttendanceStatus(e.target.value)}
                    style={{ marginRight: '5px' }} 
                  />
                  {t(`instructor.${status.toLowerCase().replace(/\s+/g, '_')}`, status)}
                </label>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <span>Display 10 records per page</span>
              <input type="text" placeholder="Search..." style={{ padding: '5px' }} />
            </div>
          </div>
        </div>
      )}

      {/* 3. CONTENT AREA */}
      <div style={{ marginTop: '20px' }}>
        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', width: '100%' }}>
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

            <div style={{ display: 'flex', gap: '10px', width: '100%' }}>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <label style={{ fontSize: '12px', marginBottom: '4px' }}>{t('instructor.from_date', 'From')}</label>
                <DatePicker
                  selected={parseDate(filters.fromDate)}
                  onChange={(date: Date | null) => setFilters({...filters, fromDate: formatDate(date)})}
                  dateFormat="yyyy-MM-dd"
                  placeholderText=""
                  className="custom-datepicker"
                  wrapperClassName="datePickerWrapper"
                />
              </div>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <label style={{ fontSize: '12px', marginBottom: '4px' }}>{t('instructor.to_date', 'To')}</label>
                <DatePicker
                  selected={parseDate(filters.toDate)}
                  onChange={(date: Date | null) => setFilters({...filters, toDate: formatDate(date)})}
                  dateFormat="yyyy-MM-dd"
                  placeholderText=""
                  className="custom-datepicker"
                  wrapperClassName="datePickerWrapper"
                />
              </div>              <button 
                onClick={handleExecute}
                style={{ padding: '0 20px', backgroundColor: '#1677ff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', whiteSpace: 'nowrap', marginLeft: 'auto' }}
              >
                {t('instructor.exam_filtration', 'Exam Filtration')}
              </button>
            </div>
          </div>
        )}
        <Outlet context={{ filters, triggerFetch, promoteStep, step, onDataLoaded: handleDataLoaded, selectedExam, setSelectedExam, attendanceStatus, setAttendanceStatus }} />
      </div>
    </div>
  );
};

export default InstructorsDashboard;
