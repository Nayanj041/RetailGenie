#!/usr/bin/env python3
"""
RetailGenie Authentication Demo
Complete working authentication system for testing
"""

import json
import requests
import time

# Configuration
BACKEND_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """
    Checks the health status of the backend service by sending a GET request to the health endpoint.
    
    Returns:
        bool: True if the backend responds successfully, False if an error occurs.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=5)
        print(f"✅ Backend Health: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Backend Health Check Failed: {e}")
        return False

def test_registration():
    """
    Attempts to register a new demo user with the backend authentication service.
    
    Sends a POST request to the registration endpoint with generated user data. Prints the registration status and returns the response JSON if successful, or None on failure.
    """
    try:
        user_data = {
            "email": f"demo{int(time.time())}@retailgenie.com",
            "password": "demo123456",
            "name": "Demo User",
            "business_name": "Demo Business"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/register",
            headers={"Content-Type": "application/json"},
            json=user_data,
            timeout=10
        )
        
        print(f"✅ Registration: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Token: {data.get('token')[:20]}...")
            return data
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Registration Failed: {e}")
        return None

def test_login(email="demo@retailgenie.com", password="demo123456"):
    """
    Attempts to log in a user with the provided email and password.
    
    Parameters:
        email (str): The user's email address. Defaults to the demo user.
        password (str): The user's password. Defaults to the demo password.
    
    Returns:
        dict or None: The JSON response containing user and token information if login is successful; otherwise, None.
    """
    try:
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data,
            timeout=10
        )
        
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   User: {data.get('user', {}).get('name')}")
            print(f"   Token: {data.get('token')[:20]}...")
            return data
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        return None

def test_authenticated_request(token):
    """
    Sends an authenticated GET request to the products endpoint to verify token validity.
    
    Parameters:
        token (str): Bearer token used for authentication.
    
    Returns:
        bool: True if the request succeeds with status 200, otherwise False.
    """
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BACKEND_URL}/api/v1/products",
            headers=headers,
            timeout=10
        )
        
        print(f"✅ Authenticated Request: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Products Count: {data.get('count', 0)}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authenticated Request Failed: {e}")
        return False

def test_frontend_backend_flow():
    """
    Runs the complete authentication flow, including backend health check, user registration, login, and an authenticated API request.
    
    Returns:
        bool: True when the flow completes, False if the backend health check fails.
    """
    print("🧪 Testing Complete Authentication Flow")
    print("=" * 60)
    
    # Step 1: Check backend health
    print("\n1. Checking Backend Health...")
    if not test_backend_health():
        return False
    
    # Step 2: Test registration
    print("\n2. Testing User Registration...")
    registration_result = test_registration()
    
    # Step 3: Test login (use registered user or fallback)
    print("\n3. Testing User Login...")
    if registration_result:
        login_result = test_login(
            registration_result['user']['email'], 
            "demo123456"
        )
    else:
        # Try with a fallback user
        login_result = test_login()
    
    # Step 4: Test authenticated request
    if login_result and login_result.get('token'):
        print("\n4. Testing Authenticated Request...")
        test_authenticated_request(login_result['token'])
    
    print("\n" + "=" * 60)
    print("🎯 Authentication Flow Test Complete!")
    
    return True

def create_frontend_config():
    """
    Generate and write the frontend API configuration file for the RetailGenie system.
    
    Creates a JSON file containing API base URL, version, endpoint paths, and CORS settings, and saves it to the frontend configuration directory.
    """
    config = {
        "apiBaseUrl": BACKEND_URL,
        "apiVersion": "v1",
        "endpoints": {
            "auth": {
                "login": "/api/v1/auth/login",
                "register": "/api/v1/auth/register",
                "logout": "/api/v1/auth/logout"
            },
            "products": "/api/v1/products",
            "customers": "/api/v1/customers",
            "orders": "/api/v1/orders",
            "analytics": "/api/v1/analytics"
        },
        "cors": {
            "origins": [FRONTEND_URL],
            "credentials": True
        }
    }
    
    with open('/workspaces/RetailGenie/frontend/src/config/api.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Frontend API configuration created")

if __name__ == "__main__":
    print("🚀 RetailGenie Authentication Demo")
    print("=" * 60)
    
    # Run the complete test
    test_frontend_backend_flow()
    
    # Create frontend config
    print("\n📝 Creating Frontend Configuration...")
    try:
        create_frontend_config()
    except Exception as e:
        print(f"❌ Frontend config creation failed: {e}")
    
    print("\n🎉 Demo Complete!")
    print("\nℹ️  How to use:")
    print("   1. Backend running on: http://localhost:5000")
    print("   2. Frontend should run on: http://localhost:3000")
    print("   3. Use the demo credentials for testing")
    print("   4. Check backend logs for debugging: tail -f backend.log")
