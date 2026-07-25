import React, { useEffect, useState } from 'react';
import { useOutletContext, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import Modal from 'react-modal';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import HelpTooltip from '../components/common/HelpTooltip.tsx';

Modal.setAppElement('#root');

interface Filters {
  faculty: string;
  major: string;
  course: string;
  class: string;
  fromDate: string;
  toDate: string;
  exam: string;
}

const ExamsAndMarks = () => {
  const navigate = useNavigate();
  const { filters, triggerFetch, promoteStep, step, onDataLoaded, selectedExam, setSelectedExam, attendanceStatus, setAttendanceStatus } = useOutletContext<{ 
    filters: Filters, 
    triggerFetch: boolean, 
    promoteStep: (s: number) => void, 
    step: number,
    onDataLoaded: (count: number) => void,
    selectedExam: any,
    setSelectedExam: (exam: any) => void,
    attendanceStatus: string,
    setAttendanceStatus: (s: string) => void
  }>();
  const { t, i18n } = useTranslation();
  console.log("Current Language:", i18n.language);
  console.log("Available translations for instructor:", i18n.store.data[i18n.language]?.translation?.instructor);
  const [data, setData] = useState<any[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [examStats, setExamStats] = useState<any>(null);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [studentDetails, setStudentDetails] = useState<any>(null);

  const openViewModal = (student: any) => {
    setSelectedStudent(student);
    setModalIsOpen(true);
    axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/exams/student-result-details?exam_id=${selectedExam.id}&student_id=${student.studentId}`)
      .then(res => {
        console.log("Modal data received:", res.data);
        setStudentDetails(res.data);
      })
      .catch(err => console.error("Error fetching modal details:", err));
  };

  const closeViewModal = () => {
    setSelectedStudent(null);
    setModalIsOpen(false);
  };

  // Pagination & Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    const username = localStorage.getItem('user_name') || '';
    const params = new URLSearchParams({
      username: username,
      ...(filters.faculty && { faculty_id: filters.faculty }),
      ...(filters.major && { major_id: filters.major }),
      ...(filters.course && { course_id: filters.course }),
      ...(filters.class && { class_id: filters.class }),
      ...(filters.fromDate && { from_date: filters.fromDate }),
      ...(filters.toDate && { to_date: filters.toDate })
    });

    const baseUrl = `${process.env.REACT_APP_API_BASE_URL}/data/exams/grid`;
    axios.get(`${baseUrl}?${params.toString()}`)
      .then(response => {
        setData(response.data);
        setLoading(false);
        if (onDataLoaded) onDataLoaded(response.data.length);
      })
      .catch(err => {
        console.error("Error fetching exams grid:", err);
        setLoading(false);
        if (onDataLoaded) onDataLoaded(0);
      });
    // 2. Fetch Trend Data
    const trendParams = new URLSearchParams({
      ...(filters.course && { course_id: filters.course }),
      ...(filters.fromDate && { from_date: filters.fromDate }),
      ...(filters.toDate && { to_date: filters.toDate })
    });
    axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/exams/trend?${trendParams.toString()}`)
      .then(response => setTrendData(response.data))
      .catch(err => console.error("Error fetching trend data:", err));
  }, [triggerFetch, filters, onDataLoaded]);

  const handleChoose = (exam: any) => {
    setSelectedExam(exam);
    promoteStep(3); 
    setLoading(true);
    setExamStats(null); // Clear previous stats

    axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/exams/results-detail?exam_id=${exam.id}`)
      .then(response => {
        setResults(response.data);
        setLoading(false);
      })
      .catch(err => { console.error("Error fetching results:", err); setLoading(false); });

    axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/exams/${exam.id}/statistics`)
      .then(response => {
        setExamStats(response.data);
      })
      .catch(err => console.error("Error fetching stats:", err));
  };

  // Pagination State for Step 3
  const [resultsCurrentPage, setResultsCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const itemsPerPage = pageSize; // Define itemsPerPage for use in pagination calculations

  const handleBack = () => promoteStep(2);

  console.log("Rendering step 3, examStats:", examStats);

  const filteredData = data.filter(item => item.name.toLowerCase().includes(searchQuery.toLowerCase()));
  const totalPages = Math.ceil(filteredData.length / pageSize);
  const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const filteredResults = results.filter(r => {
    if (attendanceStatus === 'All') return true;
    if (attendanceStatus === 'Attended') return r.startTime !== null;
    if (attendanceStatus === 'Not Attended') return r.resultId === null;
    if (attendanceStatus === 'In Exam') return r.startTime !== null && r.status === 'notComplete';
    return true;
  });

  const paginatedResults = filteredResults.slice((resultsCurrentPage - 1) * pageSize, (resultsCurrentPage - 1) * pageSize + pageSize);
  const totalResultsPages = Math.ceil(filteredResults.length / pageSize);
  const tdStyle = { padding: '5px', border: '1px solid var(--nebula-border)', fontSize: '12px' };
  const thStyle = { padding: '5px', border: '1px solid var(--nebula-border)', fontSize: '12px', background: 'var(--nebula-bg-raised)' };

  return (
    <div style={{ marginTop: '20px' }}>
      {step === 2 && (loading ? <p>{t('common.loading')}</p> : (
        <div>
          {trendData && trendData.length > 0 && (
            <div style={{ background: 'transparent', padding: '20px', borderRadius: '8px', border: '1px solid var(--nebula-border)', height: '300px', marginBottom: '30px' }}>
                <h4 style={{ textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                    {t('instructor.performance_trend', 'Performance Trend')}
                    <HelpTooltip 
                      title={t('instructor.performance_trend', 'Performance Trend')}
                      description={t('instructor.stats.trend_tooltip_desc', 'Visualizes class average performance across selected exams over time.')}
                      benefit={t('instructor.stats.trend_tooltip_benefit', 'Helps identify long-term improvement or decline patterns.')}
                    />
                </h4>
                <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" fontSize={10} label={{ value: t('instructor.stats.date', 'Date'), position: 'bottom', offset: 0, fontSize: 12 }} />
                    <YAxis fontSize={10} domain={[0, 100]} label={{ value: t('instructor.stats.avg', 'Average'), angle: -90, position: 'insideLeft', fontSize: 12 }} />
                    <Tooltip formatter={(value: any) => [value, t('instructor.stats.avg', 'Average')]} />
                    <Line type="monotone" dataKey="avg" stroke="var(--nebula-accent-cyan)" strokeWidth={2} />
                </LineChart>
                </ResponsiveContainer>
            </div>
          )}

          <div style={{ marginBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <input type="text" placeholder={t('instructor.search_exams', 'Search exams...')} value={searchQuery} onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }} style={{ padding: '5px', width: '200px' }} />
            <div>
              <span>{t('instructor.display_records_prefix', 'Display ')}</span>
              <input 
                type="number" 
                value={pageSize} 
                onChange={(e) => { setPageSize(Number(e.target.value)); setCurrentPage(1); }} 
                style={{ width: '50px', padding: '5px', marginRight: '5px' }}
              />
              <span>{t('instructor.records_per_page', 'records per page')}</span>
            </div>
            <span>{t('instructor.total_exams', 'Total Exams')}: {filteredData.length}</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', minWidth: '760px' }}>
            <thead>
              <tr>
                <th style={thStyle}>{t('instructor.name', 'Name')}</th>
                <th style={thStyle}>{t('instructor.grade', 'Grade')}</th>
                <th style={thStyle}>{t('instructor.material', 'Material')}</th>
                <th style={thStyle}>{t('instructor.division', 'Division')}</th>
                <th style={thStyle}>{t('instructor.date', 'Date')}</th>
                <th style={thStyle}>{t('instructor.status', 'Status')}</th>
                <th style={thStyle}>{t('instructor.applicants', 'Applicants')}</th>
                <th style={thStyle}>{t('instructor.examinees', 'Examinees')}</th>
                <th style={thStyle}>{t('instructor.action', 'Action')}</th>
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((item, index) => (
                <tr key={index}>
                  <td style={tdStyle}>{item.name}</td><td style={tdStyle}>{item.grade}</td><td style={tdStyle}>{item.material}</td><td style={tdStyle}>{item.division}</td>
                  <td style={tdStyle}>{item.date ? item.date.split('T')[0] : ''}</td><td style={tdStyle}>{item.status}</td><td style={tdStyle}>{item.applicants}</td><td style={tdStyle}>{item.examinees}</td>
                  <td style={tdStyle}>
                    <button onClick={() => handleChoose(item)} style={{ backgroundColor: 'var(--nebula-accent-cyan)', color: 'var(--nebula-bg-deep)', border: 'none', padding: '2px 5px', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}>{t('instructor.choose', 'Choose')}</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
          <div style={{ marginTop: '10px', display: 'flex', gap: '5px' }}>
            {Array.from({ length: totalPages }, (_, i) => (
              <button key={i} onClick={() => setCurrentPage(i + 1)} style={{ padding: '5px 10px', backgroundColor: currentPage === i + 1 ? 'var(--nebula-accent-cyan)' : 'var(--nebula-border)' }}>{i + 1}</button>
            ))}
          </div>
        </div>
      ))}

      {step === 3 && selectedExam && (
          <div>
            <button onClick={handleBack} style={{ marginBottom: '10px', padding: '5px 10px', cursor: 'pointer', backgroundColor: 'var(--nebula-bg-raised)', color: 'var(--nebula-text)', border: '1px solid var(--nebula-border)', borderRadius: '4px' }}>&larr; {t('instructor.back_to_selection', 'Back to Selection')}</button>
            
            <h3>{t('instructor.results_for', 'Results for')}: {selectedExam.name}</h3>
            <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', minWidth: '640px' }}>
              <thead>
                <tr>
                  <th style={thStyle}>{t('instructor.no', 'No')}</th>
                  <th style={thStyle}>{t('instructor.xId', 'xId')}</th>
                  <th style={thStyle}>{t('instructor.name', 'Name')}</th>
                  <th style={thStyle}>{t('instructor.mark', 'Mark')}</th>
                  <th style={thStyle}>{t('instructor.order', 'Order')}</th>
                  <th style={thStyle}>{t('instructor.answered', 'Answered')}</th>
                  <th style={thStyle}>{t('instructor.true', 'True')}</th>
                  <th style={thStyle}>{t('instructor.false', 'False')}</th>
                  <th style={thStyle}>{t('instructor.action', 'Action')}</th>
                </tr>
              </thead>
              <tbody>
                {paginatedResults.map((r, i) => (
                <tr key={i}>
                  <td style={tdStyle}>{i + 1 + (resultsCurrentPage - 1) * itemsPerPage}</td>
                  <td style={tdStyle}>{r.studentXId}</td>
                  <td style={tdStyle}>{r.studentName}</td>
                  <td style={tdStyle}>{r.mark}</td>
                  <td style={tdStyle}>{r.studentOrder}</td>
                  <td style={tdStyle}>{r.answered}</td>
                  <td style={tdStyle}>{r.true_ans}</td>
                  <td style={tdStyle}>{r.false_ans}</td>
                  <td style={tdStyle}>
                    <button onClick={() => openViewModal(r)} style={{ backgroundColor: 'var(--nebula-success)', color: '#fff', border: 'none', padding: '1px 4px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer', lineHeight: '1' }}>
                      <span style={{ fontSize: '14px', verticalAlign: 'middle' }}>👁</span> {t('instructor.view', 'View')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
          <div style={{ marginTop: '10px', display: 'flex', gap: '5px' }}>
            {Array.from({ length: totalResultsPages }, (_, i) => (
              <button key={i} onClick={() => setResultsCurrentPage(i + 1)} style={{ padding: '5px 10px', backgroundColor: resultsCurrentPage === i + 1 ? 'var(--nebula-accent-cyan)' : 'var(--nebula-border)' }}>{i + 1}</button>
            ))}
          </div>

          {/* Statistics Cards and Chart */}
          {examStats && !examStats.message && (
            <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
              {/* Cards */}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {[
                  { label: t('instructor.stats.average', 'Average'), value: examStats.average },
                  { label: t('instructor.stats.median', 'Median'), value: examStats.median },
                  { label: t('instructor.stats.stdev', 'Std Deviation'), value: examStats.standard_deviation }
                ].map((stat, i) => (
                  <div key={i} style={{ background: 'transparent', padding: '15px', borderRadius: '8px', border: '1px solid var(--nebula-border)', textAlign: 'center' }}>
                    <div style={{ color: 'var(--nebula-text-muted)', fontSize: '12px' }}>{stat.label}</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--nebula-accent-cyan)' }}>{stat.value}</div>
                  </div>
                ))}
              </div>
              
              {/* Histogram Chart */}
                <div style={{ flex: 2, background: 'transparent', padding: '20px', borderRadius: '8px', border: '1px solid var(--nebula-border)', height: '250px', position: 'relative' }}>
                  <h4 style={{ margin: '0 0 10px 0', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                      {t('instructor.stats.grade_distribution', 'Grade Distribution')}
                      <HelpTooltip 
                        title={t('instructor.stats.tooltip_title', 'Grade Distribution')}
                        description={t('instructor.stats.tooltip_desc', 'Average, Median, and Standard Deviation help visualize the class performance spread.')}
                        benefit={t('instructor.stats.tooltip_benefit', 'Red dashed lines indicate the 1-SD range from the mean.')}
                      />
                  </h4>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={examStats.histogram}>
                      <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="range" 
                      fontSize={10} 
                      name={t('instructor.stats.mark_range')}
                      label={{ value: t('instructor.stats.mark_range'), position: 'bottom', offset: 0, fontSize: 12 }} 
                    />
                    <YAxis 
                      fontSize={10} 
                      name={t('instructor.stats.frequency')}
                      label={{ value: t('instructor.stats.frequency'), angle: -90, position: 'insideLeft', fontSize: 12 }} 
                    />
                    <Tooltip formatter={(value: any) => [value, t('instructor.stats.frequency')]} />
                    <Bar dataKey="count" name={t('instructor.stats.frequency')} fill="var(--nebula-accent-cyan)" />                      <ReferenceLine x={`${Math.max(0, Math.floor((examStats.average - examStats.standard_deviation) / 10) * 10)}-${Math.max(0, Math.floor((examStats.average - examStats.standard_deviation) / 10) * 10 + 10)}`} stroke="red" strokeDasharray="3 3" />
                      <ReferenceLine x={`${Math.min(9, Math.floor((examStats.average + examStats.standard_deviation) / 10)) * 10}-${Math.min(9, Math.floor((examStats.average + examStats.standard_deviation) / 10)) * 10 + 10}`} stroke="red" strokeDasharray="3 3" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>            </div>
          )}
        </div>
      )}

      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeViewModal}
        style={{
          overlay: { backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 1000 },
          content: {
            width: '80%', margin: 'auto', maxHeight: '90%', overflow: 'auto',
            background: 'var(--nebula-bg-raised)', color: 'var(--nebula-text)',
            border: '1px solid var(--nebula-border)', borderRadius: '12px'
          }
        }}
      >
        <h3 style={{ background: 'var(--nebula-bg-glass)', color: 'var(--nebula-accent-cyan)', padding: '10px', borderRadius: '5px' }}>{t('instructor.student_details', 'Student Details')}: {studentDetails?.summary.studentName}</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: 'var(--nebula-bg-glass)', padding: '15px', borderRadius: '5px' }}>
          <span><strong>{t('instructor.name', 'Name')}:</strong> {studentDetails?.summary.studentName}</span>
          <span><strong>{t('instructor.id', 'ID')}:</strong> {studentDetails?.summary.studentXId}</span>
          <span><strong>{t('instructor.mark', 'Mark')}:</strong> {studentDetails?.summary.mark}</span>
          <span><strong>{t('instructor.true', 'True')}:</strong> {studentDetails?.summary.true_ans}</span>
          <span><strong>{t('instructor.false', 'False')}:</strong> {studentDetails?.summary.false_ans}</span>
          <span><strong>{t('instructor.not_corrected', 'Not Corrected')}:</strong> {studentDetails?.summary.not_corrected}</span>
          <span><strong>{t('instructor.unanswered', 'Unanswered')}:</strong> {studentDetails?.summary.unanswered}</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', marginTop: '20px', borderCollapse: 'collapse', minWidth: '800px' }}>
          <thead>
            <tr style={{ background: 'var(--nebula-bg-glass)' }}>
              <th>{t('instructor.question_text', 'Question Text')}</th>
              <th>{t('instructor.answers', 'Answers')}</th>
              <th>{t('instructor.question_mark', 'Question Mark')}</th>
              <th>{t('instructor.student_mark', 'Student Mark')}</th>
              <th>{t('instructor.correct_index', 'Correct Index')}</th>
              <th>{t('instructor.correct_text', 'Correct Text')}</th>
              <th>{t('instructor.student_ans_index', 'Stud. Ans Index')}</th>
              <th>{t('instructor.student_ans_text', 'Stud. Ans Text')}</th>
              <th>{t('instructor.question_status', 'Question Status')}</th>
            </tr>
          </thead>
          <tbody>
            {studentDetails?.details.map((d: any, i: number) => {
              let parsedAnswers = [];
              try { 
                  const data = JSON.parse(d.answers);
                  parsedAnswers = Array.isArray(data) ? data : [];
              } catch (e) { console.error("Error parsing answers:", e); }
              
              const correctIdx = String(d.correctIndex);
              
              // Robust matching: try index property, then try array position as fallback
              const correctAnswer = parsedAnswers.find((a: any, idx: number) => {
                  const matchByIndex = a.index !== undefined && String(a.index) === correctIdx;
                  const matchByPosition = String(idx + 1) === correctIdx;
                  return matchByIndex || matchByPosition;
              });
              
              return (
                <tr key={i}>
                  <td>{d.questionText}</td>
                  <td>
                    {parsedAnswers.map((a: any, idx: number) => (
                        <div key={idx}>{a.index || idx + 1}: {a.text || a}</div>
                    ))}
                  </td>
                  <td>{d.questionMark}</td>
                  <td>{d.studentMark}</td>
                  <td>{d.correctIndex}</td>
                  <td>{correctAnswer ? (correctAnswer.text || correctAnswer) : 'N/A'}</td>
                  <td>{d.answerIndex}</td>
                  <td>{d.answerText}</td>
                  <td style={{ color: d.status === 'correct' ? 'green' : 'red' }}>{d.status.toUpperCase()}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        </div>
        <button onClick={closeViewModal} style={{ marginTop: '20px', padding: '6px 14px', backgroundColor: 'var(--nebula-bg-glass)', color: 'var(--nebula-text)', border: '1px solid var(--nebula-border)', borderRadius: '6px', cursor: 'pointer' }}>{t('common.cancel', 'Close')}</button>
      </Modal>
    </div>
  );
};

export default ExamsAndMarks;