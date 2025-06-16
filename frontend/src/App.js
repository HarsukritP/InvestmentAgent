import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';

import './App.css';

// Import page components
import LandingPage from './LandingPage';
import AuthSuccess from './AuthSuccess';
import PortfolioPage from './pages/PortfolioPage';
import ChatPage from './pages/ChatPage';
import ActionsLogPage from './pages/ActionsLogPage';
import Navigation from './components/Navigation';
import BuyStock from './BuyStock';
import AdjustHolding from './AdjustHolding';

function App() {
  const [user, setUser] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showBuyStock, setShowBuyStock] = useState(false);
  const [showAdjustHolding, setShowAdjustHolding] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isRefreshingPortfolio, setIsRefreshingPortfolio] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Check for existing authentication on app load
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      
      if (token) {
        try {
          // Set authorization header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Verify token with backend
          const response = await axios.get('/auth/me');
          
          if (response.data.user) {
            setUser(response.data.user);
            setIsAuthenticated(true);
          }
        } catch (error) {
          console.error('Token verification failed:', error);
          // Clear invalid token
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_header');
          delete axios.defaults.headers.common['Authorization'];
        }
      }
      
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Fetch health status when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchHealthStatus();
      fetchPortfolio();
    }
  }, [isAuthenticated]);

  const fetchHealthStatus = async () => {
    try {
      const response = await axios.get('/health');
      setHealthStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch health status:', error);
    }
  };

  const fetchPortfolio = async () => {
    try {
      setIsRefreshingPortfolio(true);
      console.log('🔄 Fetching portfolio data...');
      const response = await axios.get('/portfolio');
      // Create a new object with timestamp to ensure React detects the change
      const portfolioWithTimestamp = {
        ...response.data,
        _lastUpdated: Date.now()
      };
      setPortfolio(portfolioWithTimestamp);
      console.log('✅ Portfolio data updated:', portfolioWithTimestamp);
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    } finally {
      setIsRefreshingPortfolio(false);
    }
  };

  const handleAuthenticated = (token) => {
    // Set axios authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    // Verify and get user info
    axios.get('/auth/me')
      .then(response => {
        setUser(response.data.user);
        setIsAuthenticated(true);
      })
      .catch(error => {
        console.error('Failed to get user info:', error);
        handleLogout();
      });
  };

  const handleLogout = () => {
    // Clear local storage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_header');
    
    // Clear axios header
    delete axios.defaults.headers.common['Authorization'];
    
    // Reset state
    setUser(null);
    setIsAuthenticated(false);
    setHealthStatus(null);
    setPortfolio(null);
    
    // Call logout endpoint
    axios.post('/auth/logout').catch(console.error);
  };

  const handleBuySuccess = async (buyResult) => {
    console.log('🎉 Buy operation successful:', buyResult);
    
    // Add a small delay to ensure backend has fully processed the transaction
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Refresh portfolio after successful purchase
    console.log('🔄 Refreshing portfolio after buy success...');
    await fetchPortfolio();
  };

  const handleAdjustHolding = (holding) => {
    console.log('🔧 Adjusting holding:', holding);
    setSelectedHolding(holding);
    setShowAdjustHolding(true);
  };

  const handleAdjustSuccess = async (adjustResult) => {
    console.log('🎉 Adjust operation successful:', adjustResult);
    
    // Refresh portfolio
    await new Promise(resolve => setTimeout(resolve, 500));
    await fetchPortfolio();
  };

  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Loading Portfolio Agent...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route 
            path="/" 
            element={
              !isAuthenticated ? (
                <LandingPage onAuthenticated={handleAuthenticated} />
              ) : (
                <Navigate to="/portfolio" replace />
              )
            } 
          />
          <Route 
            path="/auth/success" 
            element={<AuthSuccess onAuthenticated={handleAuthenticated} />} 
          />
          
          {/* Protected routes */}
          {isAuthenticated ? (
            <>
              <Route 
                path="/portfolio" 
                element={
                  <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                    <Navigation 
                      user={user} 
                      onLogout={handleLogout}
                      isCollapsed={sidebarCollapsed}
                      onToggleCollapse={setSidebarCollapsed}
                    />
                    <main className="main-content">
                      <PortfolioPage 
                        portfolio={portfolio}
                        healthStatus={healthStatus}
                        isRefreshing={isRefreshingPortfolio}
                        onRefresh={fetchPortfolio}
                        onBuyStock={() => setShowBuyStock(true)}
                        onAdjustHolding={handleAdjustHolding}
                      />
                    </main>
                  </div>
                } 
              />
              <Route 
                path="/chat" 
                element={
                  <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                    <Navigation 
                      user={user} 
                      onLogout={handleLogout}
                      isCollapsed={sidebarCollapsed}
                      onToggleCollapse={setSidebarCollapsed}
                    />
                    <main className="main-content">
                      <ChatPage portfolio={portfolio} user={user} />
                    </main>
                  </div>
                } 
              />
              <Route 
                path="/actions-log" 
                element={
                  <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
                    <Navigation 
                      user={user} 
                      onLogout={handleLogout}
                      isCollapsed={sidebarCollapsed}
                      onToggleCollapse={setSidebarCollapsed}
                    />
                    <main className="main-content">
                      <ActionsLogPage />
                    </main>
                  </div>
                } 
              />
              <Route path="*" element={<Navigate to="/portfolio" replace />} />
            </>
          ) : (
            <Route path="*" element={<Navigate to="/" replace />} />
          )}
        </Routes>

        {/* Global Modals */}
        {showBuyStock && (
          <BuyStock
            isOpen={showBuyStock}
            onClose={() => setShowBuyStock(false)}
            onSuccess={handleBuySuccess}
          />
        )}

        {showAdjustHolding && selectedHolding && (
          <AdjustHolding
            isOpen={showAdjustHolding}
            holding={selectedHolding}
            onClose={() => {
              setShowAdjustHolding(false);
              setSelectedHolding(null);
            }}
            onSuccess={handleAdjustSuccess}
          />
        )}
      </div>
    </Router>
  );
}

export default App; 