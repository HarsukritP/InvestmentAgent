console.log('🚀 Starting hub frontend server...');
console.log('📍 Current working directory:', process.cwd());
console.log('📍 Server file location:', __dirname);

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

console.log('✅ Required modules loaded successfully');

const app = express();
const PORT = process.env.PORT || 8080;

console.log('🎯 Server will run on port:', PORT);

// Portfolio agent proxy configuration - using environment variable for external URL
const portfolioProxy = createProxyMiddleware({
  target: process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-portfolioagent.up.railway.app',
  changeOrigin: true,
  secure: true, // External HTTPS URL
  pathRewrite: {
    '^/portfolio-agent': '', // Remove /portfolio-agent prefix when forwarding to the target
  },
      onError: (err, req, res) => {
      console.error('🚨 Portfolio proxy error:', err.message);
      console.error('Target URL:', process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-portfolioagent.up.railway.app');
      console.error('Request URL:', req.url);
      console.error('Request method:', req.method);
      console.error('Error details:', err);
      
      // Send detailed error response
      res.status(502).json({ 
        error: 'Portfolio agent temporarily unavailable', 
        details: err.message,
        target: process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-portfolioagent.up.railway.app',
        timestamp: new Date().toISOString()
      });
    },
      onProxyReq: (proxyReq, req, res) => {
      console.log(`✅ Proxying portfolio request: ${req.method} ${req.url} -> ${proxyReq.path}`);
      console.log(`🎯 Target: ${process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-portfolioagent.up.railway.app'}`);
      
      // Add headers to help with proxy
      proxyReq.setHeader('X-Forwarded-Host', req.headers.host);
      proxyReq.setHeader('X-Forwarded-Proto', 'http'); // Internal Railway networking uses HTTP
    },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`📥 Portfolio proxy response: ${proxyRes.statusCode} for ${req.url}`);
  },
  timeout: 30000, // 30 second timeout
  logLevel: 'debug'
});

// Manufacturing agent proxy configuration (placeholder)
const manufacturingProxy = createProxyMiddleware({
  target: process.env.MANUFACTURING_FRONTEND_URL || 'http://manufacturing-frontend.railway.internal',
  changeOrigin: true,
  secure: false,
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
  target: process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'http://document-review-frontend.railway.internal',
  changeOrigin: true,
  secure: false,
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
  target: process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'http://customer-support-frontend.railway.internal',
  changeOrigin: true,
  secure: false,
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
  target: process.env.HUB_BACKEND_URL || 'http://hub-backend.railway.internal',
  changeOrigin: true,
  secure: false,
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
      portfolio: process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-investment-aiagent.up.railway.app',
      manufacturing: process.env.MANUFACTURING_FRONTEND_URL || 'http://manufacturing-frontend.railway.internal',
      documentReview: process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'http://document-review-frontend.railway.internal',
      customerSupport: process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'http://customer-support-frontend.railway.internal',
      hubApi: process.env.HUB_BACKEND_URL || 'http://hub-backend.railway.internal'
    },
    environment: {
      PORT: process.env.PORT,
      NODE_ENV: process.env.NODE_ENV
    }
  });
});

