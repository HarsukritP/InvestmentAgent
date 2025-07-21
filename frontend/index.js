const express = require('express');
const path = require('path');
const cors = require('cors');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

// Determine build directory path
const buildPath = path.join(__dirname, 'build');

// Log environment information
console.log('Current directory:', __dirname);
console.log('Looking for build directory at:', buildPath);
console.log('Build directory exists:', fs.existsSync(buildPath));

if (fs.existsSync(buildPath)) {
  // List files in build directory for debugging
  console.log('Files in build directory:', fs.readdirSync(buildPath));
} else {
  console.log('Checking parent directory for build folder...');
  const parentBuildPath = path.join(__dirname, '..', 'build');
  console.log('Parent build path:', parentBuildPath);
  console.log('Parent build directory exists:', fs.existsSync(parentBuildPath));
  
  if (fs.existsSync(parentBuildPath)) {
    console.log('Using parent build directory');
    // List files in parent build directory for debugging
    console.log('Files in parent build directory:', fs.readdirSync(parentBuildPath));
  }
}

// Serve static files from the React build
app.use(express.static(buildPath));

// Add headers to all responses
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  next();
});

// Debug route
app.get('/debug', (req, res) => {
  res.json({
    environment: process.env.NODE_ENV,
    port: PORT,
    buildPath,
    buildExists: fs.existsSync(buildPath),
    currentDir: __dirname,
    files: fs.existsSync(buildPath) ? fs.readdirSync(buildPath) : []
  });
});

// Handle React routing, return all requests to React app
app.get('*', (req, res) => {
  // Check if index.html exists in the build directory
  const indexPath = path.join(buildPath, 'index.html');
  
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(404).send('Build files not found. Make sure the build process completed successfully.');
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Serving static files from: ${buildPath}`);
}); 