import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../config';
import BuyStock from '../BuyStock';
import AdjustHolding from '../AdjustHolding';
import { formatCurrency, formatPercentage, getValueClass, getMarketStatus } from '../utils/formatters';
import './PortfolioPage.css';

const PortfolioPage = ({ 
  portfolio, 
  healthStatus, 
  isRefreshing, 
  onRefresh, 
  onBuyStock, 
  onAdjustHolding,
  isMobile,
  toggleMobileNav
}) => {
  const [loading] = useState(false);
  const [error] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState(null);

  useEffect(() => {
    if (portfolio) {
      setLastUpdated(new Date().toLocaleTimeString());
    }
  }, [portfolio]);

  const formatCurrency = (amount) => {
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

  const getStatusDisplay = () => {
    if (!healthStatus) return { text: 'Loading...', class: 'loading' };
    
    const { configuration } = healthStatus;
    
    if (!configuration) return { text: 'Loading...', class: 'loading' };
    
    if (!configuration.twelvedata_key_configured && !configuration.openai_key_configured && !configuration.oauth_configured) {
      return { text: 'Demo Mode (No API Keys)', class: 'warning' };
    }
    
    if (!configuration.twelvedata_key_configured) {
      return { text: 'Using Mock Market Data', class: 'warning' };
    }
    
    if (!configuration.openai_key_configured) {
      return { text: 'AI Assistant Unavailable', class: 'warning' };
    }
    
    if (healthStatus.status === 'healthy') {
      return { text: 'All Systems Operational', class: 'success' };
    }
    
    return { text: 'Some Services Degraded', class: 'warning' };
  };

  const handleRefresh = () => {
    onRefresh();
  };

  const handleBuyStock = () => {
    setShowBuyModal(true);
  };

  const handleAdjustHolding = (holding) => {
    setSelectedHolding(holding);
    setShowAdjustModal(true);
  };

  const handleTransactionSuccess = () => {
    setShowBuyModal(false);
    setShowAdjustModal(false);
    handleRefresh();
  };

  // If portfolio is not loaded yet
  if (!portfolio) {
    return (
      <div className="portfolio-page">
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  // Extract portfolio data
  const { cash_balance = 0, holdings = [] } = portfolio;
  
  // Calculate total portfolio value
  const totalHoldingsValue = holdings.reduce((sum, holding) => {
    const shares = holding.shares || holding.quantity || 0;
    const price = holding.current_price || 0;
    return sum + (shares * price);
  }, 0);
  
  const totalPortfolioValue = totalHoldingsValue + cash_balance;
  
  // Calculate total profit/loss
  const totalCostBasis = holdings.reduce((sum, holding) => {
    const shares = holding.shares || holding.quantity || 0;
    const avgCost = holding.average_cost || holding.purchase_price || 0;
    return sum + (shares * avgCost);
  }, 0);
  
  const totalInitialValue = totalCostBasis + cash_balance;
  const totalPnL = totalPortfolioValue - totalInitialValue;
  const totalPnLPercent = totalInitialValue > 0 ? (totalPnL / totalInitialValue) * 100 : 0;

  // Get market status
  const marketStatus = getMarketStatus();

  return (
    <div className="portfolio-page">
      {/* Mobile header */}
      {isMobile && (
        <div className="mobile-header">
          <button className="menu-toggle" onClick={toggleMobileNav}>
            <span className="menu-icon">☰</span>
          </button>
          <h1 className="page-title">Portfolio</h1>
        </div>
      )}
      
      {/* Portfolio Summary */}
      <div className="portfolio-summary">
        <div className="summary-header">
          <h1>Portfolio</h1>
          <div className="market-status">
            <span className={`status-indicator ${marketStatus.isOpen ? 'open' : 'closed'}`}></span>
            <span className="status-text">
              Market {marketStatus.isOpen ? 'Open' : 'Closed'}
            </span>
            <span className="update-time">
              Next update in {marketStatus.nextUpdateMinutes} min
            </span>
          </div>
        </div>
        
        <div className="summary-cards">
          <div className="summary-card total-value">
            <div className="card-label">Total Value</div>
            <div className="card-value">{formatCurrency(totalPortfolioValue)}</div>
            <div className={`card-change ${getPerformanceClass(totalPnL)}`}>
              {formatCurrency(totalPnL)} ({formatPercent(totalPnLPercent)})
            </div>
          </div>
          
          <div className="summary-card holdings-value">
            <div className="card-label">Holdings Value</div>
            <div className="card-value">{formatCurrency(totalHoldingsValue)}</div>
            <div className="card-percent">{((totalHoldingsValue / totalPortfolioValue) * 100).toFixed(1)}% of portfolio</div>
          </div>
          
          <div className="summary-card cash-balance">
            <div className="card-label">Cash Balance</div>
            <div className="card-value">{formatCurrency(cash_balance)}</div>
            <div className="card-percent">{((cash_balance / totalPortfolioValue) * 100).toFixed(1)}% of portfolio</div>
          </div>
        </div>
        
        <div className="action-buttons">
          <button 
            className="action-button buy-button"
            onClick={handleBuyStock}
          >
            <span className="button-icon">$</span> Buy Stock
          </button>
          
          <button 
            className="action-button refresh-button"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <span className="button-icon">⟳</span> Refresh
          </button>
        </div>
      </div>
      
      {/* Holdings Section */}
      <div className="holdings-section">
        <div className="section-header">
          <h2 className="section-title">Current Holdings</h2>
          <div className="section-subtitle">
            {holdings.length} {holdings.length === 1 ? 'position' : 'positions'}
          </div>
        </div>

        {holdings.length === 0 ? (
          <div className="empty-holdings">
            <div className="empty-icon">📈</div>
            <h3>No holdings yet</h3>
            <p>Start building your portfolio by buying your first stock.</p>
            <button className="buy-first-stock-btn" onClick={handleBuyStock}>
              Buy Your First Stock
            </button>
          </div>
        ) : (
          <div className="holdings-table-wrapper">
            <table className="holdings-table">
              <thead>
                <tr className="table-header">
                  <th>Symbol</th>
                  <th>Shares</th>
                  <th>Avg. Cost</th>
                  <th>Current Price</th>
                  <th>Market Value</th>
                  <th>Profit/Loss</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding, index) => {
                  const shares = holding.shares || holding.quantity || 0;
                  const avgCost = holding.average_cost || holding.purchase_price || 0;
                  const currentPrice = holding.current_price || 0;
                  const marketValue = shares * currentPrice;
                  const costBasis = shares * avgCost;
                  const pnl = marketValue - costBasis;
                  const pnlPercent = costBasis > 0 ? (pnl / costBasis) * 100 : 0;
                  
                  return (
                    <tr key={index} className="table-row">
                      <td className="table-cell">
                        <div className="symbol-info">
                          <div className="symbol-text">
                            <strong>{holding.symbol}</strong>
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">{shares.toFixed(2)}</td>
                      <td className="table-cell">{formatCurrency(avgCost)}</td>
                      <td className="table-cell">{formatCurrency(currentPrice)}</td>
                      <td className="table-cell">{formatCurrency(marketValue)}</td>
                      <td className="table-cell">
                        <div className={`pnl-value ${getPerformanceClass(pnl)}`}>
                          {formatCurrency(pnl)}
                          <div className={`pnl-percent ${getPerformanceClass(pnlPercent)}`}>
                            {formatPercent(pnlPercent)}
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <button 
                          className="adjust-btn"
                          onClick={() => handleAdjustHolding(holding)}
                        >
                          Adjust
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modals */}
      {showBuyModal && (
        <BuyStock 
          isOpen={showBuyModal} 
          onClose={() => setShowBuyModal(false)} 
          onSuccess={handleTransactionSuccess}
          isMobile={isMobile}
        />
      )}
      
      {showAdjustModal && selectedHolding && (
        <AdjustHolding 
          isOpen={showAdjustModal} 
          holding={selectedHolding}
          onClose={() => setShowAdjustModal(false)} 
          onSuccess={handleTransactionSuccess}
          isMobile={isMobile}
        />
      )}
    </div>
  );
};

export default PortfolioPage; 