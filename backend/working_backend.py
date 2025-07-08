#!/usr/bin/env python3
"""
Working Minimal Backend for RetailGenie
Port 5001
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import uuid
import hashlib
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS configuration
CORS(app, 
     origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000'], 
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# In-memory storage for testing
users_db = {}

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "message": "RetailGenie Backend is running",
        "timestamp": time.time()
    }), 200

@app.route('/api/v1/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        logger.info("Registration request received")
        
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        logger.info(f"Registration data: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        email = data['email']
        
        # Check if user already exists
        if email in users_db:
            return jsonify({"success": False, "error": "User already exists"}), 400
        
        # Create user
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "name": data['name'],
            "email": email,
            "business_name": data.get('business_name', data.get('businessName', '')),
            "role": "retailer",
            "created_at": time.time()
        }
        
        users_db[email] = user_data
        
        # Generate mock token
        token = f"mock-jwt-{hashlib.md5(email.encode()).hexdigest()}"
        
        logger.info(f"User registered successfully: {email}")
        
        return jsonify({
            "success": True,
            "token": token,
            "user": user_data,
            "message": "Retailer registered successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        logger.info("Login request received")
        
        if not request.is_json:
            return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required"}), 400
        
        # Check if user exists
        if email not in users_db:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        user_data = users_db[email]
        
        # Generate mock token
        token = f"mock-jwt-{hashlib.md5(email.encode()).hexdigest()}"
        
        logger.info(f"User logged in successfully: {email}")
        
        return jsonify({
            "success": True,
            "token": token,
            "user": user_data,
            "message": "Login successful"
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/auth/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"success": False, "error": "No authorization header"}), 401
    
    # Mock profile response
    return jsonify({
        "success": True,
        "data": {
            "id": "mock-user-id",
            "name": "Test User",
            "email": "test@example.com",
            "role": "retailer"
        }
    }), 200

if __name__ == '__main__':
    logger.info("🚀 Starting RetailGenie Backend on port 5001...")
    logger.info("🌐 CORS configured for frontend connections")
    logger.info("🔑 Authentication endpoints ready")
    app.run(debug=True, host="0.0.0.0", port=5001)
