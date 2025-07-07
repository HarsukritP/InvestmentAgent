#!/bin/sh

# ProCogia AI Hub Frontend Startup Script
echo "🚀 Starting ProCogia AI Hub Frontend..."
echo "Environment PORT: $PORT"
echo "Working directory: $(pwd)"
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# Start our custom server
echo "Starting custom Express proxy server..."
exec node server.js 