import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './BuyStock.css';

const BuyStock = ({ isOpen, onClose, onSuccess }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [maxAffordableShares, setMaxAffordableShares] = useState(1);
  const [isSearching, setIsSearching] = useState(false);
  const [isBuying, setIsBuying] = useState(false);
  const [affordability, setAffordability] = useState(null);
  const [error, setError] = useState('');

  const searchStocks = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setError('');
    
    try {
      const response = await axios.get(`/search-stocks?query=${encodeURIComponent(searchQuery.trim())}`);
      setSearchResults(response.data.results || []);
      
      // Log caching info
      if (response.data.cached_prices > 0) {
        console.log(`💾 Pre-cached prices for ${response.data.cached_prices} stocks`);
      }
    } catch (error) {
      console.error('Search error:', error);
      setError('Failed to search stocks. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const checkAffordabilityWithPrice = useCallback(async (currentPrice) => {
    if (!selectedStock || quantity <= 0 || !currentPrice) return;
    
    try {
      // Create affordability object using cached price
      const totalCost = currentPrice * quantity;
      
      // Get user's cash balance using the optimized endpoint
      const response = await axios.get('/cash-balance');
      const cashBalance = response.data.cash_balance;
      
      const canAfford = cashBalance >= totalCost;
      const maxAffordableShares = Math.floor(cashBalance / currentPrice);
      
      setAffordability({
        can_afford: canAfford,
        total_cost: totalCost,
        available_cash: cashBalance,
        shortfall: canAfford ? 0 : totalCost - cashBalance,
        max_affordable_shares: maxAffordableShares,
        current_price: currentPrice,
        cached: true
      });
      
      console.log(`💰 Using cached price: ${selectedStock.symbol} @ $${currentPrice} (saved API call)`);
    } catch (error) {
      console.error('Cached affordability check error:', error);
      // Fallback to regular affordability check
      if (selectedStock && quantity > 0) {
        try {
          const response = await axios.get(`/check-affordability/${selectedStock.symbol}?quantity=${quantity}`);
          setAffordability(response.data);
        } catch (fallbackError) {
          console.error('Fallback affordability check error:', fallbackError);
          setAffordability(null);
        }
      }
    }
  }, [selectedStock, quantity]);

  const checkAffordability = useCallback(async () => {
    if (!selectedStock || quantity <= 0) return;
    
    try {
      const response = await axios.get(`/check-affordability/${selectedStock.symbol}?quantity=${quantity}`);
      setAffordability(response.data);
    } catch (error) {
      console.error('Affordability check error:', error);
      setAffordability(null);
    }
  }, [selectedStock, quantity]);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setSearchQuery('');
      setSearchResults([]);
      setSelectedStock(null);
      setQuantity(1);
      setMaxAffordableShares(1);
      setAffordability(null);
      setError('');
    }
  }, [isOpen]);

  // Check affordability when stock or quantity changes
  useEffect(() => {
    if (selectedStock && quantity > 0) {
      // If we have cached price data, use it directly
      if (selectedStock.current_price && selectedStock.cached) {
        // We'll need to get cash balance, but we can skip the price lookup
        checkAffordabilityWithPrice(selectedStock.current_price);
      } else {
        checkAffordability();
      }
    }
  }, [selectedStock, quantity, checkAffordability, checkAffordabilityWithPrice]);

  // Update max affordable shares when affordability data changes
  useEffect(() => {
    if (affordability && affordability.max_affordable_shares) {
      setMaxAffordableShares(Math.max(1, affordability.max_affordable_shares));
      // Ensure quantity doesn't exceed max affordable
      if (quantity > affordability.max_affordable_shares) {
        setQuantity(affordability.max_affordable_shares);
      }
    }
  }, [affordability, quantity]);

  const handleBuyStock = async () => {
    if (!selectedStock || quantity <= 0) return;
    
    setIsBuying(true);
    setError('');
    
    try {
      const response = await axios.post('/buy-stock', {
        symbol: selectedStock.symbol,
        quantity: quantity
      });
      
      if (response.data.success) {
        onSuccess && onSuccess(response.data);
        onClose();
      } else {
        setError(response.data.error || 'Failed to buy stock');
      }
    } catch (error) {
      console.error('Buy error:', error);
      
      // Handle different types of errors
      let errorMessage = 'Failed to buy stock. Please try again.';
      
      if (error.response) {
        // Server responded with error status
        if (error.response.data) {
          if (typeof error.response.data === 'string') {
            errorMessage = error.response.data;
          } else if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (error.response.data.error) {
            errorMessage = error.response.data.error;
          } else if (error.response.data.message) {
            errorMessage = error.response.data.message;
          }
        }
      } else if (error.request) {
        // Network error
        errorMessage = 'Network error. Please check your connection.';
      } else if (error.message) {
        // Other error
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsBuying(false);
    }
  };

  const handleStockSelect = (stock) => {
    setSelectedStock(stock);
    setSearchResults([]);
    setSearchQuery('');
    setQuantity(1); // Reset to 1 when selecting new stock
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchStocks();
    }
  };

  const handleQuantityChange = (newQuantity) => {
    const validQuantity = Math.max(1, Math.min(maxAffordableShares, parseInt(newQuantity) || 1));
    setQuantity(validQuantity);
  };

  if (!isOpen) return null;

  return (
    <div className="buy-stock-overlay">
      <div className="buy-stock-modal">
        <div className="buy-stock-header">
          <h2>Buy Stock</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="buy-stock-content">
          {!selectedStock ? (
            // Stock Search Phase
            <div className="search-phase">
              <div className="search-section">
                <label>Search for a stock to buy:</label>
                <div className="search-input-group">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Enter stock symbol or company name (e.g., AAPL, Tesla)"
                    className="search-input"
                  />
                  <button 
                    onClick={searchStocks} 
                    disabled={isSearching || !searchQuery.trim()}
                    className="search-button"
                  >
                    {isSearching ? 'Searching...' : 'Search'}
                  </button>
                </div>
              </div>

              {searchResults.length > 0 && (
                <div className="search-results">
                  <h3>Search Results:</h3>
                  <div className="results-list">
                    {searchResults.map((stock, index) => (
                      <div 
                        key={index} 
                        className="result-item"
                        onClick={() => handleStockSelect(stock)}
                      >
                        <div className="stock-info">
                          <div className="stock-symbol">{stock.symbol}</div>
                          <div className="stock-name">{stock.name}</div>
                          <div className="stock-details">
                            {stock.exchange} • {stock.currency}
                            {stock.cached && stock.current_price && (
                              <span className="price-info">
                                • ${stock.current_price.toFixed(2)}
                                {stock.change_percent && (
                                  <span className={`change ${stock.change_percent >= 0 ? 'positive' : 'negative'}`}>
                                    ({stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%)
                                  </span>
                                )}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="select-arrow">→</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            // Buy Phase
            <div className="buy-phase">
              <div className="selected-stock">
                <h3>Selected Stock:</h3>
                <div className="stock-card">
                  <div className="stock-header">
                    <span className="symbol">{selectedStock.symbol}</span>
                    <span className="name">{selectedStock.name}</span>
                  </div>
                  {affordability && (
                    <div className="price-info">
                      <span className="current-price">
                        Current Price: ${affordability.current_price?.toFixed(2)}
                        {affordability.cached && (
                          <span className="cached-indicator">⚡ Cached</span>
                        )}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Enhanced Quantity Selection with Slider */}
              <div className="quantity-section-enhanced">
                <label>Select Quantity to Buy:</label>
                
                {/* Slider Interface */}
                <div className="slider-container">
                  <div className="slider-labels">
                    <span className="slider-label min">1 Share</span>
                    <span className="slider-label current">
                      {quantity} Share{quantity !== 1 ? 's' : ''}
                    </span>
                    <span className="slider-label max">
                      Max: {maxAffordableShares}
                    </span>
                  </div>
                  
                  <input
                    type="range"
                    min="1"
                    max={maxAffordableShares}
                    value={quantity}
                    onChange={(e) => handleQuantityChange(e.target.value)}
                    className="buy-quantity-slider"
                    step="1"
                  />
                  
                  <div className="slider-markers">
                    <div className="marker min-position" style={{ left: '0%' }} />
                    <div 
                      className="marker current-position" 
                      style={{ left: `${((quantity - 1) / (maxAffordableShares - 1)) * 100}%` }}
                    />
                    <div className="marker max-position" style={{ left: '100%' }} />
                  </div>
                </div>

                {/* Precision Input */}
                <div className="precision-input-section">
                  <span className="precision-label">Precise Amount:</span>
                  <input
                    type="number"
                    min="1"
                    max={maxAffordableShares}
                    value={quantity}
                    onChange={(e) => handleQuantityChange(e.target.value)}
                    className="precision-quantity-input"
                  />
                  <span className="shares-label">shares</span>
                </div>
              </div>

              {affordability && (
                <div className="affordability-info-enhanced">
                  <div className="cost-breakdown">
                    <div className="cost-row">
                      <span>Total Cost:</span>
                      <span className="cost-value">${affordability.total_cost?.toFixed(2)}</span>
                    </div>
                    <div className="cost-row">
                      <span>Available Cash:</span>
                      <span className="cash-value">${affordability.available_cash?.toFixed(2)}</span>
                    </div>
                    <div className="cost-row">
                      <span>Remaining Cash:</span>
                      <span className={`remaining-value ${(affordability.available_cash - affordability.total_cost) >= 0 ? 'positive' : 'negative'}`}>
                        ${(affordability.available_cash - affordability.total_cost).toFixed(2)}
                      </span>
                    </div>
                    {!affordability.can_afford && (
                      <div className="cost-row error">
                        <span>Shortfall:</span>
                        <span className="shortfall-value">-${affordability.shortfall?.toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                  
                  {!affordability.can_afford && affordability.max_affordable_shares > 0 && (
                    <div className="suggestion">
                      💡 You can afford up to {affordability.max_affordable_shares} shares
                    </div>
                  )}
                </div>
              )}

              <div className="action-buttons">
                <button 
                  onClick={() => setSelectedStock(null)}
                  className="back-button"
                >
                  ← Back to Search
                </button>
                <button 
                  onClick={handleBuyStock}
                  disabled={isBuying || !affordability?.can_afford}
                  className={`buy-button ${affordability?.can_afford ? 'enabled' : 'disabled'}`}
                >
                  {isBuying ? 'Buying...' : `Buy ${quantity} Share${quantity !== 1 ? 's' : ''}`}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BuyStock; 