const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Portfolio agent proxy configuration using Railway private networking
const portfolioProxy = createProxyMiddleware({
  target: process.env.PORTFOLIO_FRONTEND_URL || 'http://portfolio-frontend.railway.internal:8080',
  changeOrigin: true,
  pathRewrite: {
    '^/portfolio-agent': '', // Remove /portfolio-agent prefix when forwarding to the target
  },
  onError: (err, req, res) => {
    console.error('Portfolio proxy error:', err);
    console.error('Target URL:', process.env.PORTFOLIO_FRONTEND_URL || 'http://portfolio-frontend.railway.internal:8080');
    res.status(502).json({ error: 'Portfolio agent temporarily unavailable' });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying portfolio request: ${req.method} ${req.url} -> ${proxyReq.path}`);
    console.log(`Target: ${process.env.PORTFOLIO_FRONTEND_URL || 'http://portfolio-frontend.railway.internal:8080'}`);
  },
  logLevel: 'debug'
});

// Manufacturing agent proxy configuration (placeholder)
const manufacturingProxy = createProxyMiddleware({
  target: process.env.MANUFACTURING_FRONTEND_URL || 'http://manufacturing-frontend.railway.internal:8080',
  changeOrigin: true,
  pathRewrite: {
    '^/manufacturing-agent': '',
  },
  onError: (err, req, res) => {
    console.error('Manufacturing proxy error:', err);
    res.status(502).json({ error: 'Manufacturing agent temporarily unavailable' });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying manufacturing request: ${req.method} ${req.url} -> ${proxyReq.path}`);
  }
});

// Document review agent proxy configuration (placeholder)
const documentReviewProxy = createProxyMiddleware({
  target: process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'http://document-review-frontend.railway.internal:8080',
  changeOrigin: true,
  pathRewrite: {
    '^/document-review-agent': '',
  },
  onError: (err, req, res) => {
    console.error('Document review proxy error:', err);
    res.status(502).json({ error: 'Document review agent temporarily unavailable' });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying document review request: ${req.method} ${req.url} -> ${proxyReq.path}`);
  }
});

// Customer support agent proxy configuration (placeholder)
const customerSupportProxy = createProxyMiddleware({
  target: process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'http://customer-support-frontend.railway.internal:8080',
  changeOrigin: true,
  pathRewrite: {
    '^/customer-support-agent': '',
  },
  onError: (err, req, res) => {
    console.error('Customer support proxy error:', err);
    res.status(502).json({ error: 'Customer support agent temporarily unavailable' });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying customer support request: ${req.method} ${req.url} -> ${proxyReq.path}`);
  }
});

// API proxy for hub backend
const apiProxy = createProxyMiddleware({
  target: process.env.HUB_BACKEND_URL || 'http://hub-backend.railway.internal:8080',
  changeOrigin: true,
  onError: (err, req, res) => {
    console.error('API proxy error:', err);
    res.status(502).json({ error: 'API temporarily unavailable' });
  }
});

// Health check endpoint for Railway
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    proxies: {
      portfolio: process.env.PORTFOLIO_FRONTEND_URL || 'http://portfolio-frontend.railway.internal:8080',
      manufacturing: process.env.MANUFACTURING_FRONTEND_URL || 'http://manufacturing-frontend.railway.internal:8080',
      documentReview: process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'http://document-review-frontend.railway.internal:8080',
      customerSupport: process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'http://customer-support-frontend.railway.internal:8080',
      hubApi: process.env.HUB_BACKEND_URL || 'http://hub-backend.railway.internal:8080'
    }
  });
});

// Debug endpoint to test portfolio agent connection (simplified)
app.get('/debug/portfolio-test', (req, res) => {
  const targetUrl = process.env.PORTFOLIO_FRONTEND_URL || 'http://portfolio-frontend.railway.internal:8080';
  
  res.json({
    targetUrl,
    message: 'This endpoint shows what URL the proxy is trying to connect to',
    envVar: process.env.PORTFOLIO_FRONTEND_URL ? 'Custom URL set' : 'Using default Railway internal URL'
  });
});

// IMPORTANT: Apply proxy middleware BEFORE static file serving
app.use('/portfolio-agent', portfolioProxy);
app.use('/manufacturing-agent', manufacturingProxy);
app.use('/document-review-agent', documentReviewProxy);
app.use('/customer-support-agent', customerSupportProxy);
app.use('/api', apiProxy);

// Serve static files from the React app build directory AFTER proxies
app.use(express.static(path.join(__dirname, 'build')));

// Handle React routing - serve index.html for all non-API and non-agent routes
app.get('*', (req, res) => {
  // Don't interfere with agent proxy or API routes
  if (req.path.startsWith('/portfolio-agent') || 
      req.path.startsWith('/manufacturing-agent') || 
      req.path.startsWith('/document-review-agent') || 
      req.path.startsWith('/customer-support-agent') || 
      req.path.startsWith('/api')) {
    return;
  }
  
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Hub router server running on port ${PORT}`);
  console.log(`Portfolio agent proxied at /portfolio-agent/* -> ${process.env.PORTFOLIO_FRONTEND_URL || 'http://portfolio-frontend.railway.internal:8080'}`);
  console.log(`Manufacturing agent proxied at /manufacturing-agent/*`);
  console.log(`Document review agent proxied at /document-review-agent/*`);
  console.log(`Customer support agent proxied at /customer-support-agent/*`);
  console.log(`Hub API proxied at /api/*`);
  console.log(`Environment PORT: ${process.env.PORT}`);
  console.log(`Server listening on all interfaces (0.0.0.0:${PORT})`);
  console.log(`Health check available at /health`);
}); 