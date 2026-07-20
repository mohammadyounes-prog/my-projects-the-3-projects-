import { Navigate, Outlet } from 'react-router-dom';
import { useState, useEffect } from 'react';

const ProtectedRoute = () => {
  const [isChecking, setIsChecking] = useState(true);
  const token = localStorage.getItem('token');
  const urlParams = new URLSearchParams(window.location.search);
  const ssoToken = urlParams.get('sso_token');

  console.log("ProtectedRoute: token=", token, "ssoToken=", ssoToken);

  useEffect(() => {
    // If an SSO token is in the URL, wait a moment for SsoHandler to process it
    if (ssoToken) {
      console.log("ProtectedRoute: ssoToken found, waiting...");
      const timer = setTimeout(() => setIsChecking(false), 800);
      return () => clearTimeout(timer);
    } else {
      setIsChecking(false);
    }
  }, [ssoToken]);

  if (isChecking) return <div>Authenticating...</div>;

  // Allow through if token exists OR if we are currently processing an SSO token
  if (token || ssoToken) {
    console.log("ProtectedRoute: Authorizing access.");
    return <Outlet />;
  }

  console.log("ProtectedRoute: Redirecting to login.");
  return <Navigate to="/login" />;
};

export default ProtectedRoute;
