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

// Add this temporary interceptor for debugging
axios.interceptors.request.use(config => {
    console.log("DEBUG: Axios interceptor URL:", config.url);
    return config;
}, error => {
    return Promise.reject(error);
});

// Internal component to handle SSO redirect
const SsoHandler = () => {
    const navigate = useNavigate();
    const isVerifying = React.useRef(false);

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const ssoToken = urlParams.get('sso_token');
        console.log("SsoHandler: Checking for SSO token:", ssoToken);
        
        if (ssoToken && !isVerifying.current) {
            isVerifying.current = true;
            console.log("SsoHandler: Starting verification for token:", ssoToken);
            
            const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:6018';
            
            axios.get(`${apiUrl}/verify-sso?sso_token=${ssoToken}`)
                .then(res => {
                    console.log("SsoHandler: Token verified successfully", res.data);
                    localStorage.setItem('token', res.data.access_token);
                    // Remove sso_token from URL to prevent re-processing
                    window.history.replaceState({}, document.title, window.location.pathname);
                    navigate('/home');
                })
                .catch(err => {
                    console.error("SSO verification failed", err);
                    // Optionally handle the error (e.g., show a message or redirect to login)
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
