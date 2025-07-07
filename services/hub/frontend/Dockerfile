# Use official Node.js runtime as base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy and restore package files
COPY package*.json.bak ./
RUN mv package.json.bak package.json && mv package-lock.json.bak package-lock.json

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Install serve globally for production
RUN npm install -g serve

# Remove devDependencies to reduce image size
RUN npm prune --production

# Expose port
EXPOSE $PORT

# Start the application
CMD ["sh", "-c", "serve -s build -p $PORT"] 