#!/usr/bin/env python3
"""
Test CORS configuration for RetailGenie backend
This script tests if CORS is properly configured
"""

import requests
import json

def test_cors():
    # Test the backend URL that's having issues
    backend_url = "https://retailgenie-d1ej.onrender.com"
    frontend_origin = "https://retailgenie-1.onrender.com"
    
    print("🧪 Testing CORS Configuration")
    print(f"Backend: {backend_url}")
    print(f"Frontend Origin: {frontend_origin}")
    print("-" * 50)
    
    # Test 1: Health check
    try:
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{backend_url}/api/v1/health")
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    print()
    
    # Test 2: CORS test endpoint
    try:
        print("2️⃣ Testing CORS test endpoint...")
        response = requests.get(f"{backend_url}/api/v1/cors-test")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ CORS test passed")
        else:
            print("   ❌ CORS test failed")
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")
    
    print()
    
    # Test 3: OPTIONS preflight request for login
    try:
        print("3️⃣ Testing OPTIONS preflight for login...")
        headers = {
            'Origin': frontend_origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{backend_url}/api/v1/auth/login", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        print(f"   Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        print(f"   Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not set')}")
        
        if response.status_code == 200:
            print("   ✅ OPTIONS preflight passed")
        else:
            print("   ❌ OPTIONS preflight failed")
    except Exception as e:
        print(f"   ❌ OPTIONS preflight error: {e}")
    
    print()
    
    # Test 4: Actual login request (with demo credentials)
    try:
        print("4️⃣ Testing actual login request...")
        headers = {
            'Origin': frontend_origin,
            'Content-Type': 'application/json'
        }
        data = {
            "email": "demo@retailgenie.com",
            "password": "demo123"
        }
        response = requests.post(f"{backend_url}/api/v1/auth/login", 
                               headers=headers, 
                               json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
        
        if response.status_code in [200, 401]:  # 401 is expected if demo user doesn't exist
            print("   ✅ Login request reached backend")
            if response.status_code == 200:
                print("   ✅ Login successful")
            else:
                print("   ℹ️ Login failed (credentials issue, but CORS working)")
        else:
            print("   ❌ Login request failed")
            
        # Print response for debugging
        try:
            print(f"   Response: {response.text[:200]}...")
        except:
            pass
            
    except Exception as e:
        print(f"   ❌ Login request error: {e}")

if __name__ == "__main__":
    test_cors()
