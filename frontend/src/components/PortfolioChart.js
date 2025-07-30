import React, { useState } from 'react';
import StockChart from './StockChart';
import './PortfolioChart.css';

const PortfolioChart = ({ holdings }) => {
  const [selectedSymbol, setSelectedSymbol] = useState(holdings?.[0]?.symbol || 'AAPL');
  const [chartPeriod, setChartPeriod] = useState('6months');

  if (!holdings || holdings.length === 0) {
    return (
      <div className="portfolio-chart-container">
        <div className="no-holdings-chart">
          <h3>📈 Portfolio Charts</h3>
          <p>Add holdings to your portfolio to see interactive charts</p>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio-chart-container">
      <div className="chart-header">
        <h3>📈 Portfolio Charts</h3>
        <div className="chart-controls-row">
          <div className="symbol-selector">
            <label>Stock:</label>
            <select 
              value={selectedSymbol} 
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="symbol-select"
            >
              {holdings.map(holding => (
                <option key={holding.symbol} value={holding.symbol}>
                  {holding.symbol}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      <div className="chart-content">
        <StockChart 
          symbol={selectedSymbol}
          period={chartPeriod}
          height={400}
          showControls={true}
        />
      </div>
      
      {holdings.length > 1 && (
        <div className="holdings-mini-charts">
          <h4>All Holdings Overview</h4>
          <div className="mini-charts-grid">
            {holdings.slice(0, 4).map(holding => (
              <div key={holding.symbol} className="mini-chart-card">
                <div className="mini-chart-header">
                  <span className="mini-symbol">{holding.symbol}</span>
                  <span className={`mini-change ${holding.profit_loss >= 0 ? 'positive' : 'negative'}`}>
                    {holding.profit_loss >= 0 ? '+' : ''}{holding.profit_loss_percent?.toFixed(2)}%
                  </span>
                </div>
                <StockChart 
                  symbol={holding.symbol}
                  period="1month"
                  height={120}
                  showControls={false}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioChart;