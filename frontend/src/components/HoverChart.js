import React, { useState, useEffect, useRef, useCallback } from 'react';
import './HoverChart.css';

// Mini chart using Chart.js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const HoverChart = ({ symbol, isVisible, position, onMouseLeave }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const chartRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (isVisible && symbol) {
      fetchIntradayData();
    }
  }, [isVisible, symbol, fetchIntradayData]);

  // Position the tooltip to avoid screen edges
  useEffect(() => {
    if (containerRef.current && position) {
      const container = containerRef.current;
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      
      let left = position.x + 15;
      let top = position.y + 15;
      
      // Adjust if tooltip would go off screen
      if (left + 320 > viewportWidth) {
        left = position.x - 320 - 15;
      }
      if (top + 200 > viewportHeight) {
        top = position.y - 200 - 15;
      }
      
      container.style.left = `${left}px`;
      container.style.top = `${top}px`;
    }
  }, [position]);

  const fetchIntradayData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/intraday/${symbol}?interval=1h&outputsize=24`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.data || data.data.length === 0) {
        throw new Error('No intraday data available');
      }

      // Format data for Chart.js (reverse to show chronologically)
      const chartPoints = data.data.reverse();
      const labels = chartPoints.map(point => {
        const time = point.time || point.datetime.split(' ')[1] || '';
        return time.slice(0, 5); // Format as HH:MM
      });
      const prices = chartPoints.map(point => point.close);

      // Determine chart color based on overall trend
      const firstPrice = prices[0];
      const lastPrice = prices[prices.length - 1];
      const isPositive = lastPrice >= firstPrice;
      const chartColor = isPositive ? '#8BC34A' : '#E57373';

      setChartData({
        labels,
        datasets: [
          {
            label: `${symbol} Price`,
            data: prices,
            borderColor: chartColor,
            backgroundColor: `${chartColor}15`,
            borderWidth: 2,
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            pointHoverRadius: 4,
            pointBackgroundColor: chartColor,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 1,
          }
        ]
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: false
      },
      tooltip: {
        enabled: true,
        mode: 'nearest',
        intersect: false,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#2C3E50',
        bodyColor: '#2C3E50',
        borderColor: '#8BC34A',
        borderWidth: 1,
        titleFont: { size: 12 },
        bodyFont: { size: 11 },
        callbacks: {
          label: function(context) {
            return `$${context.parsed.y.toFixed(2)}`;
          },
          title: function(context) {
            return context[0].label;
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false
        },
        ticks: {
          display: true,
          maxTicksLimit: 6,
          color: '#7A8A9A',
          font: { size: 10 }
        }
      },
      y: {
        display: true,
        grid: {
          display: true,
          color: 'rgba(139, 195, 74, 0.1)'
        },
        ticks: {
          display: true,
          maxTicksLimit: 4,
          color: '#7A8A9A',
          font: { size: 10 },
          callback: function(value) {
            return '$' + value.toFixed(2);
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  };

  if (!isVisible) return null;

  return (
    <div 
      ref={containerRef}
      className="hover-chart-container"
      onMouseLeave={onMouseLeave}
    >
      <div className="hover-chart-header">
        <span className="hover-symbol">{symbol}</span>
        <span className="hover-period">Today (Hourly)</span>
      </div>
      
      <div className="hover-chart-content">
        {loading && (
          <div className="hover-chart-loading">
            <div className="mini-spinner"></div>
            <span>Loading...</span>
          </div>
        )}
        
        {error && (
          <div className="hover-chart-error">
            <span>📊 Chart unavailable</span>
          </div>
        )}
        
        {chartData && !loading && !error && (
          <div className="hover-chart-wrapper">
            <Line ref={chartRef} data={chartData} options={chartOptions} />
          </div>
        )}
      </div>
      
      <div className="hover-chart-footer">
        <span className="hover-hint">Click for detailed view</span>
      </div>
    </div>
  );
};

export default HoverChart;