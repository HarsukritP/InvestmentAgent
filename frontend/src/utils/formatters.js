/**
 * Format a number as currency (USD)
 * @param {number} value - The value to format
 * @returns {string} - Formatted currency string
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined) return '$0.00';
  
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
 * @param {number} value - The value to format as percentage
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted percentage string
 */
export const formatPercentage = (value, decimals = 2) => {
  if (value === null || value === undefined) return '0%';
  
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value / 100);
}; 