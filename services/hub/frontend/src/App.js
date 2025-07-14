import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

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

// Simple proxy placeholder component (actual proxying handled by server.js)
const AgentProxy = ({ agentName }) => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <p>Loading {agentName}...</p>
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
          
          {/* Agent routes - proxied by server.js */}
          <Route path="/portfolio-agent" element={<AgentProxy agentName="Portfolio Agent" />} />
          <Route path="/manufacturing-agent" element={<AgentProxy agentName="Manufacturing Agent" />} />
          <Route path="/document-review-agent" element={<AgentProxy agentName="Document Review Agent" />} />
          <Route path="/customer-support-agent" element={<AgentProxy agentName="Customer Support Agent" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 