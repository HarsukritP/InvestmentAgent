const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Portfolio agent proxy configuration using environment variables
const portfolioProxy = createProxyMiddleware({
  target: process.env.PORTFOLIO_FRONTEND_URL || 'http://localhost:3000',
  changeOrigin: true,
  secure: process.env.NODE_ENV === 'production',
  pathRewrite: {
    '^/portfolio-agent': '', // Remove /portfolio-agent prefix when forwarding to the target
  },
      onError: (err, req, res) => {
      console.error('🚨 Portfolio proxy error:', err.message);
      console.error('Target URL:', process.env.PORTFOLIO_FRONTEND_URL || 'http://localhost:3000');
      console.error('Request URL:', req.url);
      console.error('Request method:', req.method);
      console.error('Error details:', err);
      
      // Send detailed error response
      res.status(502).json({ 
        error: 'Portfolio agent temporarily unavailable', 
        details: err.message,
        target: process.env.PORTFOLIO_FRONTEND_URL || 'http://localhost:3000',
        timestamp: new Date().toISOString()
      });
    },
      onProxyReq: (proxyReq, req, res) => {
      console.log(`✅ Proxying portfolio request: ${req.method} ${req.url} -> ${proxyReq.path}`);
      console.log(`🎯 Target: ${process.env.PORTFOLIO_FRONTEND_URL || 'http://localhost:3000'}`);
      
      // Add headers to help with proxy
      proxyReq.setHeader('X-Forwarded-Host', req.headers.host);
      proxyReq.setHeader('X-Forwarded-Proto', process.env.NODE_ENV === 'production' ? 'https' : 'http');
    },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`📥 Portfolio proxy response: ${proxyRes.statusCode} for ${req.url}`);
  },
  timeout: 30000, // 30 second timeout
  logLevel: 'debug'
});

// Manufacturing agent proxy configuration (placeholder)
const manufacturingProxy = createProxyMiddleware({
  target: process.env.MANUFACTURING_FRONTEND_URL || 'http://localhost:3001',
  changeOrigin: true,
  secure: process.env.NODE_ENV === 'production',
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
  target: process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'http://localhost:3002',
  changeOrigin: true,
  secure: process.env.NODE_ENV === 'production',
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
  target: process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'http://localhost:3003',
  changeOrigin: true,
  secure: process.env.NODE_ENV === 'production',
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
  target: process.env.HUB_BACKEND_URL || 'http://localhost:8001',
  changeOrigin: true,
  secure: process.env.NODE_ENV === 'production',
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
      portfolio: process.env.PORTFOLIO_FRONTEND_URL || 'NOT_CONFIGURED',
      manufacturing: process.env.MANUFACTURING_FRONTEND_URL || 'NOT_CONFIGURED',
      documentReview: process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'NOT_CONFIGURED',
      customerSupport: process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'NOT_CONFIGURED',
      hubApi: process.env.HUB_BACKEND_URL || 'NOT_CONFIGURED'
    },
    environment: {
      PORT: process.env.PORT,
      NODE_ENV: process.env.NODE_ENV
    }
  });
});

// Debug endpoint to test portfolio agent connection (simplified)
app.get('/debug/portfolio-test', (req, res) => {
  const targetUrl = process.env.PORTFOLIO_FRONTEND_URL || 'NOT_CONFIGURED';
  
  res.json({
    targetUrl,
    message: 'This endpoint shows what URL the proxy is trying to connect to',
    envVar: process.env.PORTFOLIO_FRONTEND_URL ? 'Custom URL set in Railway' : 'NOT CONFIGURED - Set PORTFOLIO_FRONTEND_URL in Railway',
    test: 'Visit /portfolio-agent to test the proxy',
    allEnvVars: {
      PORTFOLIO_FRONTEND_URL: process.env.PORTFOLIO_FRONTEND_URL || 'NOT_SET',
      MANUFACTURING_FRONTEND_URL: process.env.MANUFACTURING_FRONTEND_URL || 'NOT_SET',
      DOCUMENT_REVIEW_FRONTEND_URL: process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'NOT_SET',
      CUSTOMER_SUPPORT_FRONTEND_URL: process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'NOT_SET',
      HUB_BACKEND_URL: process.env.HUB_BACKEND_URL || 'NOT_SET',
      NODE_ENV: process.env.NODE_ENV || 'NOT_SET',
      PORT: process.env.PORT || 'NOT_SET'
    },
    timestamp: new Date().toISOString()
  });
});

