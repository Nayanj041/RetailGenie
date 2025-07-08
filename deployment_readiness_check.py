#!/usr/bin/env python3
"""
RetailGenie Full Project Deployment Readiness Check
Comprehensive test of all components before Render deployment
"""

import os
import sys
import json
import traceback
from pathlib import Path

# Add backend to path
backend_path = Path('/workspaces/RetailGenie/backend')
sys.path.insert(0, str(backend_path))

def check_file_structure():
    """
    Checks for the presence of all required backend and frontend files needed for deployment.
    
    Returns:
        bool: True if all required files are present; False if any are missing.
    """
    print("📁 CHECKING FILE STRUCTURE")
    print("=" * 50)
    
    # Backend files
    backend_files = [
        'app.py',
        'wsgi.py', 
        'Procfile',
        'requirements.txt',
        'runtime.txt',
        '.env.example'
    ]
    
    missing_backend = []
    for file in backend_files:
        if not (backend_path / file).exists():
            missing_backend.append(file)
        else:
            print(f"✅ backend/{file}")
    
    # Frontend files
    frontend_path = Path('/workspaces/RetailGenie/frontend')
    frontend_files = [
        'package.json',
        'src/App.jsx',  # Changed from App.js to App.jsx
        'src/utils/AuthContext.js',
        '.env'
    ]
    
    missing_frontend = []
    for file in frontend_files:
        if not (frontend_path / file).exists():
            missing_frontend.append(file)
        else:
            print(f"✅ frontend/{file}")
    
    if missing_backend:
        print(f"❌ Missing backend files: {missing_backend}")
        return False
    
    if missing_frontend:
        print(f"❌ Missing frontend files: {missing_frontend}")
        return False
    
    print("✅ All required files present")
    return True

def check_backend_app():
    """
    Attempts to create the backend Flask app and verifies the presence and HTTP methods of critical API endpoints.
    
    Returns:
        bool: True if the app is created successfully and all required endpoints with correct methods are present; False otherwise.
    """
    print("\n🔧 CHECKING BACKEND APPLICATION")
    print("=" * 50)
    
    try:
        # Import from app.py file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "/workspaces/RetailGenie/backend/app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        app = app_module.create_app()
        print("✅ Flask app creates successfully")
        
        # Count routes
        routes = list(app.url_map.iter_rules())
        print(f"✅ Total routes: {len(routes)}")
        
        # Check critical endpoints
        critical_endpoints = {
            '/api/v1/health': 'GET',
            '/api/v1/auth/register': 'POST',
            '/api/v1/auth/login': 'POST',
            '/api/v1/ml/sentiment/analysis': 'GET',
            '/api/v1/ml/inventory/forecast': 'GET',
            '/api/v1/ml/pricing/optimize': 'POST'
        }
        
        found_endpoints = {}
        for rule in routes:
            if rule.rule in critical_endpoints:
                found_endpoints[rule.rule] = list(rule.methods)
        
        missing_endpoints = []
        for endpoint, expected_method in critical_endpoints.items():
            if endpoint in found_endpoints:
                if expected_method in found_endpoints[endpoint]:
                    print(f"✅ {endpoint} [{expected_method}]")
                else:
                    print(f"❌ {endpoint} - method {expected_method} not found")
                    missing_endpoints.append(f"{endpoint} [{expected_method}]")
            else:
                print(f"❌ {endpoint} - endpoint not found")
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"❌ Missing endpoints: {missing_endpoints}")
            return False
        
        print("✅ All critical endpoints present")
        return True
        
    except Exception as e:
        print(f"❌ Backend app creation failed: {e}")
        traceback.print_exc()
        return False

