import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './StockChart.css';

// For this implementation, we'll use Chart.js with react-chartjs-2
// Install with: npm install chart.js react-chartjs-2
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const StockChart = ({ symbol, period = "6months", height = 400, showControls = true }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState(period);

  const periods = [
    { value: "1week", label: "1W" },
    { value: "1month", label: "1M" },
    { value: "3months", label: "3M" },
    { value: "6months", label: "6M" },
    { value: "1year", label: "1Y" },
    { value: "2years", label: "2Y" },
    { value: "5years", label: "5Y" }
  ];

  const fetchChartData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`/chart/${symbol}?period=${selectedPeriod}`);
      const data = response.data;
      
      if (!data.data || data.data.length === 0) {
        throw new Error('No chart data available');
      }

      // Format data for Chart.js with even spacing
      const allData = data.data;
      
      // For longer periods, filter to get evenly spaced points
      let filteredData = allData;
      
      if (selectedPeriod === '1year' || selectedPeriod === '2years' || selectedPeriod === '5years') {
        // For long periods, show every 7th point (roughly weekly)
        filteredData = allData.filter((_, index) => index % 7 === 0);
      } else if (selectedPeriod === '6months') {
        // For 6 months, show every 3rd point
        filteredData = allData.filter((_, index) => index % 3 === 0);
      } else if (selectedPeriod === '3months') {
        // For 3 months, show every 2nd point
        filteredData = allData.filter((_, index) => index % 2 === 0);
      }
      
      // Always include the last point
      if (filteredData[filteredData.length - 1] !== allData[allData.length - 1]) {
        filteredData.push(allData[allData.length - 1]);
      }
      
      const labels = filteredData.map(point => {
        const date = new Date(point.date);
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          ...(selectedPeriod.includes('year') && { year: '2-digit' })
        });
      });
      const prices = filteredData.map(point => point.close || point.price);

      // Calculate price change colors
      const backgroundColors = prices.map((price, index) => {
        if (index === 0) return 'rgba(139, 195, 74, 0.8)'; // Green for first point
        return price >= prices[index - 1] 
          ? 'rgba(139, 195, 74, 0.8)'  // Green for gains
          : 'rgba(229, 115, 115, 0.8)'; // Red for losses
      });

      setChartData({
        labels,
        datasets: [
          {
            label: `${symbol} Price`,
            data: prices,
            borderColor: '#8BC34A',
            backgroundColor: 'rgba(139, 195, 74, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.1,
            pointBackgroundColor: backgroundColors,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
          }
        ]
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [symbol, selectedPeriod]);

  useEffect(() => {
    if (symbol) {
      fetchChartData();
    }
  }, [symbol, selectedPeriod, fetchChartData]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: `${symbol} - ${periods.find(p => p.value === selectedPeriod)?.label || selectedPeriod}`,
        font: {
          size: 16,
          weight: 'bold'
        },
        color: '#2C3E50'
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#2C3E50',
        bodyColor: '#2C3E50',
        borderColor: '#8BC34A',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            return `Price: $${context.parsed.y.toFixed(2)}`;
          },
          title: function(context) {
            const date = new Date(context[0].label);
            return date.toLocaleDateString('en-US', { 
              weekday: 'short', 
              year: 'numeric', 
              month: 'short', 
              day: 'numeric' 
            });
          }
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: selectedPeriod === '1week' ? 'day' : 
                selectedPeriod === '1month' ? 'week' : 'month'
        },
        grid: {
          display: false
        },
        ticks: {
          color: '#7A8A9A'
        }
      },
      y: {
        grid: {
          color: 'rgba(139, 195, 74, 0.1)'
        },
        ticks: {
          color: '#7A8A9A',
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
    },
    elements: {
      point: {
        hoverBackgroundColor: '#8BC34A'
      }
    }
  };

  if (loading) {
    return (
      <div className="stock-chart-container" style={{ height }}>
        <div className="chart-loading">
          <div className="spinner"></div>
          <p>Loading chart data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stock-chart-container" style={{ height }}>
        <div className="chart-error">
          <p>❌ {error}</p>
          <button 
            className="retry-button"
            onClick={fetchChartData}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="stock-chart-container" style={{ height }}>
      {showControls && (
        <div className="chart-controls">
          {periods.map(p => (
            <button
              key={p.value}
              className={`period-button ${selectedPeriod === p.value ? 'active' : ''}`}
              onClick={() => setSelectedPeriod(p.value)}
            >
              {p.label}
            </button>
          ))}
        </div>
      )}
      
      <div className="chart-wrapper">
        {chartData && (
          <Line data={chartData} options={chartOptions} />
        )}
      </div>
    </div>
  );
};

export default StockChart;