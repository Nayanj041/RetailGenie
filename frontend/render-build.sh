#!/bin/bash

# Render.com build script for RetailGenie Frontend
echo "Starting Render.com build for RetailGenie Frontend..."

# Set environment variables for build
export CI=false
export GENERATE_SOURCEMAP=false
export NODE_OPTIONS="--max-old-space-size=4096"

# Install dependencies
echo "Installing dependencies with legacy peer deps..."
npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Ensure critical build dependencies are available
echo "Ensuring critical build dependencies..."
npm install cross-spawn --save
npm install react-scripts --save

# Build the application
echo "Building React application..."
npm run build

echo "Build completed successfully!"
echo "Checking build output..."
ls -la build/

echo "Build artifacts ready for deployment"
