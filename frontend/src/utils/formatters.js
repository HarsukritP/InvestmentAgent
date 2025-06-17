/**
 * Format a number as currency (USD)
 * @param {number} value - The value to format
 * @returns {string} - Formatted currency string
 */
export const formatCurrency = (value) => {
  if (value === undefined || value === null || isNaN(value)) {
    return '$0.00';
  }
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

/**
 * Format a date string to a readable format
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
export const formatDate = (dateString) => {
  if (!dateString) return '-';
  
  try {
    const date = new Date(dateString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return '-';
    }
    
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  } catch (error) {
    console.error('Error formatting date:', error);
    return '-';
  }
};

/**
 * Format a number with commas for thousands
 * @param {number} value - The value to format
 * @returns {string} - Formatted number string
 */
export const formatNumber = (value) => {
  if (value === null || value === undefined) return '0';
  
  return new Intl.NumberFormat('en-US').format(value);
};

/**
 * Format a percentage value
 * @param {number} value - The percentage value
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value) => {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.00%';
  }
  
  const formatted = value.toFixed(2);
  return value >= 0 ? `+${formatted}%` : `${formatted}%`;
};

/**
 * Get CSS class name based on value (positive/negative/neutral)
 * @param {number} value - The value to check
 * @returns {string} CSS class name
 */
export const getValueClass = (value) => {
  if (value === undefined || value === null || isNaN(value)) {
    return 'neutral';
  }
  return value >= 0 ? 'positive' : 'negative';
};

/**
 * Check if the US stock market is currently open
 * @returns {boolean} True if market is open
 */
export const isMarketOpen = () => {
  // Get current time in Eastern Time
  const now = new Date();
  const options = { timeZone: 'America/New_York' };
  const nyTime = new Date(now.toLocaleString('en-US', options));
  
  // Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
  const hour = nyTime.getHours();
  const minute = nyTime.getMinutes();
  const day = nyTime.getDay(); // 0 = Sunday, 6 = Saturday
  
  // Check if it's a weekday
  if (day === 0 || day === 6) {
    return false;
  }
  
  // Check if within market hours (9:30 AM - 4:00 PM)
  if ((hour === 9 && minute >= 30) || (hour > 9 && hour < 16)) {
    return true;
  }
  
  return false;
};

/**
 * Get the market status with next update time
 * @param {Object} healthStatus - The health status object from the API
 * @returns {Object} Market status object with text, class, and next update info
 */
export const getMarketStatus = (healthStatus) => {
  if (!healthStatus || !healthStatus.services || !healthStatus.services.market_data) {
    return { 
      text: 'Market Status Unknown', 
      class: 'neutral',
      nextUpdate: null
    };
  }
  
  const marketData = healthStatus.services.market_data;
  const autoRefresh = marketData.auto_refresh;
  
  if (!autoRefresh) {
    return { 
      text: 'Auto-Refresh Disabled', 
      class: 'warning',
      nextUpdate: null
    };
  }
  
  const isOpen = autoRefresh.market_status === 'open';
  const nextUpdateSeconds = autoRefresh.next_refresh_in_seconds || 0;
  const nextUpdateMinutes = Math.ceil(nextUpdateSeconds / 60);
  
  return {
    text: isOpen ? 'Market Open' : 'Market Closed',
    class: isOpen ? 'success' : 'neutral',
    nextUpdate: `Next update in ${nextUpdateMinutes} min`,
    refreshInterval: autoRefresh.refresh_interval_minutes
  };
}; 