# Use official Node.js runtime as base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production dependencies are already installed via npm ci

# Remove devDependencies to reduce image size
RUN npm prune --production

# Expose port
EXPOSE $PORT

# Start the application
CMD ["npm", "run", "serve"] 