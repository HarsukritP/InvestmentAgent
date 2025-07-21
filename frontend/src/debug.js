/**
 * Debug utility for frontend issues
 */

// Export a function to check connectivity to the backend
export const checkBackendConnection = async () => {
  try {
    // Import API_URL from config
    const { API_URL } = await import('./config');
    
    console.log('Checking backend connection to:', API_URL);
    
    // Make a simple fetch request to the backend
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      console.error('Backend connection failed with status:', response.status);
      return {
        success: false,
        status: response.status,
        message: `Failed to connect to backend: ${response.statusText}`
      };
    }
    
    const data = await response.json();
    console.log('Backend connection successful:', data);
    
    return {
      success: true,
      data: data
    };
  } catch (error) {
    console.error('Backend connection error:', error);
    return {
      success: false,
      error: error.message || 'Unknown error'
    };
  }
};

// Export a function to check if the app is running in Railway
export const isRunningInRailway = () => {
  const hostname = window.location.hostname;
  return hostname.includes('railway.app');
};

// Export a function to get environment information
export const getEnvironmentInfo = () => {
  return {
    hostname: window.location.hostname,
    protocol: window.location.protocol,
    port: window.location.port,
    pathname: window.location.pathname,
    userAgent: navigator.userAgent,
    isRailway: isRunningInRailway()
  };
}; 