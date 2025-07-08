#!/usr/bin/env python3

# Simple test to check if app.py can be imported
import sys
import os

try:
    print("Testing imports...")
    
    # Test individual imports
    print("1. Testing bcrypt...")
    import bcrypt
    print("   ✅ bcrypt OK")
    
    print("2. Testing jwt...")
    import jwt
    print("   ✅ jwt OK")
    
    print("3. Testing Flask...")
    from flask import Flask
    print("   ✅ Flask OK")
    
    print("4. Testing app creation...")
    from app import create_app
    print("   ✅ create_app import OK")
    
    print("5. Creating app...")
    app = create_app()
    print("   ✅ App created successfully")
    
    print("6. Testing auth endpoints...")
    with app.test_client() as client:
        # Test registration
        response = client.post('/api/v1/auth/register', 
                             json={'email': 'test@test.com', 'password': 'test123', 'name': 'Test', 'business_name': 'Test Business'},
                             content_type='application/json')
        print(f"   Registration response: {response.status_code} - {response.get_json()}")
        
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
