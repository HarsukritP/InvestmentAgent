/**
 * Application configuration
 */

// API URL - Use relative URL when accessed through proxy, otherwise use environment variable or default
// This ensures OAuth works correctly when accessed through the hub proxy
const isProxied = window.location.pathname.startsWith('/portfolio-agent');

// If accessed through proxy, use relative API URL to ensure OAuth works
export const API_URL = isProxied 
  ? '/portfolio-agent/api' // When accessed via proxy, use relative path
  : (process.env.REACT_APP_API_URL || 'https://investmentaiagentservice.up.railway.app');

// Log the API URL for debugging
console.log('🔗 Using API URL:', API_URL);
console.log('📍 Current pathname:', window.location.pathname);
console.log('🔄 Is proxied:', isProxied);

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