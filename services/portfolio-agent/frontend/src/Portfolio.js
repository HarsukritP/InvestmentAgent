import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Portfolio = ({ healthStatus, portfolioData: propPortfolioData, onRefresh, isRefreshing, onAdjustHolding }) => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Use prop data if available, otherwise use internal state
  const currentPortfolioData = propPortfolioData || portfolioData;

  // Debug logging
  console.log('🔍 Portfolio component render:', {
    propPortfolioData: propPortfolioData ? 'HAS_PROP_DATA' : 'NO_PROP_DATA',
    internalPortfolioData: portfolioData ? 'HAS_INTERNAL_DATA' : 'NO_INTERNAL_DATA',
    currentPortfolioData: currentPortfolioData ? 'HAS_CURRENT_DATA' : 'NO_CURRENT_DATA',
    holdingsCount: currentPortfolioData?.portfolio?.holdings?.length || 0
  });

  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/portfolio');
      
      // Backend returns data directly, no need to check for success wrapper
      setPortfolioData(response.data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Portfolio fetch error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load portfolio');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Only fetch if no prop data is provided
    if (!propPortfolioData) {
      fetchPortfolio();
      
      // Auto-refresh every 60 seconds
      const interval = setInterval(fetchPortfolio, 60000);
      return () => clearInterval(interval);
    } else {
      setLoading(false);
      setLastUpdated(new Date().toLocaleTimeString());
    }
  }, [propPortfolioData]);

  // Update last updated time when prop data changes
  useEffect(() => {
    if (propPortfolioData) {
      console.log('📊 Portfolio prop data changed:', propPortfolioData);
      setLastUpdated(new Date().toLocaleTimeString());
    }
  }, [propPortfolioData]);

  const formatCurrency = (amount) => {
    // Add safety check for undefined/null values
    if (amount === undefined || amount === null || isNaN(amount)) {
      return '$0.00';
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatPercent = (percent) => {
    // Add safety check for undefined/null values
    if (percent === undefined || percent === null || isNaN(percent)) {
      return '0.00%';
    }
    const formatted = percent.toFixed(2);
    return percent >= 0 ? `+${formatted}%` : `${formatted}%`;
  };

  const getPerformanceClass = (value) => {
    if (value === undefined || value === null || isNaN(value)) {
      return 'neutral';
    }
    return value >= 0 ? 'positive' : 'negative';
  };

  const getPerformanceIcon = (value) => {
    if (value === undefined || value === null || isNaN(value)) {
      return '→';
    }
    if (value > 0) return '↗';
    if (value < 0) return '↘';
    return '→';
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📊 Portfolio Analytics</h2>
          <p className="card-subtitle">Real-time portfolio performance</p>
        </div>
        <div className="card-content">
          <div className="loading">
            <div className="spinner"></div>
            <span>Loading portfolio data...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📊 Portfolio Analytics</h2>
          <p className="card-subtitle">Real-time portfolio performance</p>
        </div>
        <div className="card-content">
          <div className="error">
            <strong>Error loading portfolio:</strong> {error}
            <button 
              onClick={onRefresh || fetchPortfolio}
              style={{ marginLeft: '1rem', padding: '0.5rem 1rem', cursor: 'pointer' }}
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!currentPortfolioData || !currentPortfolioData.portfolio) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">📊 Portfolio Analytics</h2>
          <p className="card-subtitle">No portfolio data available</p>
        </div>
      </div>
    );
  }

  // Extract portfolio data for easier access
  const portfolio = currentPortfolioData.portfolio;
  const holdings = currentPortfolioData.holdings || [];  // Holdings are at root level, not inside portfolio
  
  // Debug logging for holdings
  console.log('🔍 Portfolio data structure:', {
    currentPortfolioData,
    portfolio,
    holdings,
    holdingsLength: holdings.length,
    portfolioKeys: Object.keys(portfolio || {}),
    holdingsType: Array.isArray(holdings) ? 'array' : typeof holdings
  });
  
  // Calculate summary values
  const portfolioValue = portfolio.total_market_value || 0;
  const cashBalance = portfolio.cash_balance || 0;
  const totalAccountValue = portfolioValue + cashBalance;
  
  // Calculate total P&L
  const totalCost = holdings.reduce((sum, holding) => {
    return sum + (holding.shares || holding.quantity || 0) * (holding.average_cost || holding.purchase_price || 0);
  }, 0);
  const totalPnl = portfolioValue - totalCost;
  const totalPnlPercent = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0;

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          📊 Portfolio Analytics
          {isRefreshing && <span style={{ marginLeft: '10px', fontSize: '14px', color: '#007bff' }}>🔄 Refreshing...</span>}
        </h2>
        <p className="card-subtitle">
          Real-time performance • Last updated: {lastUpdated}
        </p>
      </div>
      
      <div className="card-content">
        {/* Performance Summary */}
        <div className="portfolio-summary">
          <div className="summary-item">
            <div className="summary-label">Portfolio Value</div>
            <div className="summary-value">
              {formatCurrency(portfolioValue)}
            </div>
          </div>
          
          <div className="summary-item">
            <div className="summary-label">Total Return</div>
            <div className="summary-value">
              {formatCurrency(totalPnl)}
            </div>
            <div className={`summary-change ${getPerformanceClass(totalPnl)}`}>
              {getPerformanceIcon(totalPnl)} {formatPercent(totalPnlPercent)}
            </div>
          </div>
          
          <div className="summary-item">
            <div className="summary-label">Cash Balance</div>
            <div className="summary-value">
              {formatCurrency(cashBalance)}
            </div>
          </div>
          
          <div className="summary-item">
            <div className="summary-label">Total Account</div>
            <div className="summary-value">
              {formatCurrency(totalAccountValue)}
            </div>
          </div>
        </div>

        {/* Holdings Table */}
        <div className="holdings-section">
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)' }}>
            Holdings Dashboard
          </h3>
          
          {holdings.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
              No holdings found
            </div>
          ) : (
            <table className="holdings-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Quantity</th>
                  <th>Entry Price</th>
                  <th>Current Price</th>
                  <th>Current Value</th>
                  <th>P&L</th>
                  <th>Performance</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => {
                  // Handle both legacy and database formats
                  const symbol = holding.symbol;
                  const quantity = holding.shares || holding.quantity || 0;
                  const entryPrice = holding.average_cost || holding.purchase_price || 0;
                  const currentPrice = holding.current_price || 0;
                  const currentValue = holding.market_value || (quantity * currentPrice);
                  const pnl = holding.unrealized_pnl || (currentValue - (quantity * entryPrice));
                  const pnlPercent = holding.unrealized_pnl_percent || (entryPrice > 0 ? (pnl / (quantity * entryPrice)) * 100 : 0);
                  
                  return (
                    <tr key={symbol}>
                      <td className="symbol">{symbol}</td>
                      <td>{quantity}</td>
                      <td className="price">{formatCurrency(entryPrice)}</td>
                      <td className="price">{formatCurrency(currentPrice)}</td>
                      <td className="price">{formatCurrency(currentValue)}</td>
                      <td className={`price ${getPerformanceClass(pnl)}`}>
                        {formatCurrency(pnl)}
                      </td>
                      <td className={getPerformanceClass(pnlPercent)}>
                        {getPerformanceIcon(pnlPercent)} {formatPercent(pnlPercent)}
                      </td>
                      <td>
                        <button 
                          onClick={() => onAdjustHolding(holding)}
                          style={{
                            padding: '0.5rem 1rem',
                            background: 'var(--button-primary)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}
                        >
                          Adjust
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Data Status */}
        <div style={{ 
          marginTop: '1.5rem', 
          padding: '1rem', 
          background: 'var(--procogia-light)', 
          borderRadius: '8px',
          fontSize: '14px',
          color: 'var(--text-secondary)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>🔄 Real-time Data</span>
            <button 
              onClick={fetchPortfolio}
              style={{
                padding: '0.5rem 1rem',
                background: 'var(--button-primary)',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Refresh
            </button>
          </div>
          <div style={{ marginTop: '0.5rem', fontSize: '12px', opacity: '0.8' }}>
            {holdings.some(h => h.quote_data?.mock) && 
              "⚠️ Using simulated market data (configure API keys for live data)"
            }
          </div>
        </div>
      </div>
    </div>
  );
};

export default Portfolio; 