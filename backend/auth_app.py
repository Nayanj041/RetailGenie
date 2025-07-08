#!/usr/bin/env python3
"""
Minimal Flask App with Working Authentication
"""

import os
import uuid
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

# Set Firebase credentials
os.environ['FIREBASE_CREDENTIALS_PATH'] = '/workspaces/RetailGenie/backend/retailgenie-production-firebase-adminsdk-fbsvc-f1c87b490f.json'

from app.utils.firebase_utils import FirebaseUtils

def create_minimal_app():
    """Create minimal Flask app with authentication"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['JWT_SECRET'] = 'dev-jwt-secret'
    
    # CORS configuration
    CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'], 
         supports_credentials=True, 
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize Firebase
    firebase = FirebaseUtils()
    
    def generate_jwt_token(user_data):
        """Generate JWT token for user"""
        payload = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'role': user_data.get('role', 'user'),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        return jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')
    
    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "message": "RetailGenie Authentication API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": [
                "/api/v1/auth/register",
                "/api/v1/auth/login",
                "/api/v1/health"
            ]
        })
    
    @app.route("/api/v1/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "message": "Authentication service is running",
            "firebase_connected": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    @app.route("/api/v1/auth/register", methods=["POST"])
    def register():
        """User registration endpoint"""
        try:
            # Get JSON data
            if not request.is_json:
                return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No JSON data provided"}), 400
            
            # Extract and validate data
            email = data.get("email")
            password = data.get("password")
            name = data.get("name")
            business_name = data.get("business_name")
            
            if not all([email, password, name]):
                return jsonify({"success": False, "error": "Email, password, and name required"}), 400
            
            if not business_name:
                return jsonify({"success": False, "error": "Business name is required for retailer registration"}), 400
            
            # Validate email format
            if "@" not in email:
                return jsonify({"success": False, "error": "Invalid email format"}), 400
            
            # Validate password strength
            if len(password) < 6:
                return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
            
            # Check if user already exists
            existing_users = firebase.get_documents("users") or []
            if any(u.get("email") == email for u in existing_users):
                return jsonify({"success": False, "error": "User already exists"}), 400
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user data
            user_data = {
                "id": str(uuid.uuid4()),
                "email": email,
                "name": name,
                "business_name": business_name,
                "password": hashed_password.decode('utf-8'),
                "role": "retailer",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": None,
                "active": True
            }
            
            # Save user to Firebase
            user_id = firebase.create_document("users", user_data)
            
            # Generate token (remove password from user data first)
            user_for_token = user_data.copy()
            user_for_token.pop("password", None)
            token = generate_jwt_token(user_for_token)
            
            return jsonify({
                "success": True,
                "user_id": user_id,
                "token": token,
                "user": user_for_token,
                "message": "Retailer registered successfully"
            }), 201
                
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/v1/auth/login", methods=["POST"])
    def login():
        """User login endpoint"""
        try:
            # Get JSON data
            if not request.is_json:
                return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No JSON data provided"}), 400
            
            # Extract credentials
            email = data.get("email")
            password = data.get("password")
            
            if not email or not password:
                return jsonify({"success": False, "error": "Email and password required"}), 400
            
            # Find user
            users = firebase.get_documents("users") or []
            user = next((u for u in users if u.get("email") == email), None)
            
            if not user:
                return jsonify({"success": False, "error": "Invalid credentials"}), 401
            
            # Check password
            if bcrypt.checkpw(password.encode('utf-8'), user.get("password", "").encode('utf-8')):
                # Update last login
                user["last_login"] = datetime.now(timezone.utc).isoformat()
                firebase.update_document("users", user["id"], {"last_login": user["last_login"]})
                
                # Generate token (remove password from user data first)
                user_for_token = user.copy()
                user_for_token.pop("password", None)
                token = generate_jwt_token(user_for_token)
                
                return jsonify({
                    "success": True,
                    "token": token,
                    "user": user_for_token,
                    "message": "Login successful"
                }), 200
            else:
                return jsonify({"success": False, "error": "Invalid credentials"}), 401
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "available_endpoints": ["/", "/api/v1/health", "/api/v1/auth/register", "/api/v1/auth/login"]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == "__main__":
    app = create_minimal_app()
    print("🚀 Starting RetailGenie Authentication Service...")
    print("📍 Available endpoints:")
    print("   GET  /")
    print("   GET  /api/v1/health")
    print("   POST /api/v1/auth/register")
    print("   POST /api/v1/auth/login")
    print("🌐 Running on http://localhost:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
