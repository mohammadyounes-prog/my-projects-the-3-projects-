import React, { Suspense, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './App.css'; // Global styles

// Import page components
import LoginPage from './pages/Login.tsx';
import LandingPage from './pages/LandingPage.tsx';
import HomePage from './pages/HomePage.tsx';
import DashboardPage from './pages/Dashboard.tsx';
import ExecutiveDashboard from './pages/ExecutiveDashboard.tsx';
import CorporateDashboard from './pages/CorporateDashboard.tsx';
import SettingsPage from './pages/Settings.tsx';
import WeightsPage from './pages/Weights.tsx';

// Import layout components
import Layout from './components/layout/Layout.tsx';
import EducationalLayout from './components/layout/EducationalLayout.tsx';
import ProtectedRoute from './components/ProtectedRoute.tsx';

// Import Instructors dashboard page
import InstructorsDashboard from './pages/InstructorsDashboard.tsx';
import ExamsAndMarks from './pages/ExamsAndMarks.tsx';
import ExamResultsPage from './pages/ExamResultsPage.tsx';

// Import i18n setup
import './i18n/index.ts'; 

// Internal component to handle SSO redirect from website hub (?sso_token=)
// Contract: GET {API_BASE}/auth/verify-sso?sso_token=… → { access_token, … }
const SsoHandler = () => {
    const navigate = useNavigate();
    const isVerifying = React.useRef(false);

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const ssoToken = urlParams.get('sso_token');
        
        if (ssoToken && !isVerifying.current) {
            isVerifying.current = true;

            // Same base as Login (`REACT_APP_API_BASE_URL` + `/auth/...`); API_URL is an alias.
            const apiBase =
                process.env.REACT_APP_API_BASE_URL ||
                process.env.REACT_APP_API_URL ||
                'http://localhost:6018/api/v1';
            
            axios.get(`${apiBase}/auth/verify-sso`, { params: { sso_token: ssoToken } })
                .then(res => {
                    const { access_token, role, name } = res.data;
                    if (!access_token) {
                        throw new Error('verify-sso response missing access_token');
                    }
                    localStorage.setItem('token', access_token);
                    if (role) localStorage.setItem('role', role);
                    if (name) localStorage.setItem('user_name', name);
                    // Remove sso_token from URL to prevent re-processing
                    window.history.replaceState({}, document.title, window.location.pathname);
                    navigate('/home');
                })
                .catch(err => {
                    console.error("SSO verification failed", err);
                })
                .finally(() => {
                    isVerifying.current = false;
                });
        }
    }, [navigate]);
    return null;
};

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Router>
        <SsoHandler />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          {/* Protected routes wrapped by a Layout component */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Layout />}>
              {/* `/` and `/home` share one gateway layout (LandingPage / HomePage wrappers) */}
              <Route index element={<LandingPage />} />
              <Route path="home" element={<HomePage />} />
              <Route path="educational" element={<EducationalLayout />}>
                <Route path="admins" element={<DashboardPage />} />
                <Route path="instructors" element={<InstructorsDashboard />}>
                  <Route path="exams-marks" element={<ExamsAndMarks />} />
                </Route>
                <Route path="exam-results/:examId" element={<ExamResultsPage />} />
              </Route>
              <Route path="executive-dashboard" element={<ExecutiveDashboard />} />
              <Route path="corporate-dashboard" element={<CorporateDashboard />} />
              <Route path="weights" element={<WeightsPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Route>
          
          {/* Catch-all or 404 route could be added here */}
        </Routes>
      </Router>
    </Suspense>
  );
}

export default App;
