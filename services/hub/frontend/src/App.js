import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import LandingPage from './pages/LandingPage';
import AgentsPage from './pages/AgentsPage';
import DemosPage from './pages/DemosPage';
import FAQsPage from './pages/FAQsPage';
import ContactPage from './pages/ContactPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/agents" element={<AgentsPage />} />
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