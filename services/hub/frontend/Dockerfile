# Use official Node.js runtime as base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the React app
RUN npm run build

# Now install only production dependencies (this removes devDependencies)
RUN npm ci --only=production

# Install our custom runtime dependencies if they were removed
RUN npm install express http-proxy-middleware

# Create a simple startup script inline to avoid file permission issues
RUN echo '#!/bin/sh\necho "🚀 Starting ProCogia AI Hub Frontend..."\necho "Environment PORT: $PORT"\nexec node server.js' > /app/start.sh && chmod +x /app/start.sh

# Remove any conflicting files that might trigger auto-detection
RUN rm -f package-lock.json || true

# Expose port
EXPOSE $PORT

# Use exec form to prevent shell interpretation and conflicts
ENTRYPOINT ["/app/start.sh"] 