// Debug endpoint to test portfolio agent connection (simplified)
app.get('/debug/portfolio-test', (req, res) => {
  const targetUrl = process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-investment-aiagent.up.railway.app';
  
  res.json({
    targetUrl,
    message: 'This endpoint shows what URL the proxy is trying to connect to',
    envVar: process.env.PORTFOLIO_FRONTEND_URL ? 'Custom URL set in Railway' : 'Using default internal Railway URL',
    test: 'Visit /portfolio-agent to test the proxy',
    serviceName: 'Using your configured Railway variable names',
    currentUrls: {
      portfolioFrontend: 'http://portfolio-frontend.railway.internal',
      portfolioBackend: 'http://portfolio-backend.railway.internal',
      hubFrontend: 'http://hub-frontend.railway.internal',
      hubBackend: 'http://hub-backend.railway.internal'
    },
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

// Portfolio backend API proxy - for OAuth and other API requests
const portfolioApiProxy = createProxyMiddleware({
  target: process.env.PORTFOLIO_BACKEND_URL || 'https://procogia-portfolioagent-service.up.railway.app',
  changeOrigin: true,
  secure: true,
  pathRewrite: {
    '^/portfolio-agent/api': '/', // Rewrite /portfolio-agent/api to / (root path)
  },
  onError: (err, req, res) => {
    console.error('🚨 Portfolio API proxy error:', err.message);
    console.error('Target URL:', process.env.PORTFOLIO_BACKEND_URL || 'https://procogia-portfolioagent-service.up.railway.app');
    console.error('Request URL:', req.url);
    console.error('Error details:', err);
    res.status(502).json({ error: 'Portfolio API temporarily unavailable' });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`🔌 Proxying portfolio API: ${req.method} ${req.url} -> ${proxyReq.path}`);
    console.log(`🎯 API Target: ${process.env.PORTFOLIO_BACKEND_URL || 'https://procogia-portfolioagent-service.up.railway.app'}`);
    
    // Add headers to help with proxy
    proxyReq.setHeader('X-Forwarded-Host', req.headers.host);
    proxyReq.setHeader('X-Forwarded-Proto', 'https');
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`📡 Portfolio API response: ${proxyRes.statusCode} for ${req.url}`);
    
    // Add CORS headers for OAuth
    proxyRes.headers['Access-Control-Allow-Origin'] = '*';
    proxyRes.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS';
    proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization';
    proxyRes.headers['Access-Control-Allow-Credentials'] = 'true';
  }
});

// Apply portfolio API proxy for /portfolio-agent/api routes
app.use('/portfolio-agent/api', portfolioApiProxy);

// Handle React routing - serve index.html ONLY for the root route
// IMPORTANT: This must come BEFORE the static proxy to ensure root route is handled correctly
app.get('/', (req, res) => {
  console.log('🏠 Serving root route - will redirect to ProCogia services');
  // Add cache-busting headers for index.html
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// PORTFOLIO STATIC ASSETS PROXY - Handle static file requests when viewing portfolio agent
// This forwards static asset requests to the portfolio frontend
const portfolioStaticProxy = createProxyMiddleware({
  target: process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-portfolioagent.up.railway.app',
  changeOrigin: true,
  secure: true,
  // Only proxy static requests that would come from the portfolio frontend
  pathFilter: (pathname, req) => {
    // IMPORTANT: Only match static assets, never match the root path
    if (pathname === '/' || pathname === '') {
      console.log('🛑 Preventing static proxy from handling root path');
      return false;
    }
    
    // Check if the request is for static assets
    const isStaticAsset = pathname.startsWith('/static/') || 
                          pathname.includes('.js') || 
                          pathname.includes('.css') || 
                          pathname.includes('.ico') ||
                          pathname.includes('.png') ||
                          pathname.includes('.jpg') ||
                          pathname.includes('.svg');
    
    console.log(`🔍 Static asset check: ${pathname}, is static: ${isStaticAsset}`);
    return isStaticAsset;
  },
  onError: (err, req, res) => {
    console.error('🚨 Portfolio static proxy error:', err.message);
    res.status(502).json({ error: 'Portfolio static assets temporarily unavailable' });
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`📁 Proxying portfolio static: ${req.method} ${req.url} -> ${proxyReq.path}`);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`📁 Portfolio static response: ${proxyRes.statusCode} for ${req.url}`);
    
    // Add cache control headers to prevent caching issues
    proxyRes.headers['cache-control'] = 'no-cache, no-store, must-revalidate';
    proxyRes.headers['pragma'] = 'no-cache';
    proxyRes.headers['expires'] = '0';
  }
});

app.use(portfolioStaticProxy);

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
// Add cache-busting headers to prevent stale file issues
app.use(express.static(path.join(__dirname, 'build'), {
  setHeaders: (res, filePath) => {
    // Cache static assets for 1 hour, but index.html for 0 seconds
    if (filePath.endsWith('index.html')) {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
    } else {
      res.setHeader('Cache-Control', 'public, max-age=3600'); // 1 hour for assets
    }
  }
}));

// Catch-all for any other routes not handled by proxies - return 404
// This prevents React Router from interfering with proxy routes
app.get('*', (req, res) => {
  console.log(`❌ Route not found: ${req.url}`);
  res.status(404).json({ 
    error: 'Route not found', 
    message: 'This route is not available through the ProCogia AI Hub',
    availableRoutes: [
      '/ - ProCogia Hub (redirects to procogia.com/services)',
      '/portfolio-agent - Portfolio Management Agent',
      '/manufacturing-agent - Manufacturing Agent (coming soon)', 
      '/document-review-agent - Document Review Agent (coming soon)',
      '/customer-support-agent - Customer Support Agent (coming soon)',
      '/api/* - Hub API endpoints',
      '/health - Health check',
      '/debug/portfolio-test - Debug endpoint'
    ],
    requestedRoute: req.url,
    suggestion: req.url.startsWith('/portfolio') ? 'Did you mean /portfolio-agent?' : 'Check the available routes above',
    timestamp: new Date().toISOString()
  });
});

// Check if build directory exists before starting server
const fs = require('fs');
const buildPath = path.join(__dirname, 'build');

console.log('🔍 Checking build directory...');
try {
  if (fs.existsSync(buildPath)) {
    console.log('✅ Build directory found:', buildPath);
    const buildFiles = fs.readdirSync(buildPath);
    console.log('📁 Build files:', buildFiles.slice(0, 5)); // Show first 5 files only
  } else {
    console.log('❌ Build directory NOT found:', buildPath);
    console.log('📂 Current directory contents:', fs.readdirSync(__dirname));
  }
} catch (error) {
  console.error('❌ Error checking build directory:', error.message);
}

// Add error handling for server startup
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

console.log('🔄 Attempting to start server...');

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 SUCCESS! Hub router server running on port ${PORT}`);
  console.log(`📡 Portfolio agent proxied at /portfolio-agent/* -> ${process.env.PORTFOLIO_FRONTEND_URL || 'https://procogia-investment-aiagent.up.railway.app'}`);
  console.log(`📡 Manufacturing agent proxied at /manufacturing-agent/* -> ${process.env.MANUFACTURING_FRONTEND_URL || 'http://manufacturing-frontend.railway.internal'}`);
  console.log(`📡 Document review agent proxied at /document-review-agent/* -> ${process.env.DOCUMENT_REVIEW_FRONTEND_URL || 'http://document-review-frontend.railway.internal'}`);
  console.log(`📡 Customer support agent proxied at /customer-support-agent/* -> ${process.env.CUSTOMER_SUPPORT_FRONTEND_URL || 'http://customer-support-frontend.railway.internal'}`);
  console.log(`📡 Hub API proxied at /api/* -> ${process.env.HUB_BACKEND_URL || 'http://hub-backend.railway.internal'}`);
  console.log(`🌍 Environment NODE_ENV: ${process.env.NODE_ENV || 'NOT_SET'}`);
  console.log(`🌍 Environment PORT: ${process.env.PORT || 'NOT_SET'}`);
  console.log(`🌍 Server listening on all interfaces (0.0.0.0:${PORT})`);
  console.log(`❤️  Health check available at /health`);
  console.log(`🔧 Proxy debug available at /debug/portfolio-test`);
  console.log(`✅ SERVER STARTUP COMPLETE!`);
});

server.on('error', (error) => {
  console.error('❌ Server failed to start:', error);
  if (error.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use`);
  }
  process.exit(1);
}); 