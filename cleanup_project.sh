#!/bin/bash

# RetailGenie Final Cleanup and Organization Script
# This script organizes the project for final production state

echo "🧹 Starting RetailGenie Project Cleanup..."

cd /workspaces/RetailGenie

# Create organized directory structure
echo "📁 Organizing directory structure..."

# Move documentation files to docs directory
mkdir -p docs
mv backend/ADVANCED_FEATURES.md docs/ 2>/dev/null || true
mv backend/PERFORMANCE_OPTIMIZATION_SUMMARY.md docs/ 2>/dev/null || true
mv backend/DEPLOYMENT.md docs/ 2>/dev/null || true
mv backend/TESTING_GUIDE.md docs/ 2>/dev/null || true
mv backend/DEVELOPMENT_WORKFLOW.md docs/ 2>/dev/null || true

# Create scripts directory for utility scripts
mkdir -p scripts
mv backend/deploy_production.sh scripts/ 2>/dev/null || true
mv backend/start_advanced.sh scripts/ 2>/dev/null || true
mv backend/start_optimized.sh scripts/ 2>/dev/null || true
mv backend/consolidate_files.sh scripts/ 2>/dev/null || true

# Clean up duplicate/backup files
echo "🗑️ Removing duplicate and backup files..."
cd backend
rm -f app_backup.py database_app.py working_app.py minimal_app.py 2>/dev/null || true
rm -f config_optimized.py requirements_unified.txt 2>/dev/null || true
rm -f README_backup.md 2>/dev/null || true

# Clean up test files that are duplicated
rm -f test_api.py test_firebase.py 2>/dev/null || true

# Remove empty or unused files
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Organize startup scripts
echo "📝 Organizing startup scripts..."
mkdir -p scripts
mv start.sh scripts/ 2>/dev/null || true
mv simple_start.sh scripts/ 2>/dev/null || true
mv start_production.sh scripts/ 2>/dev/null || true
mv start_unified.sh scripts/ 2>/dev/null || true
mv deploy.sh scripts/ 2>/dev/null || true

# Make scripts executable
chmod +x scripts/*.sh 2>/dev/null || true

echo "✅ Cleanup completed!"

# Show final structure
echo "📊 Final project structure:"
ls -la | head -20

echo ""
echo "🚀 RetailGenie is now organized and ready for production!"
echo ""
echo "Quick start options:"
echo "  - Basic API: python backend/app.py"
echo "  - Main: python backend/app.py"
echo "  - Advanced:  ./scripts/start_advanced.sh"
echo "  - Deploy:    ./scripts/deploy_production.sh"
