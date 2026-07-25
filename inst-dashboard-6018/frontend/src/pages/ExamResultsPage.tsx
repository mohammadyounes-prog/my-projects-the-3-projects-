import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Modal from 'react-modal';

Modal.setAppElement('#root');

const ExamResultsPage = () => {
  const { examId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<any>(null);
  const [studentDetails, setStudentDetails] = useState<any>(null);
  const [attendanceStatus, setAttendanceStatus] = useState('All');

  useEffect(() => {
    if (examId) {
      axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/exams/results-detail?exam_id=${examId}`)
        .then(res => {
          setResults(res.data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Error fetching results:", err);
          setLoading(false);
        });
    }
  }, [examId]);

  const openViewModal = (student: any) => {
    setSelectedStudent(student);
    setModalIsOpen(true);
    axios.get(`${process.env.REACT_APP_API_BASE_URL}/data/exams/student-result-details?exam_id=${examId}&student_id=${student.studentId}`)
      .then(res => {
        console.log("Student details received:", res.data);
        setStudentDetails(res.data);
      })
      .catch(err => console.error("Error fetching details:", err));
  };

  const [recordsPerPage, setRecordsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  const filteredResults = results.filter(r => {
    if (attendanceStatus === 'All') return true;
    if (attendanceStatus === 'Attended') return r.startTime !== null;
    if (attendanceStatus === 'Not Attended') return r.resultId === null;
    if (attendanceStatus === 'In Exam') return r.startTime !== null && r.status === 'notComplete';
    return true;
  });

  const totalPages = Math.ceil(filteredResults.length / recordsPerPage);
  const paginatedResults = filteredResults.slice((currentPage - 1) * recordsPerPage, currentPage * recordsPerPage);

  const thStyle = { padding: '10px', borderBottom: '2px solid var(--nebula-border)', textAlign: 'left' as const };
  const tdStyle = { padding: '10px', borderBottom: '1px solid var(--nebula-border)' };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span>Display</span>
          <select value={recordsPerPage} onChange={(e) => { setRecordsPerPage(Number(e.target.value)); setCurrentPage(1); }}>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
          <span>records per page</span>
        </div>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', minWidth: '900px' }}>
          <thead>
            <tr>
              <th style={thStyle}>No</th><th style={thStyle}>xId</th><th style={thStyle}>Name</th><th style={thStyle}>Mark</th>
              <th style={thStyle}>Order</th><th style={thStyle}>Answered</th><th style={thStyle}>True</th>
              <th style={thStyle}>False</th><th style={thStyle}>Not Corrected</th><th style={thStyle}>Start Time</th>
              <th style={thStyle}>Take Time</th><th style={thStyle}>Action</th>
            </tr>
          </thead>
          <tbody>
            {paginatedResults.map((r, i) => (
              <tr key={i}>
                <td style={tdStyle}>{i + 1}</td><td style={tdStyle}>{r.studentXId}</td><td style={tdStyle}>{r.studentName}</td>
                <td style={tdStyle}>{r.mark}</td><td style={tdStyle}>{r.studentOrder}</td><td style={tdStyle}>{r.answered}</td>
                <td style={tdStyle}>{r.true_ans}</td><td style={tdStyle}>{r.false_ans}</td><td style={tdStyle}>{r.not_corrected}</td>
                <td style={tdStyle}>{r.startTime}</td><td style={tdStyle}>{r.takeTime}s</td>
                <td style={tdStyle}>
                  <button onClick={() => openViewModal(r)} style={{ backgroundColor: 'var(--nebula-success)', color: '#fff', padding: '2px 8px', borderRadius: '4px', cursor: 'pointer', border: 'none' }}>
                    <span style={{ fontSize: '14px', verticalAlign: 'middle' }}>👁</span> View
                  </button>
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

      <Modal
        isOpen={modalIsOpen}
        onRequestClose={() => setModalIsOpen(false)}
        style={{
          overlay: { backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 1000 },
          content: {
            width: '80%', margin: 'auto', maxHeight: '90%', overflow: 'auto',
            background: 'var(--nebula-bg-raised)', color: 'var(--nebula-text)',
            border: '1px solid var(--nebula-border)', borderRadius: '12px'
          }
        }}
      >
        <h3>Student Details: {studentDetails?.summary.studentName}</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: 'var(--nebula-bg-glass)', padding: '15px', borderRadius: '5px' }}>
          <span><strong>Name:</strong> {studentDetails?.summary.studentName}</span>
          <span><strong>ID:</strong> {studentDetails?.summary.studentXId}</span>
          <span><strong>Mark:</strong> {studentDetails?.summary.mark}</span>
          <span><strong>True:</strong> {studentDetails?.summary.true_ans}</span>
          <span><strong>False:</strong> {studentDetails?.summary.false_ans}</span>
          <span><strong>Not Corrected:</strong> {studentDetails?.summary.not_corrected}</span>
          <span><strong>Unanswered:</strong> {studentDetails?.summary.unanswered}</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', marginTop: '20px', borderCollapse: 'collapse', minWidth: '800px' }}>
          <thead>
            <tr style={{ background: 'var(--nebula-border)', textAlign: 'left' }}>
              <th style={{ padding: '8px' }}>Question Text</th>
              <th style={{ padding: '8px' }}>Answers</th>
              <th style={{ padding: '8px' }}>Q. Mark</th>
              <th style={{ padding: '8px' }}>Stud. Mark</th>
              <th style={{ padding: '8px' }}>Correct Index</th>
              <th style={{ padding: '8px' }}>Correct Text</th>
              <th style={{ padding: '8px' }}>Stud. Ans Index</th>
              <th style={{ padding: '8px' }}>Stud. Ans Text</th>
              <th style={{ padding: '8px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {studentDetails?.details.map((d: any, i: number) => {
              let parsedAnswers = [];
              try { 
                  const data = JSON.parse(d.answers);
                  parsedAnswers = Array.isArray(data) ? data : [];
              } catch (e) { console.error("Error parsing answers:", e); }
              
              // Finalized matching logic: Check `index` property or fallback to position
              const correctIdx = String(d.correctIndex);
              const correctAnswer = parsedAnswers.find((a: any, idx: number) => {
                  const matchByIndex = a.index !== undefined && String(a.index) === correctIdx;
                  const matchByPosition = String(idx + 1) === correctIdx;
                  return matchByIndex || matchByPosition;
              });
              
              return (
                <tr key={i} style={{ borderBottom: '1px solid var(--nebula-border)' }}>
                  <td style={{ padding: '8px' }}>{d.questionText}</td>
                  <td style={{ padding: '8px' }}>
                    {parsedAnswers.map((a: any, idx: number) => (
                        <div key={idx}>{a.index || (idx + 1)}: {a.text || a}</div>
                    ))}
                  </td>
                  <td style={{ padding: '8px' }}>{d.questionMark}</td>
                  <td style={{ padding: '8px' }}>{d.studentMark}</td>
                  <td style={{ padding: '8px' }}>{d.correctIndex}</td>
                  <td style={{ padding: '8px' }}>{correctAnswer ? (correctAnswer.text || correctAnswer) : 'N/A'}</td>
                  <td style={{ padding: '8px' }}>{d.answerIndex}</td>
                  <td style={{ padding: '8px' }}>{d.answerText}</td>
                  <td style={{ padding: '8px', color: d.status === 'correct' ? 'green' : 'red', fontWeight: 'bold' }}>
                    {d.status.toUpperCase()}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        </div>
        <button onClick={() => setModalIsOpen(false)} style={{ marginTop: '20px', padding: '6px 14px', backgroundColor: 'var(--nebula-bg-glass)', color: 'var(--nebula-text)', border: '1px solid var(--nebula-border)', borderRadius: '6px', cursor: 'pointer' }}>Close</button>
      </Modal>
    </div>
  );
};

export default ExamResultsPage;