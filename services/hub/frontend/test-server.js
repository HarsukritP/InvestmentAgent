console.log('🧪 Starting minimal test server...');

const express = require('express');
const app = express();
const PORT = process.env.PORT || 8080;

console.log('✅ Express loaded, creating test route...');

app.get('/test', (req, res) => {
  console.log('📥 Test route hit!');
  res.json({ message: 'Test server working!', timestamp: new Date().toISOString() });
});

app.get('/health', (req, res) => {
  console.log('📥 Health route hit!');
  res.json({ status: 'OK', test: true });
});

console.log('🔄 Starting test server...');

app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Test server running on port ${PORT}`);
  console.log(`🌍 Test endpoints: /test and /health`);
}).on('error', (err) => {
  console.error('❌ Test server failed:', err);
}); 