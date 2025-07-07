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

# Build the React app
RUN npm run build

# Remove devDependencies to reduce image size
RUN npm prune --production

# Make start script executable
RUN chmod +x start.sh

# Expose port
EXPOSE $PORT

# Start the application using our custom script
CMD ["./start.sh"] 