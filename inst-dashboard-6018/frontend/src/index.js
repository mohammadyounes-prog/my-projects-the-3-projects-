import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Explicitly import global CSS
import App from './App.tsx'; // Explicitly import App component with .tsx extension
// You might also need to import your i18n setup if it's not handled in App.tsx
// import './i18n';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
