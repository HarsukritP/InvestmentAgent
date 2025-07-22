import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './BuyStock.css';

const BuyStock = ({ isOpen, onClose, onSuccess, isMobile, existingHolding = null }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [maxAffordableShares, setMaxAffordableShares] = useState(1);
  const [isSearching, setIsSearching] = useState(false);
  const [isBuying, setIsBuying] = useState(false);
  const [affordability, setAffordability] = useState(null);
  const [error, setError] = useState('');
  const [currentShares, setCurrentShares] = useState(0);
  const [targetShares, setTargetShares] = useState(0);
  const [sharesDifference, setSharesDifference] = useState(0);
  const [action, setAction] = useState('buy'); // 'buy' or 'sell'

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
      if (existingHolding) {
        // If editing an existing holding, pre-select it
        setSelectedStock({
          symbol: existingHolding.symbol,
          name: existingHolding.name || existingHolding.symbol,
          current_price: existingHolding.current_price
        });
        setCurrentShares(existingHolding.shares || existingHolding.quantity || 0);
        setQuantity(1); // Default to adding 1 more share
        setTargetShares(existingHolding.shares || existingHolding.quantity || 0);
        setSearchQuery('');
        setSearchResults([]);
      } else {
        // New stock purchase
        setSearchQuery('');
        setSearchResults([]);
        setSelectedStock(null);
        setCurrentShares(0);
        setQuantity(1);
        setTargetShares(1); // Start with 1 for new purchases
      }
      setMaxAffordableShares(1);
      setAffordability(null);
      setError('');
      setAction('buy');
    }
  }, [isOpen, existingHolding]);

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
      
      // If we have an existing holding, update the max target shares
      if (existingHolding) {
        const current = currentShares;
        const max = current + affordability.max_affordable_shares;
        setMaxAffordableShares(max);
      }
    }
  }, [affordability, quantity, existingHolding, currentShares]);

  // Update shares difference when target shares change
  useEffect(() => {
    if (existingHolding) {
      const difference = targetShares - currentShares;
      setSharesDifference(difference);
      setQuantity(Math.abs(difference));
      setAction(difference >= 0 ? 'buy' : 'sell');
    } else if (selectedStock) {
      // For new purchases, target shares equals quantity
      setSharesDifference(targetShares);
      setQuantity(targetShares);
    }
  }, [targetShares, currentShares, existingHolding, selectedStock]);

  const handleTransaction = async () => {
    if (!selectedStock || (action === 'buy' && quantity <= 0)) return;
    
    setIsBuying(true);
    setError('');
    
    try {
      let response;
      
      if (action === 'buy') {
        response = await axios.post('/buy-stock', {
          symbol: selectedStock.symbol,
          quantity: quantity
        });
      } else {
        // Handle sell action
        response = await axios.post('/sell-stock', {
          symbol: selectedStock.symbol,
          quantity: quantity
        });
      }
      
      if (response.data.success) {
        onSuccess && onSuccess(response.data);
        onClose();
      } else {
        setError(response.data.error || `Failed to ${action} stock`);
      }
    } catch (error) {
      console.error(`${action} error:`, error);
      
      // Handle different types of errors
      let errorMessage = `Failed to ${action} stock. Please try again.`;
      
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
    setCurrentShares(0); // No current shares for new stock
    setTargetShares(1); // Start with 1 share
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchStocks();
    }
  };

  const handleQuantityChange = (newQuantity) => {
    const validQuantity = Math.max(1, Math.min(maxAffordableShares, parseInt(newQuantity) || 1));
    setQuantity(validQuantity);
    
    if (existingHolding) {
      setTargetShares(currentShares + validQuantity);
    } else if (selectedStock) {
      setTargetShares(validQuantity);
    }
  };

  const handleSliderChange = (newValue) => {
    const newTargetShares = parseInt(newValue);
    setTargetShares(newTargetShares);
  };

  if (!isOpen) return null;

  return (
    <div className={`buy-stock-overlay ${isMobile ? 'mobile' : ''}`}>
      <div className={`buy-stock-modal ${isMobile ? 'mobile' : ''} ${selectedStock ? 'adjust-modal' : ''}`}>
        <div className="modal-header">
          <h2>
            {existingHolding ? 
              sharesDifference > 0 ? 
                `Buy More ${existingHolding.symbol}` : 
                sharesDifference < 0 ? 
                  `Sell ${existingHolding.symbol}` : 
                  `Adjust ${existingHolding.symbol}` 
              : selectedStock ? `Buy ${selectedStock.symbol}` : 'Buy Stock'}
          </h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-content">
          {!selectedStock ? (
            // Stock Search View
            <div className="stock-search">
              <div className="search-box">
                <input
                  type="text"
                  placeholder="Search by symbol or company name"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  autoFocus
                />
                <button 
                  className="search-button"
                  onClick={searchStocks}
                  disabled={isSearching || !searchQuery.trim()}
                >
                  {isSearching ? 'Searching...' : 'Search'}
                </button>
              </div>
              
              {error && <div className="error-message">{error}</div>}
              
              {isSearching ? (
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <p>Searching for stocks...</p>
                </div>
              ) : (
                <div className="search-results">
                  {searchResults.length > 0 ? (
                    <ul className="stock-list">
                      {searchResults.map((stock, index) => (
                        <li key={index} className="stock-item" onClick={() => handleStockSelect(stock)}>
                          <div className="stock-symbol">{stock.symbol}</div>
                          <div className="stock-name">{stock.name}</div>
                          {stock.current_price && (
                            <div className="stock-price">${stock.current_price.toFixed(2)}</div>
                          )}
                        </li>
                      ))}
                    </ul>
                  ) : searchQuery.trim() ? (
                    <div className="no-results">No stocks found matching "{searchQuery}"</div>
                  ) : null}
                </div>
              )}
            </div>
          ) : (
            // Stock Purchase View with Slider (for both new and existing)
            <div className="stock-purchase adjust-position">
              {/* Current Position Info */}
              <div className="selected-stock">
                <h3>Current Position:</h3>
                <div className="stock-card">
                  <div className="stock-header">
                    <span className="symbol">{selectedStock.symbol}</span>
                    <span className="name">Current: {currentShares} shares</span>
                  </div>
                  <div className="price-info">
                    <span className="current-price">
                      Current Price: ${affordability?.current_price?.toFixed(2) || '0.00'}
                    </span>
                    <span className="position-value">
                      Position Value: ${((currentShares * (affordability?.current_price || 0))).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Position Slider */}
              <div className="slider-section">
                <label>{existingHolding ? 'Adjust Position:' : 'Shares to Buy:'}</label>
                <div className="slider-container">
                  <div className="slider-labels">
                    <span className="slider-label sell">{existingHolding ? 'Sell All (0)' : 'Min (1)'}</span>
                    {existingHolding && <span className="slider-label current">Current ({currentShares})</span>}
                    <span className="slider-label buy">Max ({maxAffordableShares})</span>
                  </div>
                  <input
                    type="range"
                    min={existingHolding ? 0 : 1}
                    max={maxAffordableShares}
                    value={targetShares}
                    onChange={(e) => handleSliderChange(e.target.value)}
                    className="position-slider"
                    step="1"
                  />
                  <div className="slider-markers">
                    {existingHolding && (
                      <div 
                        className="marker sell-all" 
                        style={{ left: '0%' }}
                      />
                    )}
                    {existingHolding && (
                      <div 
                        className="marker current-position" 
                        style={{ left: `${(currentShares / maxAffordableShares) * 100}%` }}
                      />
                    )}
                    <div 
                      className="marker max-position" 
                      style={{ left: '100%' }}
                    />
                  </div>
                </div>
                
                {/* Target Shares Display */}
                <div className="target-display">
                  <span className="target-label">Target Shares:</span>
                  <input
                    type="number"
                    min={existingHolding ? 0 : 1}
                    max={maxAffordableShares}
                    value={targetShares}
                    onChange={(e) => handleSliderChange(e.target.value)}
                    className="target-input"
                  />
                </div>
              </div>

              {/* Real-time Stats */}
              {affordability && (
                <div className="stats-section">
                  <div className="stats-header">
                    <h4 className={sharesDifference > 0 ? "buying" : sharesDifference < 0 ? "selling" : "no-change"}>
                      {sharesDifference > 0 ? 
                        `📈 Buying ${sharesDifference} More Shares` : 
                        sharesDifference < 0 ? 
                          `📉 Selling ${Math.abs(sharesDifference)} Shares` : 
                          `No Change in Position`}
                    </h4>
                  </div>
                  
                  <div className="stats-grid">
                    <div className="stat-item">
                      <span className="stat-label">Position Change:</span>
                      <span className={`stat-value ${sharesDifference > 0 ? 'positive' : sharesDifference < 0 ? 'negative' : ''}`}>
                        {sharesDifference > 0 ? `+${sharesDifference}` : sharesDifference} shares
                      </span>
                    </div>
                    
                    <div className="stat-item">
                      <span className="stat-label">{sharesDifference >= 0 ? 'Cost:' : 'Proceeds:'}</span>
                      <span className={`stat-value ${sharesDifference < 0 ? 'positive' : ''}`}>
                        ${Math.abs(sharesDifference * (affordability.current_price || 0)).toFixed(2)}
                      </span>
                    </div>
                    
                    <div className="stat-item">
                      <span className="stat-label">New Position Value:</span>
                      <span className="stat-value">
                        ${(targetShares * (affordability.current_price || 0)).toFixed(2)}
                      </span>
                    </div>
                    
                    <div className="stat-item">
                      <span className="stat-label">Remaining Cash:</span>
                      <span className={`stat-value ${sharesDifference >= 0 ? (affordability.can_afford ? 'positive' : 'negative') : 'positive'}`}>
                        ${(sharesDifference >= 0 ? 
                          (affordability.available_cash - (sharesDifference * (affordability.current_price || 0))) : 
                          (affordability.available_cash + Math.abs(sharesDifference * (affordability.current_price || 0)))).toFixed(2)}
                      </span>
                    </div>
                  </div>

                  {/* Affordability Warning */}
                  {sharesDifference > 0 && !affordability.can_afford && (
                    <div className="affordability-warning">
                      <span className="warning-icon">⚠️</span>
                      <span>Insufficient funds! Shortfall: ${affordability.shortfall.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          
          {error && <div className="error-message">{error}</div>}
          
          <div className="action-buttons">
            <button 
              className="cancel-button"
              onClick={onClose}
            >
              Cancel
            </button>
            <button 
              className={`${action}-button`}
              onClick={handleTransaction}
              disabled={isBuying || 
                !affordability || 
                (action === 'buy' && (!affordability.can_afford || sharesDifference <= 0)) ||
                (sharesDifference === 0)}
            >
              {isBuying ? 'Processing...' : 
                sharesDifference > 0 ? 
                  `Buy ${sharesDifference} More Shares` : 
                  sharesDifference < 0 ? 
                    `Sell ${Math.abs(sharesDifference)} Shares` : 
                    'No Change'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyStock; 