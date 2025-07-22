import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import BuyStock from '../BuyStock';
import './PortfolioPage.css';

const PortfolioPage = ({ onBuyStock, onAdjustHolding, onTransactionSuccess }) => {
  const [portfolio, setPortfolio] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState(null);
  const [marketStatus, setMarketStatus] = useState({
    isOpen: false,
    nextUpdateMinutes: 0
  });

  const fetchPortfolio = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/portfolio');
      setPortfolio(response.data);
      
      // Check market status
      const statusResponse = await axios.get('/market-status');
      setMarketStatus({
        isOpen: statusResponse.data.is_open,
        nextUpdateMinutes: statusResponse.data.next_update_minutes || 5
      });
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      setError('Failed to load portfolio data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPortfolio();
    
    // Set up auto-refresh every 5 minutes
    const refreshInterval = setInterval(() => {
      fetchPortfolio();
    }, 5 * 60 * 1000);
    
    return () => clearInterval(refreshInterval);
  }, [fetchPortfolio]);

  const handleBuyStock = () => {
    setSelectedHolding(null);
    setShowBuyModal(true);
  };
  
  const handleAdjustHolding = (holding) => {
    setSelectedHolding(holding);
    setShowBuyModal(true);
  };
  
  const handleTransactionSuccess = (data) => {
    fetchPortfolio();
    setSelectedHolding(null);
    if (onTransactionSuccess) {
      onTransactionSuccess(data);
    }
  };

  if (isLoading) {
    return (
      <div className="portfolio-page">
        <div className="portfolio-page-header">
          <h1>Portfolio</h1>
        </div>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portfolio-page">
        <div className="portfolio-page-header">
          <h1>Portfolio</h1>
        </div>
        <div className="error">
          <p>{error}</p>
          <button onClick={fetchPortfolio}>Try Again</button>
        </div>
      </div>
    );
  }

  const { cash_balance, holdings, total_value, holdings_value } = portfolio || {};
  const holdingsCount = holdings ? holdings.length : 0;

  return (
    <div className="portfolio-page">
      <div className="portfolio-page-header">
        <h1>Portfolio</h1>
      </div>
      
      <div className="portfolio-summary">
        <div className="summary-row">
          <div className="summary-header">
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
            <div className="summary-card">
              <div className="card-label">Total Value</div>
              <div className="card-value">${total_value ? total_value.toFixed(2) : '0.00'}</div>
              {portfolio && portfolio.total_change && (
                <div className={`card-percentage ${portfolio.total_change >= 0 ? 'positive' : 'negative'}`}>
                  {portfolio.total_change >= 0 ? '+' : ''}{portfolio.total_change.toFixed(2)}%
                </div>
              )}
            </div>
            
            <div className="summary-card">
              <div className="card-label">Holdings Value</div>
              <div className="card-value">${holdings_value ? holdings_value.toFixed(2) : '0.00'}</div>
              <div className="card-secondary">
                {holdings_value && total_value ? ((holdings_value / total_value) * 100).toFixed(1) : '0.0'}% of portfolio
              </div>
            </div>
            
            <div className="summary-card">
              <div className="card-label">Cash Balance</div>
              <div className="card-value">${cash_balance ? cash_balance.toFixed(2) : '0.00'}</div>
              <div className="card-secondary">
                {cash_balance && total_value ? ((cash_balance / total_value) * 100).toFixed(1) : '0.0'}% of portfolio
              </div>
            </div>
          </div>
          
          <div className="action-buttons">
            <button className="action-button buy-button" onClick={handleBuyStock}>
              Buy Stock
            </button>
            <button className="action-button refresh-button" onClick={fetchPortfolio}>
              Refresh
            </button>
          </div>
        </div>
      </div>
      
      {holdingsCount > 0 ? (
        <>
          <div className="positions-count">{holdingsCount} positions</div>
          <table className="holdings-table">
            <thead>
              <tr>
                <th>SYMBOL</th>
                <th>SHARES</th>
                <th>AVG. COST</th>
                <th>CURRENT PRICE</th>
                <th>MARKET VALUE</th>
                <th>PROFIT/LOSS</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {holdings.map((holding) => (
                <tr key={holding.symbol}>
                  <td className="symbol-cell">{holding.symbol}</td>
                  <td>{holding.shares.toFixed(2)}</td>
                  <td>${holding.avg_cost.toFixed(2)}</td>
                  <td>${holding.current_price.toFixed(2)}</td>
                  <td>${holding.market_value.toFixed(2)}</td>
                  <td className={`profit-cell ${holding.profit_loss >= 0 ? 'positive' : 'negative'}`}>
                    ${holding.profit_loss.toFixed(2)}
                    <br />
                    {holding.profit_loss_percent >= 0 ? '+' : ''}{holding.profit_loss_percent.toFixed(2)}%
                  </td>
                  <td className="action-cell">
                    <button 
                      className="buy-more-button" 
                      onClick={() => handleAdjustHolding(holding)}
                    >
                      Adjust
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        <div className="no-holdings">
          <h3>No holdings yet</h3>
          <p>Start building your portfolio by buying your first stock.</p>
          <button onClick={handleBuyStock}>Buy Stock</button>
        </div>
      )}
      
      <BuyStock 
        isOpen={showBuyModal} 
        onClose={() => setShowBuyModal(false)}
        onSuccess={handleTransactionSuccess}
        existingHolding={selectedHolding}
      />
    </div>
  );
};

export default PortfolioPage; 