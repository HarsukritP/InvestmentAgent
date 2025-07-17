/**
 * Application configuration
 */

// API URL - use environment variable or default to external Railway URL for direct access
export const API_URL = process.env.REACT_APP_API_URL || 'https://investmentaiagentservice.up.railway.app';

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