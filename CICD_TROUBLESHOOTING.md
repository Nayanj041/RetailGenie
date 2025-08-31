# CI/CD Troubleshooting Guide for RetailGenie

## 🚨 Common CI/CD Issues and Solutions

### Issue 1: Test Collection Failures

**Problem**: Pytest cannot collect tests or tests fail to import.

**Symptoms**:
- `ImportError` during test collection
- `ModuleNotFoundError` for application modules
- Tests pass locally but fail in CI

**Solutions**:
```bash
# Fix import paths
export PYTHONPATH="${PYTHONPATH}:/workspaces/RetailGenie/backend"

# Install all dependencies
pip install -r requirements.txt

# Check test structure
python -m pytest --collect-only -v
```

### Issue 2: Missing Test Files

**Problem**: CI pipeline references test files that don't exist.

**Files to Check**:
- `tests/test_basic.py` ✅ (Created)
- `tests/test_app.py` ✅ (Exists)
- `tests/test_integration.py` ✅ (Exists)
- `tests/integration/test_simple_integration.py` ✅ (Created)
- `tests/deployment/test_simple_deployment.py` ✅ (Created)
- `tests/load/locustfile_simple.py` ✅ (Created)

### Issue 3: Pre-commit Hook Failures

**Problem**: Pre-commit hooks fail in CI but pass locally.

**Solutions**:
```bash
# Install and run pre-commit locally
pip install pre-commit
pre-commit install
pre-commit run --all-files

# Fix common issues
black . --line-length=88
isort . --profile=black
flake8 --max-line-length=88
```

### Issue 4: Docker Build Failures

**Problem**: Docker build fails due to dependency issues.

**Solutions**:
1. **Python Version Mismatch** ✅ Fixed: Updated Dockerfile to use Python 3.12
2. **Missing Requirements File** ✅ Fixed: Changed from requirements-render.txt to requirements.txt
3. **Build Context Issues**: Ensure Dockerfile is in the correct location

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### Issue 5: Environment Variables Missing

**Problem**: Application fails because environment variables are not set.

**Required Environment Variables**:
```bash
# Development
export FLASK_ENV=development
export FLASK_DEBUG=true
export TESTING=true

# Production
export FLASK_ENV=production
export FLASK_DEBUG=false
export SECRET_KEY=your-secret-key

# Optional (for full functionality)
export FIREBASE_PROJECT_ID=your-project-id
export GEMINI_API_KEY=your-gemini-key
export REDIS_URL=redis://localhost:6379
```

### Issue 6: Database Connection Failures

**Problem**: Tests fail due to Firebase/database connection issues.

**Solution**: Use mocked dependencies in tests:
```python
@patch('utils.firebase_utils.FirebaseUtils')
def test_with_mock_firebase(mock_firebase_class):
    mock_firebase = Mock()
    mock_firebase.db = Mock()
    mock_firebase_class.return_value = mock_firebase
    # Your test code here
```

## 🛠 CI/CD Pipeline Configuration

### GitHub Actions Workflow Status

The current workflow (`/.github/workflows/ci.yml`) includes:

1. **Validation Stage** ✅
   - Commit message validation
   - Branch naming validation

2. **Code Quality Stage** ✅
   - Pre-commit hooks
   - Black formatting
   - Flake8 linting
   - MyPy type checking

3. **Testing Stage** ✅
   - Unit tests with pytest
   - Integration tests
   - Coverage reporting
   - Multiple Python versions (3.11, 3.12)

4. **Security Stage** ✅
   - Safety vulnerability scanning
   - Bandit security linting

5. **Performance Stage** ✅
   - Load testing with Locust
   - Performance benchmarks

6. **Deployment Stage** ✅
   - Docker image building
   - Smoke tests

### Deployment Configurations

#### Render.com ✅
```yaml
# render.yaml
services:
  - type: web
    name: retailgenie-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn wsgi:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.1
```

#### Docker ✅
```dockerfile
# Updated Dockerfile with Python 3.12
FROM python:3.12-slim
# ... (see full Dockerfile above)
```

## 🚀 Quick Fix Commands

### Run Full Test Suite
```bash
cd backend
python -m pytest tests/ -v --cov=. --cov-report=html
```

### Fix Code Formatting
```bash
cd backend
black . --line-length=88
isort . --profile=black
flake8 --max-line-length=88 --ignore=E203,W503
```

### Test Docker Build
```bash
cd backend
docker build -t retailgenie-test -f deployment/Dockerfile .
```

### Run Load Tests
```bash
cd backend
pip install locust
locust -f tests/load/locustfile_simple.py --headless -u 5 -r 1 -t 30s --host=http://localhost:5000
```

## 📊 Monitoring and Debugging

### GitHub Actions Logs
1. Go to GitHub repository
2. Click "Actions" tab
3. Select failing workflow
4. Expand failed jobs to see detailed logs

### Local Debugging
```bash
# Run the fix script
./fix_cicd.sh

# Check test collection
cd backend && python -m pytest --collect-only

# Check imports
cd backend && python -c "from app import create_app; print('✅ App imports work')"

# Check pre-commit
cd backend && pre-commit run --all-files
```

### Performance Monitoring
```bash
# Run performance tests locally
cd backend
python monitoring/test_performance.py

# Generate load test report
locust -f tests/load/locustfile_simple.py --headless -u 10 -r 2 -t 60s --host=http://localhost:5000 --html=load_report.html
```

## ✅ Verification Checklist

- [x] All test files exist and are properly structured
- [x] Dockerfile uses correct Python version (3.12)
- [x] Requirements file path is correct in Dockerfile
- [x] Pre-commit configuration is valid
- [x] GitHub Actions workflow references existing files
- [x] Mock dependencies are used in tests
- [x] Environment variables are properly handled
- [x] Load testing configuration is set up
- [x] Deployment configurations are updated

## 🎯 Next Steps

1. **Run the fix script**: `./fix_cicd.sh`
2. **Commit changes**: All fixes have been applied
3. **Push to GitHub**: Trigger the CI/CD pipeline
4. **Monitor workflow**: Check GitHub Actions for any remaining issues
5. **Deploy**: Use the updated configurations for deployment

## 🆘 Getting Help

If issues persist:

1. **Check logs**: GitHub Actions → Your workflow → Failed job
2. **Test locally**: Run all tests in your development environment
3. **Validate environment**: Ensure all required tools are installed
4. **Review changes**: Compare with working configurations

## 🔄 Continuous Improvement

The CI/CD pipeline is configured to:
- Automatically run on pushes to main/develop branches
- Run on pull requests
- Provide detailed feedback on failures
- Generate coverage and performance reports
- Ensure code quality with multiple checks

Remember to keep dependencies updated and regularly review pipeline performance!
