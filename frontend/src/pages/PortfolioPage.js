import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import BuyStock from '../BuyStock';
import './PortfolioPage.css';

const PortfolioPage = ({ onTransactionSuccess }) => {
  const [portfolio, setPortfolio] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState(null);
  const [marketStatus, setMarketStatus] = useState({
    isOpen: false,
    nextUpdateMinutes: 5
  });

  const fetchPortfolio = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Fetching portfolio data...');
      const response = await axios.get('/portfolio');
      console.log('Portfolio data received:', response.data);
      setPortfolio(response.data);
      
      // Extract portfolio data from response structure
      const portfolioData = response.data.portfolio || {};
      const holdingsData = response.data.holdings || [];
      
      // Calculate total value and holdings value
      const cashBalance = portfolioData.cash_balance || 0;
      const holdingsValue = holdingsData.reduce((total, holding) => total + (holding.market_value || 0), 0);
      const totalValue = cashBalance + holdingsValue;
      
      setPortfolio({
        cash_balance: cashBalance,
        holdings: holdingsData,
        total_value: totalValue,
        holdings_value: holdingsValue
      });
      
      // Try to get market status
      try {
        const statusResponse = await axios.get('/health');
        const isMarketOpen = statusResponse.data?.services?.market_data?.status === 'healthy';
        setMarketStatus({
          isOpen: isMarketOpen,
          nextUpdateMinutes: 5
        });
      } catch (statusError) {
        console.error('Error fetching market status:', statusError);
        // Don't set an error, just keep default market status
      }
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
        <h1 className="page-title">Portfolio</h1>
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
        <h1 className="page-title">Portfolio</h1>
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
      <h1 className="page-title">Portfolio</h1>
      
      <div className="market-status-bar">
        <div className="status-indicator-container">
          <span className={`status-indicator ${marketStatus.isOpen ? 'open' : 'closed'}`}></span>
          <span className="status-text">
            Market {marketStatus.isOpen ? 'Open' : 'Closed'}
          </span>
        </div>
        <span className="update-time">
          Next update in {marketStatus.nextUpdateMinutes} min
        </span>
      </div>
      
      <div className="portfolio-summary">
        <div className="stats-grid">
          <div className="stat-card">
            <h3>TOTAL VALUE</h3>
            <p className="stat-value">${total_value ? total_value.toFixed(2) : '0.00'}</p>
            {portfolio && portfolio.total_change && (
              <p className={`stat-change ${portfolio.total_change >= 0 ? 'positive' : 'negative'}`}>
                {portfolio.total_change >= 0 ? '+' : ''}{portfolio.total_change.toFixed(2)}%
              </p>
            )}
          </div>
          
          <div className="stat-card">
            <h3>HOLDINGS VALUE</h3>
            <p className="stat-value">${holdings_value ? holdings_value.toFixed(2) : '0.00'}</p>
            <p className="stat-secondary">
              {holdings_value && total_value ? ((holdings_value / total_value) * 100).toFixed(1) : '0.0'}% of portfolio
            </p>
          </div>
          
          <div className="stat-card">
            <h3>CASH BALANCE</h3>
            <p className="stat-value">${cash_balance ? cash_balance.toFixed(2) : '0.00'}</p>
            <p className="stat-secondary">
              {cash_balance && total_value ? ((cash_balance / total_value) * 100).toFixed(1) : '0.0'}% of portfolio
            </p>
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
      
      {holdingsCount > 0 ? (
        <>
          <div className="positions-count">{holdingsCount} positions</div>
          <div className="holdings-table-container">
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
                    <td>${holding.average_cost ? holding.average_cost.toFixed(2) : holding.avg_cost.toFixed(2)}</td>
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
          </div>
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