const express = require('express');
const path = require('path');
const app = express();

const PORT = process.env.PORT || 3000;

// Serve static files from the React app build directory
app.use(express.static(path.join(__dirname, 'build')));

// API routes or other specific routes can be added here if needed
// app.use('/api', apiRouter);

// Handle React routing, return all requests to React app
// This must be the last route
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Portfolio Frontend Server running on port ${PORT}`);
}); 