// CRITICAL: Apply proxy middleware BEFORE any other middleware
app.use('/portfolio-agent', portfolioProxy);
app.use('/manufacturing-agent', manufacturingProxy);
app.use('/document-review-agent', documentReviewProxy);
app.use('/customer-support-agent', customerSupportProxy);
app.use('/api', apiProxy);

// Debug middleware AFTER proxies (only for non-proxy routes)
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Serve static files from the React app build directory AFTER proxies
app.use(express.static(path.join(__dirname, 'build')));

// Handle React routing - serve index.html for specific routes only
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// Catch-all for any other routes not handled by proxies - return 404
app.get('*', (req, res) => {
  res.status(404).json({ 
    error: 'Route not found', 
    availableRoutes: [
      '/',
      '/portfolio-agent',
      '/manufacturing-agent', 
      '/document-review-agent',
      '/customer-support-agent',
      '/api/*',
      '/health',
      '/debug/portfolio-test'
    ],
    requestedRoute: req.url,
    timestamp: new Date().toISOString()
  });
});

// Check if build directory exists before starting server
const fs = require('fs');
const buildPath = path.join(__dirname, 'build');

console.log('🔍 Checking build directory...');
if (fs.existsSync(buildPath)) {
  console.log('✅ Build directory found:', buildPath);
  const buildFiles = fs.readdirSync(buildPath);
  console.log('📁 Build files:', buildFiles);
} else {
  console.log('❌ Build directory NOT found:', buildPath);
  console.log('📂 Current directory contents:', fs.readdirSync(__dirname));
}

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Hub router server running on port ${PORT}`);
  console.log(`📡 Portfolio agent proxied at /portfolio-agent/* -> ${process.env.PORTFOLIO_FRONTEND_URL || 'NOT_CONFIGURED'}`);
  console.log(`📡 Manufacturing agent proxied at /manufacturing-agent/* -> ${process.env.MANUFACTURING_FRONTEND_URL || 'NOT_CONFIGURED'}`);
  console.log(`📡 Document review agent proxied at /document-review-agent/* -> ${process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'NOT_CONFIGURED'}`);
  console.log(`📡 Customer support agent proxied at /customer-support-agent/* -> ${process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'NOT_CONFIGURED'}`);
  console.log(`📡 Hub API proxied at /api/* -> ${process.env.HUB_BACKEND_URL || 'NOT_CONFIGURED'}`);
  console.log(`🌍 Environment NODE_ENV: ${process.env.NODE_ENV || 'NOT_SET'}`);
  console.log(`🌍 Environment PORT: ${process.env.PORT || 'NOT_SET'}`);
  console.log(`🌍 Server listening on all interfaces (0.0.0.0:${PORT})`);
  console.log(`❤️  Health check available at /health`);
  console.log(`🔧 Proxy debug available at /debug/portfolio-test`);
  
  // Test health endpoint immediately after startup
  setTimeout(() => {
    console.log('🩺 Testing health endpoint...');
    const http = require('http');
    const req = http.request({
      hostname: 'localhost',
      port: PORT,
      path: '/health',
      method: 'GET'
    }, (res) => {
      console.log(`✅ Health endpoint responding with status: ${res.statusCode}`);
    });
    req.on('error', (err) => {
      console.log(`❌ Health endpoint test failed:`, err.message);
    });
    req.end();
  }, 1000);
}); 