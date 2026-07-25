import { Navigate, Outlet } from 'react-router-dom';
import { useState, useEffect } from 'react';

const ProtectedRoute = () => {
  const [isChecking, setIsChecking] = useState(true);
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
    return <Outlet />;
  }

  return <Navigate to="/login" />;
};

export default ProtectedRoute;
