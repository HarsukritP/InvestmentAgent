const express = require('express');
const path = require('path');
const cors = require('cors');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

// Determine build directory path - try multiple possible locations
let buildPath = path.join(__dirname, 'build');

// Check if build directory exists, if not try alternative locations
if (!fs.existsSync(buildPath)) {
  console.log(`Build directory not found at ${buildPath}, trying alternatives...`);
  
  const alternatives = [
    path.join(__dirname, '..', 'build'),
    path.join(__dirname, '..', '..', 'build'),
    path.join(process.cwd(), 'build'),
    '/app/build'
  ];
  
  for (const altPath of alternatives) {
    console.log(`Checking ${altPath}...`);
    if (fs.existsSync(altPath)) {
      buildPath = altPath;
      console.log(`Found build directory at ${buildPath}`);
      break;
    }
  }
}

// Log environment information
console.log('Current directory:', __dirname);
console.log('Process current working directory:', process.cwd());
console.log('Using build directory at:', buildPath);
console.log('Build directory exists:', fs.existsSync(buildPath));

if (fs.existsSync(buildPath)) {
  // List files in build directory for debugging
  console.log('Files in build directory:', fs.readdirSync(buildPath));
}

// Serve static files from the React build
if (fs.existsSync(buildPath)) {
  app.use(express.static(buildPath));
  console.log(`Serving static files from: ${buildPath}`);
} else {
  console.error('ERROR: Build directory not found! Static files will not be served.');
}

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
    processDir: process.cwd(),
    files: fs.existsSync(buildPath) ? fs.readdirSync(buildPath) : [],
    env: process.env
  });
});

// Handle React routing, return all requests to React app
app.get('*', (req, res) => {
  // Check if index.html exists in the build directory
  const indexPath = path.join(buildPath, 'index.html');
  
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(404).send(`
      <html>
        <head><title>Build Not Found</title></head>
        <body>
          <h1>Build files not found</h1>
          <p>Make sure the build process completed successfully.</p>
          <h2>Debug Information:</h2>
          <pre>
            Current directory: ${__dirname}
            Process working directory: ${process.cwd()}
            Build path: ${buildPath}
            Index path: ${indexPath}
            Index exists: ${fs.existsSync(indexPath)}
          </pre>
        </body>
      </html>
    `);
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 