import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './BuyStock.css'; // Reuse the same styles

const AdjustHolding = ({ isOpen, onClose, onSuccess, holding }) => {
  const [targetShares, setTargetShares] = useState(0);
  const [maxAffordableShares, setMaxAffordableShares] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [affordability, setAffordability] = useState(null);
  const [error, setError] = useState('');
  const [showSellAllConfirm, setShowSellAllConfirm] = useState(false);
  const [cashBalance, setCashBalance] = useState(0);

  const fetchCashBalance = async () => {
    try {
      const response = await axios.get('/cash-balance');
      setCashBalance(response.data.cash_balance || 0);
    } catch (error) {
      console.error('Error fetching cash balance:', error);
      setCashBalance(0);
    }
  };

  const calculateMaxAffordable = useCallback(async () => {
    if (!holding) return;
    
    try {
      // Get current price and calculate max affordable shares
      const currentPrice = holding.current_price || 0;
      const currentShares = holding.shares || holding.quantity || 0;
      
      if (currentPrice > 0) {
        const maxBuyable = cashBalance > 0 ? Math.floor(cashBalance / currentPrice) : 0;
        setMaxAffordableShares(currentShares + maxBuyable);
      } else {
        setMaxAffordableShares(currentShares);
      }
    } catch (error) {
      console.error('Error calculating max affordable:', error);
      setMaxAffordableShares(holding.shares || holding.quantity || 0);
    }
  }, [holding, cashBalance]);

  const updateStats = useCallback(() => {
    if (!holding) return;

    const currentShares = holding.shares || holding.quantity || 0;
    const currentPrice = holding.current_price || 0;
    const sharesDifference = targetShares - currentShares;
    
    if (sharesDifference === 0) {
      // No change
      setAffordability({
        action: 'hold',
        shares_change: 0,
        cost_change: 0,
        can_afford: true,
        new_position_value: currentShares * currentPrice,
        remaining_cash: cashBalance
      });
    } else if (sharesDifference > 0) {
      // Buying more shares
      const additionalCost = sharesDifference * currentPrice;
      const canAfford = additionalCost <= cashBalance;
      
      setAffordability({
        action: 'buy',
        shares_change: sharesDifference,
        cost_change: additionalCost,
        can_afford: canAfford,
        new_position_value: targetShares * currentPrice,
        remaining_cash: cashBalance - additionalCost,
        shortfall: canAfford ? 0 : additionalCost - cashBalance
      });
    } else {
      // Selling shares
      const sharesBeingSold = Math.abs(sharesDifference);
      const proceeds = sharesBeingSold * currentPrice;
      
      setAffordability({
        action: 'sell',
        shares_change: sharesDifference,
        cost_change: -proceeds, // Negative because it's income
        can_afford: true, // Can always sell what you own
        new_position_value: targetShares * currentPrice,
        remaining_cash: cashBalance + proceeds,
        proceeds: proceeds
      });
    }
  }, [holding, targetShares, cashBalance]);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen && holding) {
      const currentShares = holding.shares || holding.quantity || 0;
      setTargetShares(currentShares);
      setError('');
      setShowSellAllConfirm(false);
      fetchCashBalance();
    }
  }, [isOpen, holding]);

  // Calculate max affordable when cash balance is available
  useEffect(() => {
    if (holding && cashBalance >= 0) {
      calculateMaxAffordable();
    }
  }, [holding, cashBalance, calculateMaxAffordable]);

  // Update stats when target shares change
  useEffect(() => {
    if (holding && targetShares >= 0 && maxAffordableShares >= 0) {
      updateStats();
    }
  }, [holding, targetShares, cashBalance, maxAffordableShares, updateStats]);

  const handleAdjust = async () => {
    if (!holding || !affordability) return;
    
    const currentShares = holding.shares || holding.quantity || 0;
    const sharesDifference = targetShares - currentShares;
    
    if (sharesDifference === 0) {
      onClose();
      return;
    }

    setIsProcessing(true);
    setError('');
    
    try {
      const action = sharesDifference > 0 ? 'buy' : 'sell';
      const shares = Math.abs(sharesDifference);
      
      const response = await axios.post('/trade', {
        symbol: holding.symbol,
        shares: shares,
        action: action
      });
      
      if (response.data.success) {
        onSuccess && onSuccess(response.data);
      } else {
        setError(response.data.message || 'Failed to adjust holding');
      }
    } catch (error) {
      console.error('Adjust error:', error);
      
      let errorMessage = 'Failed to adjust holding. Please try again.';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        }
      }
      
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSellAll = async () => {
    const totalShares = holding.shares || holding.quantity || 0;
    
    setIsProcessing(true);
    setError('');
    
    try {
      const response = await axios.post('/trade', {
        symbol: holding.symbol,
        shares: totalShares,
        action: 'sell'
      });
      
      if (response.data.success) {
        onSuccess && onSuccess(response.data);
      } else {
        setError(response.data.message || 'Failed to sell all shares');
      }
    } catch (error) {
      console.error('Sell all error:', error);
      setError('Failed to sell all shares. Please try again.');
    } finally {
      setIsProcessing(false);
      setShowSellAllConfirm(false);
    }
  };

  if (!isOpen || !holding) return null;

  const currentShares = holding.shares || holding.quantity || 0;
  const currentPrice = holding.current_price || 0;
  const symbol = holding.symbol;
  const sharesDifference = targetShares - currentShares;

  return (
    <div className="buy-stock-overlay">
      <div className="buy-stock-modal adjust-modal">
        <div className="buy-stock-header">
          <h2>Adjust Position: {symbol}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="buy-stock-content">
          {/* Current Position Info */}
          <div className="selected-stock">
            <h3>Current Position:</h3>
            <div className="stock-card">
              <div className="stock-header">
                <span className="symbol">{symbol}</span>
                <span className="name">Current: {currentShares} shares</span>
              </div>
              <div className="price-info">
                <span className="current-price">
                  Current Price: ${currentPrice.toFixed(2)}
                </span>
                <span className="current-value">
                  Position Value: ${(currentShares * currentPrice).toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Position Slider */}
          <div className="slider-section">
            <label>Adjust Position:</label>
            <div className="slider-container">
              <div className="slider-labels">
                <span className="slider-label sell">Sell All (0)</span>
                <span className="slider-label current">Current ({currentShares})</span>
                <span className="slider-label buy">Max ({maxAffordableShares})</span>
              </div>
              <input
                type="range"
                min="0"
                max={maxAffordableShares}
                value={targetShares}
                onChange={(e) => setTargetShares(parseInt(e.target.value))}
                className="position-slider"
                step="1"
              />
              <div className="slider-markers">
                <div 
                  className="marker sell-all" 
                  style={{ left: '0%' }}
                />
                <div 
                  className="marker current-position" 
                  style={{ left: `${(currentShares / maxAffordableShares) * 100}%` }}
                />
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
                max={maxAffordableShares}
                value={targetShares}
                onChange={(e) => setTargetShares(Math.max(0, Math.min(maxAffordableShares, parseInt(e.target.value) || 0)))}
                className="target-input"
              />
            </div>
          </div>

          {/* Real-time Stats */}
          {affordability && (
            <div className="stats-section">
              <div className="stats-header">
                <h4 className={
                  affordability.action === 'hold' ? 'no-change' :
                  affordability.action === 'buy' ? 'buying' : 'selling'
                }>
                  {affordability.action === 'hold' && '📊 No Change'}
                  {affordability.action === 'buy' && `📈 Buying ${Math.abs(sharesDifference)} Shares`}
                  {affordability.action === 'sell' && `📉 Selling ${Math.abs(sharesDifference)} Shares`}
                </h4>
              </div>
              
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Position Change:</span>
                  <span className={`stat-value ${sharesDifference > 0 ? 'positive' : sharesDifference < 0 ? 'negative' : 'neutral'}`}>
                    {sharesDifference > 0 ? '+' : ''}{sharesDifference} shares
                  </span>
                </div>
                
                <div className="stat-item">
                  <span className="stat-label">
                    {affordability.action === 'buy' ? 'Cost:' : affordability.action === 'sell' ? 'Proceeds:' : 'Cost:'}
                  </span>
                  <span className={`stat-value ${affordability.action === 'sell' ? 'positive' : 'neutral'}`}>
                    {affordability.action === 'sell' ? '+' : affordability.cost_change !== 0 ? '-' : ''}${Math.abs(affordability.cost_change).toFixed(2)}
                  </span>
                </div>
                
                <div className="stat-item">
                  <span className="stat-label">New Position Value:</span>
                  <span className="stat-value">${affordability.new_position_value.toFixed(2)}</span>
                </div>
                
                <div className="stat-item">
                  <span className="stat-label">Remaining Cash:</span>
                  <span className={`stat-value ${affordability.remaining_cash < 0 ? 'negative' : 'positive'}`}>
                    ${affordability.remaining_cash.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Affordability Warning */}
              {!affordability.can_afford && (
                <div className="affordability-warning">
                  <span className="warning-icon">⚠️</span>
                  <span>Insufficient funds! Shortfall: ${affordability.shortfall.toFixed(2)}</span>
                </div>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="action-buttons">
            <button 
              onClick={onClose}
              className="back-button"
            >
              Cancel
            </button>
            
            {targetShares === 0 && (
              <button 
                onClick={() => setShowSellAllConfirm(true)}
                className="sell-all-button"
                disabled={isProcessing}
              >
                🔥 Sell All Position
              </button>
            )}
            
            <button 
              onClick={handleAdjust}
              disabled={isProcessing || !affordability?.can_afford || sharesDifference === 0}
              className={`confirm-button ${
                sharesDifference > 0 ? 'buy-button' : 
                sharesDifference < 0 ? 'sell-button' : 
                'neutral-button'
              }`}
            >
              {isProcessing ? 'Processing...' : 
               sharesDifference === 0 ? 'No Change' :
               sharesDifference > 0 ? `Buy ${Math.abs(sharesDifference)} Shares` : 
               `Sell ${Math.abs(sharesDifference)} Shares`}
            </button>
          </div>
        </div>
      </div>

      {/* Sell All Confirmation Modal */}
      {showSellAllConfirm && (
        <div className="buy-stock-overlay">
          <div className="buy-stock-modal confirm-modal">
            <div className="buy-stock-header">
              <h2>Confirm Sell All</h2>
            </div>
            <div className="buy-stock-content">
              <div className="confirm-message">
                <p>Are you sure you want to sell ALL {currentShares} shares of {symbol}?</p>
                <p>This will completely remove this holding from your portfolio.</p>
                <div className="confirm-details">
                  <strong>Estimated Proceeds: ${(currentShares * currentPrice).toFixed(2)}</strong>
                </div>
              </div>
              <div className="action-buttons">
                <button 
                  onClick={() => setShowSellAllConfirm(false)}
                  className="back-button"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleSellAll}
                  disabled={isProcessing}
                  className="confirm-sell-all-button"
                >
                  {isProcessing ? 'Selling...' : 'Yes, Sell All'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdjustHolding; 