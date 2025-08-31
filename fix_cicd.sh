#!/bin/bash

# CI/CD Fix Script for RetailGenie
# This script addresses common CI/CD pipeline issues

set -e

echo "🔧 RetailGenie CI/CD Fix Script"
echo "==============================="

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Navigate to backend
cd backend

echo "🐍 Checking Python environment..."
python --version

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "🧪 Checking test structure..."

# Create missing test directories if they don't exist
mkdir -p tests/unit tests/integration tests/performance tests/deployment tests/load

# Create __init__.py files for test directories
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/performance/__init__.py
touch tests/deployment/__init__.py
touch tests/load/__init__.py

echo "✅ Test directories structure verified"

# Check if critical test files exist
echo "🔍 Checking critical test files..."

critical_tests=(
    "tests/test_basic.py"
    "tests/test_app.py"
    "tests/test_integration.py"
    "tests/integration/test_simple_integration.py"
    "tests/deployment/test_simple_deployment.py"
    "tests/load/locustfile_simple.py"
)

missing_tests=()
for test_file in "${critical_tests[@]}"; do
    if [ ! -f "$test_file" ]; then
        missing_tests+=("$test_file")
    fi
done

if [ ${#missing_tests[@]} -gt 0 ]; then
    echo "⚠️  Missing test files:"
    for test in "${missing_tests[@]}"; do
        echo "   - $test"
    done
else
    echo "✅ All critical test files present"
fi

# Run pytest to check if tests can be collected
echo "🧪 Testing pytest collection..."
if python -m pytest --collect-only > /dev/null 2>&1; then
    echo "✅ Pytest can collect tests successfully"
else
    echo "⚠️  Pytest collection has issues. Running with verbose output:"
    python -m pytest --collect-only -v
fi

# Check pre-commit configuration
echo "🔧 Checking pre-commit configuration..."
if [ -f ".pre-commit-config.yaml" ]; then
    echo "✅ Pre-commit config found"
    
    # Install pre-commit if available
    if command -v pre-commit &> /dev/null; then
        echo "📝 Installing pre-commit hooks..."
        pre-commit install || echo "⚠️  Pre-commit installation failed (may need manual setup)"
    else
        echo "📦 Installing pre-commit..."
        pip install pre-commit
        pre-commit install || echo "⚠️  Pre-commit installation failed"
    fi
else
    echo "⚠️  No pre-commit config found"
fi

# Check GitHub Actions workflow
echo "🔄 Checking GitHub Actions workflow..."
if [ -f "../.github/workflows/ci.yml" ]; then
    echo "✅ GitHub Actions workflow found"
else
    echo "⚠️  No GitHub Actions workflow found"
fi

# Check Docker configuration
echo "🐳 Checking Docker configuration..."
docker_files=("deployment/Dockerfile" "deployment/docker-compose.yml")
for docker_file in "${docker_files[@]}"; do
    if [ -f "$docker_file" ]; then
        echo "✅ $docker_file found"
    else
        echo "⚠️  $docker_file not found"
    fi
done

# Check deployment configurations
echo "🚀 Checking deployment configurations..."
deploy_files=("render.yaml" "Procfile" "wsgi.py")
for deploy_file in "${deploy_files[@]}"; do
    if [ -f "$deploy_file" ]; then
        echo "✅ $deploy_file found"
    else
        echo "⚠️  $deploy_file not found"
    fi
done

# Run a basic test to verify everything works
echo "🧪 Running basic tests..."
if python -m pytest tests/test_basic.py -v; then
    echo "✅ Basic tests pass"
else
    echo "❌ Basic tests failed"
fi

echo ""
echo "🎉 CI/CD Fix Script Complete!"
echo "==============================="
echo ""
echo "📋 Summary:"
echo "   - Test structure verified ✅"
echo "   - Dependencies installed ✅"
echo "   - Configuration files checked ✅"
echo ""
echo "🚀 Next steps:"
echo "   1. Commit and push your changes"
echo "   2. Check GitHub Actions workflow"
echo "   3. Monitor CI/CD pipeline"
echo ""
echo "💡 For issues, check:"
echo "   - GitHub Actions logs"
echo "   - Test coverage reports"
echo "   - Deployment logs"
