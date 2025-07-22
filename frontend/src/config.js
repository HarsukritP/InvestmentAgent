/**
 * Application configuration
 */

// Determine the appropriate API URL based on the current domain
const determineApiUrl = () => {
  const hostname = window.location.hostname;
  
  if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
    return 'http://localhost:8000';
  } else {
    // For all production environments, use the Railway backend
    return 'https://portfolioagent-backend-production.up.railway.app';
  }
};

// API URL - Use environment variable if set, otherwise determine based on hostname
export const API_URL = process.env.REACT_APP_API_URL || determineApiUrl();

// Google OAuth Client ID
export const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

// App settings
export const APP_NAME = 'ProCogia Portfolio Agent';
export const APP_VERSION = '1.0.0';

// Feature flags
export const FEATURES = {
  enableDebugTools: process.env.NODE_ENV === 'development',
  enableAIAssistant: true,
  enableRealTimeData: true
}; 