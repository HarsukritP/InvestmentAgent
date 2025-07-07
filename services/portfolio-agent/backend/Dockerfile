FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy setup script and make it executable
COPY setup.sh .
RUN chmod +x setup.sh

# Copy the rest of the application
COPY . .

# Run setup script
RUN ./setup.sh

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose the port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get(f'http://localhost:{$PORT}/health')" || exit 1

# Start the application
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port $PORT"] 