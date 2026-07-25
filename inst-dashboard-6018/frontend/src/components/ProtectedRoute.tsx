import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { canAccess } from '../auth/roles.ts';

const ProtectedRoute = () => {
  const [isChecking, setIsChecking] = useState(true);
  const location = useLocation();
  const token = localStorage.getItem('token');
  const urlParams = new URLSearchParams(window.location.search);
  const ssoToken = urlParams.get('sso_token');

  useEffect(() => {
    // If an SSO token is in the URL, wait a moment for SsoHandler to process it
    if (ssoToken) {
      const timer = setTimeout(() => setIsChecking(false), 800);
      return () => clearTimeout(timer);
    } else {
      setIsChecking(false);
    }
  }, [ssoToken]);

  if (isChecking) return <div>Authenticating...</div>;

  // Allow through if token exists OR if we are currently processing an SSO token
  if (token || ssoToken) {
    // Soft role guard: forbidden module paths redirect to gateway (skip while SSO pending)
    if (token && !ssoToken && !canAccess(location.pathname)) {
      return <Navigate to="/home" replace />;
    }
    return <Outlet />;
  }

  return <Navigate to="/login" />;
};

export default ProtectedRoute;
