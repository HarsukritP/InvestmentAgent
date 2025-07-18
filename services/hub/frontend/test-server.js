console.log('🧪 Starting minimal test server...');
console.log('📍 Current directory:', process.cwd());
console.log('📍 __dirname:', __dirname);
console.log('🌍 Environment variables:');
console.log('  PORT:', process.env.PORT || 'NOT_SET');
console.log('  NODE_ENV:', process.env.NODE_ENV || 'NOT_SET');
console.log('  PWD:', process.env.PWD || 'NOT_SET');

const express = require('express');
const app = express();
const PORT = process.env.PORT || 8080;

console.log('✅ Express loaded, creating test routes...');

app.get('/', (req, res) => {
  console.log('📥 Root route hit!');
  res.send(`
    <h1>🧪 Test Server Working!</h1>
    <p>✅ Express server is running properly</p>
    <p>🔗 <a href="/health">Health Check</a></p>
    <p>🔗 <a href="/test">JSON Test</a></p>
    <p>🔗 <a href="/static-test.html">Static File Test</a></p>
    <p>📅 ${new Date().toISOString()}</p>
  `);
});

app.get('/test', (req, res) => {
  console.log('📥 Test route hit!');
  res.json({ message: 'Test server working!', timestamp: new Date().toISOString() });
});

app.get('/health', (req, res) => {
  console.log('📥 Health route hit!');
  res.json({ status: 'OK', test: true });
});

// Serve static file
app.get('/static-test.html', (req, res) => {
  console.log('📥 Static file route hit!');
  res.sendFile(__dirname + '/static-test.html');
});

console.log('🔄 Starting test server...');

app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Test server running on port ${PORT}`);
  console.log(`🌍 Test endpoints: /test and /health`);
}).on('error', (err) => {
  console.error('❌ Test server failed:', err);
}); 