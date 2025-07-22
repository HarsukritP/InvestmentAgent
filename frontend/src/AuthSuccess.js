import React, { useEffect } from 'react';

const AuthSuccess = ({ onAuthenticated }) => {
  useEffect(() => {
    // Get token from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      // Store token in localStorage
      localStorage.setItem('auth_token', token);
      
      // Set authorization header for future requests
      const authHeader = `Bearer ${token}`;
      localStorage.setItem('auth_header', authHeader);
      
      // Call the authentication callback
      if (onAuthenticated) {
        onAuthenticated(token);
      }
      
      // Redirect to the custom domain if we're on Railway
      const currentHost = window.location.hostname;
      if (currentHost.includes('railway.app')) {
        window.location.href = 'https://portfolioagent.procogia.ai/portfolio';
        return;
      }
      
      // Otherwise, just clear URL parameters and let the app handle routing
      window.history.replaceState({}, document.title, "/portfolio");
    } else {
      console.error('No token received from OAuth callback');
      // Redirect to landing page
      window.location.href = '/';
    }
  }, [onAuthenticated]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      fontFamily: 'system-ui'
    }}>
      <div style={{
        textAlign: 'center',
        background: 'rgba(255, 255, 255, 0.1)',
        padding: '2rem',
        borderRadius: '16px',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid rgba(255, 255, 255, 0.3)',
          borderTop: '4px solid white',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 1rem'
        }}></div>
        <h2>Completing Authentication...</h2>
        <p>Please wait while we log you in.</p>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    </div>
  );
};

export default AuthSuccess; 