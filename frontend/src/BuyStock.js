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
  const [hasSearched, setHasSearched] = useState(false);
  const [isBuying, setIsBuying] = useState(false);
  const [affordability, setAffordability] = useState(null);
  const [error, setError] = useState('');
  const [currentShares, setCurrentShares] = useState(0);
  const [targetShares, setTargetShares] = useState(0);
  const [sharesDifference, setSharesDifference] = useState(0);
  const [action, setAction] = useState('buy'); // 'buy' or 'sell'
  const [sliderMax, setSliderMax] = useState(1);
  const [maxBuyableShares, setMaxBuyableShares] = useState(0);

  // Helper function to round to 2 decimal places
  const roundToTwoDecimals = (num) => {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  };

  const searchStocks = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setHasSearched(true);
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
    if (!selectedStock || !currentPrice) return;
    
    try {
      // Get user's cash balance using the optimized endpoint
      const response = await axios.get('/cash-balance');
      const cashBalance = response.data.cash_balance;
      const maxAffordableShares = Math.floor(cashBalance / currentPrice);
      
      setMaxBuyableShares(maxAffordableShares);
      setAffordability({
        can_afford: true, // We'll check this based on target shares later
        total_cost: 0, // Will be calculated based on target shares
        available_cash: cashBalance,
        shortfall: 0, // Will be calculated based on target shares
        max_affordable_shares: maxAffordableShares,
        current_price: currentPrice,
        cached: true
      });
      
      console.log(`💰 Using cached price: ${selectedStock.symbol} @ $${currentPrice} (saved API call)`);
    } catch (error) {
      console.error('Cached affordability check error:', error);
      // Fallback to regular affordability check
      if (selectedStock) {
        try {
          const response = await axios.get(`/check-affordability/${selectedStock.symbol}?quantity=1`);
          setMaxBuyableShares(response.data.max_affordable_shares || 0);
          setAffordability(response.data);
        } catch (fallbackError) {
          console.error('Fallback affordability check error:', fallbackError);
          setAffordability(null);
        }
      }
    }
  }, [selectedStock]);

  const checkAffordability = useCallback(async () => {
    if (!selectedStock) return;
    
    try {
      const response = await axios.get(`/check-affordability/${selectedStock.symbol}?quantity=1`);
      setMaxBuyableShares(response.data.max_affordable_shares || 0);
      setAffordability(response.data);
    } catch (error) {
      console.error('Affordability check error:', error);
      setAffordability(null);
    }
  }, [selectedStock]);

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
        const shares = roundToTwoDecimals(existingHolding.shares || existingHolding.quantity || 0);
        setCurrentShares(shares);
        setTargetShares(shares); // Start at current position
        setSearchQuery('');
        setSearchResults([]);
        setHasSearched(false);
      } else {
        // New stock purchase
        setSearchQuery('');
        setSearchResults([]);
        setHasSearched(false);
        setSelectedStock(null);
        setCurrentShares(0);
        setTargetShares(1); // Start with 1 for new purchases
      }
      setMaxAffordableShares(1);
      setAffordability(null);
      setError('');
      setAction('buy');
      setSliderMax(1);
      setMaxBuyableShares(0);
    }
  }, [isOpen, existingHolding]);

  // Check affordability when stock changes
  useEffect(() => {
    if (selectedStock) {
      // If we have cached price data, use it directly
      if (selectedStock.current_price && selectedStock.cached) {
        // We'll need to get cash balance, but we can skip the price lookup
        checkAffordabilityWithPrice(selectedStock.current_price);
      } else {
        checkAffordability();
      }
    }
  }, [selectedStock, checkAffordability, checkAffordabilityWithPrice]);

  // Update max affordable shares when affordability data changes
  useEffect(() => {
    if (affordability) {
      const maxBuyable = Math.max(0, maxBuyableShares);
      setMaxAffordableShares(maxBuyable);
      
      // Set the slider max to current + max affordable
      if (existingHolding) {
        // IMPORTANT: Make sure max is at least the current shares
        // This ensures you can always sell down to 0, even with no cash
        const newSliderMax = Math.max(currentShares, currentShares + maxBuyable);
        setSliderMax(roundToTwoDecimals(newSliderMax));
      } else {
        setSliderMax(Math.max(1, maxBuyable));
      }
    }
  }, [affordability, existingHolding, currentShares, maxBuyableShares]);

  // Update shares difference when target shares change
  useEffect(() => {
    if (existingHolding) {
      const difference = roundToTwoDecimals(targetShares - currentShares);
      setSharesDifference(difference);
      setQuantity(roundToTwoDecimals(Math.abs(difference)));
      setAction(difference >= 0 ? 'buy' : 'sell');
      
      // Update affordability check based on target
      if (affordability && affordability.current_price) {
        const price = affordability.current_price;
        const cost = difference * price;
        const canAfford = difference <= 0 || (affordability.available_cash >= cost);
        
        setAffordability(prev => ({
          ...prev,
          can_afford: canAfford,
          total_cost: Math.abs(cost),
          shortfall: canAfford ? 0 : cost - affordability.available_cash
        }));
      }
    } else if (selectedStock) {
      // For new purchases, target shares equals quantity
      setSharesDifference(roundToTwoDecimals(targetShares));
      setQuantity(roundToTwoDecimals(targetShares));
      
      // Update affordability check based on target
      if (affordability && affordability.current_price) {
        const price = affordability.current_price;
        const cost = targetShares * price;
        const canAfford = affordability.available_cash >= cost;
        
        setAffordability(prev => ({
          ...prev,
          can_afford: canAfford,
          total_cost: cost,
          shortfall: canAfford ? 0 : cost - affordability.available_cash
        }));
      }
    }
  }, [targetShares, currentShares, existingHolding, selectedStock, affordability]);

  const handleTransaction = async () => {
    if (!selectedStock || (action === 'buy' && quantity <= 0)) return;
    
    setIsBuying(true);
    setError('');
    
    try {
      let response;
      const roundedQuantity = roundToTwoDecimals(quantity);
      
      if (action === 'buy') {
        response = await axios.post('/buy-stock', {
          symbol: selectedStock.symbol,
          quantity: roundedQuantity
        });
      } else {
        // Handle sell action
        response = await axios.post('/sell-stock', {
          symbol: selectedStock.symbol,
          quantity: roundedQuantity
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
    const parsedQuantity = parseFloat(newQuantity) || 0;
    const roundedQuantity = roundToTwoDecimals(parsedQuantity);
    
    if (existingHolding) {
      // For existing holdings, ensure we don't exceed slider bounds
      const validTarget = Math.max(0, Math.min(sliderMax, roundedQuantity));
      setTargetShares(validTarget);
    } else if (selectedStock) {
      // For new purchases, ensure we don't exceed max affordable
      const validQuantity = Math.max(1, Math.min(maxAffordableShares, roundedQuantity));
      setTargetShares(validQuantity);
    }
  };

  const handleSliderChange = (newValue) => {
    const newTargetShares = roundToTwoDecimals(parseFloat(newValue));
    setTargetShares(newTargetShares);
  };

  // Calculate slider position percentages for markers
  const getSliderPosition = useCallback((value) => {
    if (!existingHolding) return 0;
    const min = 0;
    const max = sliderMax;
    return ((value - min) / (max - min)) * 100;
  }, [existingHolding, sliderMax]);

  // Set the CSS variable for the slider gradient
  useEffect(() => {
    if (existingHolding) {
      const currentPosition = getSliderPosition(currentShares);
      document.documentElement.style.setProperty('--current-position', `${currentPosition}%`);
    } else {
      document.documentElement.style.setProperty('--current-position', '30%');
    }
    
    // Clean up on unmount
    return () => {
      document.documentElement.style.removeProperty('--current-position');
    };
  }, [existingHolding, currentShares, sliderMax, getSliderPosition]);

  // Get the max display value
  const getMaxDisplay = () => {
    if (!existingHolding) return roundToTwoDecimals(maxAffordableShares);
    
    // For existing holdings, show the total max shares (current + additional)
    return roundToTwoDecimals(sliderMax);
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
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setHasSearched(false); // Reset search state when typing
                  }}
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
                          <div className="stock-info">
                            <div className="stock-symbol">{stock.symbol}</div>
                            <div className="stock-name">{stock.name}</div>
                            <div className="stock-details">
                              {stock.exchange && <span className="stock-exchange">{stock.exchange}</span>}
                              {stock.region && stock.region !== 'United States' && <span className="stock-region">{stock.region}</span>}
                              {stock.currency && stock.currency !== 'USD' && <span className="stock-currency">{stock.currency}</span>}
                            </div>
                          </div>
                          {stock.current_price && (
                            <div className="stock-price">${stock.current_price.toFixed(2)}</div>
                          )}
                        </li>
                      ))}
                    </ul>
                  ) : hasSearched && searchQuery.trim() ? (
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
                    <span className="name">Current: {currentShares.toFixed(2)} shares</span>
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
                    <span className="slider-label sell">Sell All (0)</span>
                    {existingHolding && <span className="slider-label current">Current ({currentShares.toFixed(2)})</span>}
                    <span className="slider-label buy">Max ({getMaxDisplay().toFixed(2)})</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max={sliderMax}
                    value={targetShares}
                    onChange={(e) => handleSliderChange(e.target.value)}
                    className="position-slider"
                    step="0.01"
                  />
                  <div className="slider-markers">
                    <div 
                      className="marker sell-all" 
                      style={{ left: '0%' }}
                    />
                    {existingHolding && (
                      <div 
                        className="marker current-position" 
                        style={{ left: `${getSliderPosition(currentShares)}%` }}
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
                    min="0"
                    max={sliderMax}
                    step="0.01"
                    value={targetShares}
                    onChange={(e) => handleQuantityChange(e.target.value)}
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
                        `📈 Buying ${sharesDifference.toFixed(2)} More Shares` : 
                        sharesDifference < 0 ? 
                          `📉 Selling ${Math.abs(sharesDifference).toFixed(2)} Shares` : 
                          `No Change in Position`}
                    </h4>
                  </div>
                  
                  <div className="stats-grid">
                    <div className="stat-item">
                      <span className="stat-label">Position Change:</span>
                      <span className={`stat-value ${sharesDifference > 0 ? 'positive' : sharesDifference < 0 ? 'negative' : ''}`}>
                        {sharesDifference > 0 ? `+${sharesDifference.toFixed(2)}` : sharesDifference.toFixed(2)} shares
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
                  `Buy ${sharesDifference.toFixed(2)} More Shares` : 
                  sharesDifference < 0 ? 
                    `Sell ${Math.abs(sharesDifference).toFixed(2)} Shares` : 
                    'No Change'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyStock; 