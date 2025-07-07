const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Portfolio agent proxy configuration
const portfolioProxy = createProxyMiddleware({
  target: `https://${process.env.PORTFOLIO_FRONTEND_URL || 'procogia-investment-aiagent.up.railway.app'}`,
  changeOrigin: true,
  pathRewrite: {
    '^/portfolio': '', // Remove /portfolio prefix when forwarding to the target
  },
  onError: (err, req, res) => {
    console.error('Portfolio proxy error:', err);
    res.status(502).json({ error: 'Portfolio agent temporarily unavailable' });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying request: ${req.method} ${req.url} -> ${proxyReq.path}`);
  }
});

// API proxy for hub backend
const apiProxy = createProxyMiddleware({
  target: `https://${process.env.HUB_BACKEND_URL || 'agenthub-backend.up.railway.app'}`,
  changeOrigin: true,
  onError: (err, req, res) => {
    console.error('API proxy error:', err);
    res.status(502).json({ error: 'API temporarily unavailable' });
  }
});

// Health check endpoint for Railway
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Apply proxy middleware
app.use('/portfolio', portfolioProxy);
app.use('/api', apiProxy);

// Serve static files from the React app build directory
app.use(express.static(path.join(__dirname, 'build')));

// Handle React routing - serve index.html for all non-API routes
app.get('*', (req, res) => {
  // Don't interfere with portfolio proxy or API routes
  if (req.path.startsWith('/portfolio') || req.path.startsWith('/api')) {
    return;
  }
  
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Hub frontend server running on port ${PORT}`);
  console.log(`Portfolio agent proxied at /portfolio/*`);
  console.log(`Hub API proxied at /api/*`);
  console.log(`Environment PORT: ${process.env.PORT}`);
  console.log(`Server listening on all interfaces (0.0.0.0:${PORT})`);
  console.log(`Health check available at /health`);
}); 