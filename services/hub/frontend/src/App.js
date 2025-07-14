import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import AgentsPage from './pages/AgentsPage';
import PortfolioAgentPage from './pages/PortfolioAgentPage';
import DocumentReviewAgentPage from './pages/DocumentReviewAgentPage';
import CustomerSupportAgentPage from './pages/CustomerSupportAgentPage';
import SalesAssistantAgentPage from './pages/SalesAssistantAgentPage';
import DemosPage from './pages/DemosPage';
import FAQsPage from './pages/FAQsPage';
import ContactPage from './pages/ContactPage';
import './App.css';

// External redirect component
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
        <Navigation />
        <Routes>
          {/* Redirect main page to ProCogia Solutions */}
          <Route path="/" element={<ExternalRedirect url="https://procogia.com/solutions/" />} />
          <Route path="/agents" element={<AgentsPage />} />
          
          {/* Agent Info Pages */}
          <Route path="/agents/info/portfolio-agent" element={<PortfolioAgentPage />} />
          <Route path="/agents/info/document-review" element={<DocumentReviewAgentPage />} />
          <Route path="/agents/info/customer-support" element={<CustomerSupportAgentPage />} />
          <Route path="/agents/info/sales-assistant" element={<SalesAssistantAgentPage />} />
          
          <Route path="/demos" element={<DemosPage />} />
          <Route path="/faqs" element={<FAQsPage />} />
          <Route path="/contact" element={<ContactPage />} />
          
          {/* Legacy route for backward compatibility */}
          <Route path="/hub" element={<AgentsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 