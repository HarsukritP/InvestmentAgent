import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// External redirect component for the base route
const ExternalRedirect = ({ url }) => {
  React.useEffect(() => {
    window.location.href = url;
  }, [url]);
  
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <p>Redirecting to ProCogia Solutions...</p>
    </div>
  );
};

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Base route - redirect to ProCogia Solutions */}
          <Route path="/" element={<ExternalRedirect url="https://procogia.com/solutions/" />} />
          
          {/* All agent routes are handled by server.js proxy - no React routes needed */}
          {/* /portfolio-agent/* -> proxied to portfolio frontend */}
          {/* /manufacturing-agent/* -> proxied to manufacturing frontend */}
          {/* /document-review-agent/* -> proxied to document review frontend */}
          {/* /customer-support-agent/* -> proxied to customer support frontend */}
        </Routes>
      </div>
    </Router>
  );
}

export default App; 