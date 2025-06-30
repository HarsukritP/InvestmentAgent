import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HubPage from './hub/HubPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HubPage />} />
          <Route path="/hub" element={<HubPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 