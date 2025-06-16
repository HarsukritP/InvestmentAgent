/**
 * Application configuration
 */

// API URL - defaults to localhost:8000 in development
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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