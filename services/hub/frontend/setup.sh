#!/bin/bash

# Print current environment
echo "Current environment:"
env
echo "Current directory:"
pwd
ls -la

# Try to use Nixpacks-provided Node.js
if command -v node &> /dev/null && command -v npm &> /dev/null; then
  echo "Node.js and npm already installed:"
  node -v
  npm -v
else
  # Install Node.js and npm using NVM as fallback
  echo "Installing Node.js and npm using NVM..."
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm install 18
  nvm use 18
  
  # Verify installation
  node -v
  npm -v
fi

echo "Node.js and npm installation complete." 