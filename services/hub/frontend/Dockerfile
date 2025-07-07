FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json first for better caching
COPY package*.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Install serve globally for production serving
RUN npm install -g serve

# Clean up node_modules to reduce image size (keep only production dependencies)
RUN rm -rf node_modules && npm ci --only=production

# Create a non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose the port
EXPOSE 3000

# Start the application with PORT environment variable support
CMD ["sh", "-c", "serve -s build -l ${PORT:-3000}"] 