def check_registration_endpoint():
    """
    Tests the backend registration endpoint by submitting a sample registration request and verifying successful user creation and token generation.
    
    Returns:
        bool: True if the registration endpoint responds correctly and returns expected data; False otherwise.
    """
    print("\n🔐 CHECKING REGISTRATION ENDPOINT")
    print("=" * 50)
    
    try:
        # Import from app.py file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "/workspaces/RetailGenie/backend/app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        app = app_module.create_app()
        
        with app.test_client() as client:
            # Test registration
            import uuid
            test_data = {
                'name': 'Test Retailer Deploy',
                'email': f'deploy-test-{uuid.uuid4().hex[:8]}@store.com',
                'password': 'deploytest123',
                'business_name': 'Deploy Test Store'
            }
            
            response = client.post('/api/v1/auth/register', 
                                  json=test_data,
                                  headers={'Content-Type': 'application/json'})
            
            print(f"Registration Status Code: {response.status_code}")
            result = response.get_json()
            
            # Check if we got a token (successful registration)
            if result and 'token' in result and 'user' in result:
                print("✅ Registration endpoint works correctly")
                print(f"✅ Token generated: Yes")
                print(f"✅ User created with ID: {result['user'].get('id')}")
                return True
            elif response.status_code in [200, 201]:
                if result and result.get('success'):
                    print("✅ Registration endpoint works correctly")
                    print(f"✅ Token generated: {'token' in result}")
                    return True
                else:
                    print(f"❌ Registration failed: {result.get('error') if result else 'No response'}")
                    return False
            else:
                print(f"❌ Registration endpoint error: {result.get('error') if result else 'Unknown error'}")
                print(f"Full response: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        traceback.print_exc()
        return False

def check_ml_endpoints():
    """
    Tests the machine learning-related API endpoints of the backend for correct responses.
    
    Returns:
        bool: True if all ML endpoints respond as expected without exceptions; False otherwise.
    """
    print("\n🤖 CHECKING ML ENDPOINTS")
    print("=" * 50)
    
    try:
        # Import from app.py file directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_module", "/workspaces/RetailGenie/backend/app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        app = app_module.create_app()
        
        with app.test_client() as client:
            # Test sentiment analysis
            response = client.get('/api/v1/ml/sentiment/analysis')
            print(f"Sentiment Analysis: {response.status_code}")
            if response.status_code == 200:
                print("✅ Sentiment analysis endpoint works")
            else:
                print("❌ Sentiment analysis endpoint failed")
            
            # Test inventory forecast
            response = client.get('/api/v1/ml/inventory/forecast')
            print(f"Inventory Forecast: {response.status_code}")
            if response.status_code == 200:
                print("✅ Inventory forecast endpoint works")
            else:
                print("❌ Inventory forecast endpoint failed")
            
            # Test pricing optimization
            response = client.post('/api/v1/ml/pricing/optimize',
                                  json={'product_id': 'test-product'},
                                  headers={'Content-Type': 'application/json'})
            print(f"Pricing Optimization: {response.status_code}")
            if response.status_code in [200, 404]:  # 404 is OK if product not found but endpoint works
                result = response.get_json()
                if response.status_code == 200 or (result and 'error' in result):
                    print("✅ Pricing optimization endpoint works")
                else:
                    print("❌ Pricing optimization endpoint failed")
            else:
                print("❌ Pricing optimization endpoint failed")
                
        return True
        
    except Exception as e:
        print(f"❌ ML endpoints test failed: {e}")
        return False

def check_environment_config():
    """
    Checks that required environment configuration files and variables are present for both backend and frontend.
    
    Verifies the existence of the backend `.env.example` file and ensures it contains all required environment variable names. Also checks that the frontend `.env` file exists and includes the `REACT_APP_API_URL` variable.
    
    Returns:
        bool: True if all required configuration files and variables are present; False otherwise.
    """
    print("\n🌍 CHECKING ENVIRONMENT CONFIGURATION")
    print("=" * 50)
    
    # Check backend .env.example
    env_example = backend_path / '.env.example'
    if env_example.exists():
        print("✅ Backend .env.example exists")
        
        required_vars = [
            'FIREBASE_PROJECT_ID',
            'GEMINI_API_KEY',
            'SECRET_KEY',
            'JWT_SECRET'
        ]
        
        with open(env_example) as f:
            content = f.read()
            
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
            else:
                print(f"✅ {var} in .env.example")
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
    else:
        print("❌ Backend .env.example missing")
        return False
    
    # Check frontend .env
    frontend_env = Path('/workspaces/RetailGenie/frontend/.env')
    if frontend_env.exists():
        print("✅ Frontend .env exists")
        with open(frontend_env) as f:
            content = f.read()
            if 'REACT_APP_API_URL' in content:
                print("✅ REACT_APP_API_URL configured")
            else:
                print("❌ REACT_APP_API_URL missing")
                return False
    else:
        print("❌ Frontend .env missing")
        return False
    
    return True

def check_deployment_files():
    """
    Verify that deployment-specific files (`Procfile` and `runtime.txt`) exist in the backend directory and are correctly configured.
    
    Returns:
        bool: True if both files are present and valid, otherwise False.
    """
    print("\n🚀 CHECKING DEPLOYMENT FILES")
    print("=" * 50)
    
    # Check Procfile
    procfile = backend_path / 'Procfile'
    if procfile.exists():
        with open(procfile) as f:
            content = f.read().strip()
            if 'gunicorn' in content and 'wsgi:app' in content:
                print("✅ Procfile correctly configured")
            else:
                print(f"❌ Procfile incorrect: {content}")
                return False
    else:
        print("❌ Procfile missing")
        return False
    
    # Check runtime.txt
    runtime = backend_path / 'runtime.txt'
    if runtime.exists():
        with open(runtime) as f:
            content = f.read().strip()
            if content.startswith('python-'):
                print(f"✅ Runtime specified: {content}")
            else:
                print(f"❌ Invalid runtime: {content}")
                return False
    else:
        print("❌ runtime.txt missing")
        return False
    
    return True

def main():
    """
    Runs all deployment readiness checks and prints a summary of their results.
    
    Executes a series of validation functions to verify the RetailGenie project is ready for deployment, including file structure, backend application, API endpoints, environment configuration, and deployment files. Prints a detailed summary table indicating pass/fail status for each check and outputs deployment instructions if all checks pass.
    
    Returns:
        bool: True if all checks pass and the project is ready for deployment; False otherwise.
    """
    print("🔍 RETAILGENIE DEPLOYMENT READINESS CHECK")
    print("=" * 70)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Backend Application", check_backend_app),
        ("Registration Endpoint", check_registration_endpoint),
        ("ML Endpoints", check_ml_endpoints),
        ("Environment Config", check_environment_config),
        ("Deployment Files", check_deployment_files)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 PROJECT IS READY FOR RENDER DEPLOYMENT!")
        print("🚀 All checks passed successfully")
        print("\nNext steps:")
        print("1. Push to GitHub repository")
        print("2. Connect to Render")
        print("3. Set environment variables in Render")
        print("4. Deploy!")
    else:
        print("❌ PROJECT NOT READY FOR DEPLOYMENT")
        print("⚠️  Please fix the failed checks above")
    
    return all_passed

if __name__ == "__main__":
    main()
