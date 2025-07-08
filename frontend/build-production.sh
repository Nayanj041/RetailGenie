#!/bin/bash

# Frontend build script for production deployment
echo "Starting frontend build for production deployment..."

# Ensure we're in the frontend directory
cd /workspaces/RetailGenie/frontend

# Clear npm cache
echo "Clearing npm cache..."
npm cache clean --force

# Remove node_modules and reinstall (ensures clean state)
echo "Cleaning node_modules..."
rm -rf node_modules
rm -f package-lock.json

# Install dependencies with legacy peer deps
echo "Installing dependencies..."
npm install --legacy-peer-deps

# Add required dependencies if missing
echo "Ensuring cross-spawn is installed..."
npm install cross-spawn --save --legacy-peer-deps

# Run the build
echo "Building the application..."
CI=false npm run build

echo "Frontend build completed successfully!"
echo "Build artifacts are in: /workspaces/RetailGenie/frontend/build"
