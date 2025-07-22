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
        setSearchQuery('');
        setSearchResults([]);
      } else {
        // New stock purchase
        setSearchQuery('');
        setSearchResults([]);
        setSelectedStock(null);
        setCurrentShares(0);
        setQuantity(1);
      }
      setMaxAffordableShares(1);
      setAffordability(null);
      setError('');
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
    <div className={`buy-stock-overlay ${isMobile ? 'mobile' : ''}`}>
      <div className={`buy-stock-modal ${isMobile ? 'mobile' : ''}`}>
        <div className="modal-header">
          <h2>{existingHolding ? `Buy More ${existingHolding.symbol}` : 'Buy Stock'}</h2>
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
            // Stock Purchase View
            <div className="stock-purchase">
              <div className="selected-stock">
                <div className="stock-header">
                  <div className="stock-symbol">{selectedStock.symbol}</div>
                  <div className="stock-name">{selectedStock.name}</div>
                </div>
                
                {currentShares > 0 && (
                  <div className="current-position">
                    <div className="position-label">Current Position</div>
                    <div className="position-value">{currentShares} shares</div>
                  </div>
                )}
                
                {affordability && (
                  <div className="stock-price-info">
                    <div className="price-label">Current Price</div>
                    <div className="price-value">${affordability.current_price.toFixed(2)}</div>
                  </div>
                )}
              </div>
              
              <div className="purchase-form">
                <div className="quantity-selector">
                  <label htmlFor="quantity">Quantity to Buy</label>
                  <div className="quantity-controls">
                    <button 
                      className="quantity-btn"
                      onClick={() => handleQuantityChange(quantity - 1)}
                      disabled={quantity <= 1}
                    >
                      -
                    </button>
                    <input
                      id="quantity"
                      type="number"
                      min="1"
                      max={maxAffordableShares}
                      value={quantity}
                      onChange={(e) => handleQuantityChange(e.target.value)}
                    />
                    <button 
                      className="quantity-btn"
                      onClick={() => handleQuantityChange(quantity + 1)}
                      disabled={quantity >= maxAffordableShares}
                    >
                      +
                    </button>
                  </div>
                </div>
                
                {affordability && (
                  <div className="purchase-summary">
                    <div className="summary-row">
                      <div className="summary-label">Total Cost</div>
                      <div className="summary-value">${affordability.total_cost.toFixed(2)}</div>
                    </div>
                    <div className="summary-row">
                      <div className="summary-label">Available Cash</div>
                      <div className="summary-value">${affordability.available_cash.toFixed(2)}</div>
                    </div>
                    {!affordability.can_afford && (
                      <div className="summary-row error">
                        <div className="summary-label">Shortfall</div>
                        <div className="summary-value">${affordability.shortfall.toFixed(2)}</div>
                      </div>
                    )}
                    <div className="summary-row">
                      <div className="summary-label">Max Shares</div>
                      <div className="summary-value">{affordability.max_affordable_shares}</div>
                    </div>
                    
                    {currentShares > 0 && (
                      <div className="summary-row total">
                        <div className="summary-label">New Position Total</div>
                        <div className="summary-value">{currentShares + quantity} shares</div>
                      </div>
                    )}
                  </div>
                )}
                
                {error && <div className="error-message">{error}</div>}
                
                <div className="action-buttons">
                  <button 
                    className="cancel-button"
                    onClick={() => existingHolding ? onClose() : setSelectedStock(null)}
                  >
                    {existingHolding ? 'Cancel' : 'Back'}
                  </button>
                  <button 
                    className="buy-button"
                    onClick={handleBuyStock}
                    disabled={
                      isBuying || 
                      !affordability || 
                      !affordability.can_afford || 
                      quantity <= 0
                    }
                  >
                    {isBuying ? 'Processing...' : currentShares > 0 ? 'Buy More' : 'Buy Now'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BuyStock; 