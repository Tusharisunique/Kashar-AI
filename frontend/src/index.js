import React from 'react';
import ReactDOM from 'react-dom/client';
import axios from 'axios';
import './index.css';
import App from './App';

// Configure API base URL for production deployments
// In development, REACT_APP_API_BASE_URL is usually undefined and
// CRA's proxy setting will forward /api requests to the backend.
axios.defaults.baseURL = process.env.REACT_APP_API_BASE_URL || '';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
