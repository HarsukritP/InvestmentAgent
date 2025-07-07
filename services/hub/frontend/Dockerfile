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

# Remove package.json to prevent Railway from auto-detecting scripts
RUN cp package.json package.json.backup && echo '{"name":"procogia-ai-hub","version":"1.0.0","private":true}' > package.json

# Expose port
EXPOSE $PORT

# Use CMD with explicit node command - Railway should respect this
CMD ["node", "server.js"] 