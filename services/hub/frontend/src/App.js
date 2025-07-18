import React from 'react';
import './App.css';

function App() {
  // Auto-redirect to ProCogia services page when accessing root
  React.useEffect(() => {
    // Only redirect if we're at the exact root path
    if (window.location.pathname === '/') {
      console.log('🔄 Redirecting from root to ProCogia services...');
      window.location.href = 'https://procogia.com/services';
    }
  }, []);
  
  return (
    <div className="App">
      <div style={{ 
        padding: '40px', 
        textAlign: 'center', 
        fontFamily: 'system-ui, sans-serif',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          padding: '2rem',
          borderRadius: '16px',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <h1 style={{ margin: '0 0 1rem 0', fontSize: '2rem' }}>ProCogia AI Hub</h1>
          <p style={{ margin: '0 0 1.5rem 0', opacity: 0.9 }}>
            Redirecting to ProCogia Solutions...
          </p>
          <div style={{
            width: '40px',
            height: '40px',
            border: '4px solid rgba(255, 255, 255, 0.3)',
            borderTop: '4px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
        </div>
        
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
}

export default App; 