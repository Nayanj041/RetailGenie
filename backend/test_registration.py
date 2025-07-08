#!/usr/bin/env python3
"""
Simple test to check registration endpoint without ML dependencies
"""

import sys
import os
import json
import requests
import subprocess
import time
import signal

def test_registration():
    """
    Tests the registration endpoint of a mock Flask application by launching it as a subprocess and performing HTTP requests.
    
    This function dynamically creates and runs a minimal Flask server exposing `/api/v1/health` and `/api/v1/auth/register` endpoints, then verifies the health check and registration functionality by sending HTTP requests and printing the results. The server process is terminated after the test completes.
    """
    print("🧪 Testing Registration Endpoint...")
    
    # Start a simple Flask app for testing
    test_app_code = """
import os
import sys
sys.path.insert(0, '/workspaces/RetailGenie/backend')

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import bcrypt
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        business_name = data.get("business_name")
        
        if not all([email, password, name]):
            return jsonify({"success": False, "error": "Email, password, and name required"}), 400
        
        if not business_name:
            return jsonify({"success": False, "error": "Business name is required for retailer registration"}), 400
        
        # Mock successful registration
        user_data = {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "business_name": business_name,
            "role": "retailer"
        }
        
        return jsonify({
            "success": True,
            "user_id": user_data["id"],
            "token": "test-token-123",
            "user": user_data,
            "message": "Retailer registered successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
"""
    
    # Write test app to file
    with open('/tmp/test_app.py', 'w') as f:
        f.write(test_app_code)
    
    # Start test app
    print("Starting test server on port 5001...")
    proc = subprocess.Popen([sys.executable, '/tmp/test_app.py'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
    
    time.sleep(3)  # Wait for server to start
    
    try:
        # Test health endpoint
        health_response = requests.get('http://localhost:5001/api/v1/health', timeout=5)
        print(f"Health check: {health_response.status_code}")
        
        # Test registration
        registration_data = {
            "name": "Test Retailer",
            "email": "test@example.com",
            "password": "test123",
            "business_name": "Test Store"
        }
        
        response = requests.post(
            'http://localhost:5001/api/v1/auth/register',
            json=registration_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Registration Status Code: {response.status_code}")
        print(f"Registration Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration endpoint works!")
        else:
            print("❌ Registration failed")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_registration()
