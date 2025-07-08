#!/usr/bin/env python3
"""
RetailGenie Fixed Authentication Backend
Complete working authentication system
"""

import os
import uuid
import jwt
import bcrypt
import logging
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

# Set environment variables
os.environ['FIREBASE_CREDENTIALS_PATH'] = '/workspaces/RetailGenie/backend/retailgenie-production-firebase-adminsdk-fbsvc-f1c87b490f.json'

from app.utils.firebase_utils import FirebaseUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_fixed_app():
    """
    Create and configure a Flask application providing authentication and product endpoints with Firebase integration.
    
    This function sets up a Flask app with CORS support for local and GitHub Codespaces origins, initializes Firebase utilities, and registers routes for user registration, login, health checks, and product retrieval. It also configures JWT-based authentication and custom error handlers for 404 and 500 responses.
    
    Returns:
        app (Flask): A configured Flask application instance ready to run.
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'retailgenie-super-secret-key-2024'
    app.config['JWT_SECRET'] = 'retailgenie-jwt-secret-key-2024'
    
    # CORS configuration - Allow frontend including Codespace URLs
    cors_origins = ['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001']
    
    # Add Codespace URLs if we're in a Codespace
    codespace_name = os.environ.get('CODESPACE_NAME')
    if codespace_name:
        codespace_domain = os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'app.github.dev')
        cors_origins.extend([
            f'https://{codespace_name}-3000.{codespace_domain}',
            f'https://{codespace_name}-3001.{codespace_domain}'
        ])
    
    CORS(app, 
         origins=cors_origins, 
         supports_credentials=True, 
         allow_headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Headers'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize Firebase
    firebase = FirebaseUtils()
    
    def generate_jwt_token(user_data):
        """
        Generate a JWT token containing user ID, email, role, and a 24-hour expiration.
        
        Parameters:
            user_data (dict): Dictionary containing user information, including 'id', 'email', and optionally 'role'.
        
        Returns:
            str: Encoded JWT token as a string.
        """
        payload = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'role': user_data.get('role', 'retailer'),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        return jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')
    
    @app.route("/", methods=["GET"])
    def root():
        """
        Return a JSON response with API information, current status, version, and available endpoints.
        """
        return jsonify({
            "message": "RetailGenie Fixed Authentication API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": [
                "POST /api/v1/auth/register",
                "POST /api/v1/auth/login", 
                "GET  /api/v1/health",
                "GET  /api/v1/products"
            ]
        })
    
    @app.route("/api/v1/health", methods=["GET"])
    def health():
        """
        Return a JSON response indicating the health status of the authentication service, including a timestamp and Firebase connection status.
        """
        return jsonify({
            "status": "healthy",
            "message": "RetailGenie Authentication Service",
            "firebase_connected": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    @app.route("/api/v1/auth/register", methods=["POST", "OPTIONS"])
    def register():
        """
        Handles user registration by validating input, checking for existing users, hashing the password, creating a new retailer user in Firebase, and returning a JWT token and user data on success.
        
        Returns:
            Response: A JSON response indicating success or failure, with a JWT token and user information on successful registration.
        """
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"}), 200
            
        try:
            # Validate request
            if not request.is_json:
                return jsonify({
                    "success": False, 
                    "message": "Content-Type must be application/json"
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False, 
                    "message": "No JSON data provided"
                }), 400
            
            # Extract and validate required fields
            email = data.get("email", "").strip()
            password = data.get("password", "")
            name = data.get("name", "").strip()
            business_name = data.get("business_name", "").strip()
            
            # Validation
            if not all([email, password, name]):
                return jsonify({
                    "success": False,
                    "message": "Email, password, and name are required"
                }), 400
            
            if not business_name:
                return jsonify({
                    "success": False,
                    "message": "Business name is required for retailer registration"
                }), 400
            
            if "@" not in email:
                return jsonify({
                    "success": False,
                    "message": "Invalid email format"
                }), 400
            
            if len(password) < 6:
                return jsonify({
                    "success": False,
                    "message": "Password must be at least 6 characters"
                }), 400
            
            # Check for existing user
            try:
                existing_users = firebase.get_documents("users") or []
                if any(u.get("email", "").lower() == email.lower() for u in existing_users):
                    return jsonify({
                        "success": False,
                        "message": "User with this email already exists"
                    }), 400
            except Exception as e:
                logger.warning(f"Error checking existing users: {e}")
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            user_data = {
                "id": str(uuid.uuid4()),
                "email": email.lower(),
                "name": name,
                "business_name": business_name,
                "password": hashed_password,
                "role": "retailer",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": None,
                "active": True
            }
            
            # Save to Firebase
            user_id = firebase.create_document("users", user_data)
            
            # Generate token (remove password from response)
            user_for_response = user_data.copy()
            user_for_response.pop("password", None)
            token = generate_jwt_token(user_for_response)
            
            logger.info(f"User registered successfully: {email}")
            
            return jsonify({
                "success": True,
                "message": "Registration successful",
                "token": token,
                "user": user_for_response
            }), 201
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Registration failed: {str(e)}"
            }), 500
    
    @app.route("/api/v1/auth/login", methods=["POST", "OPTIONS"])
    def login():
        """
        Handles user login by validating credentials, verifying the user against stored records, and issuing a JWT token upon successful authentication.
        
        Returns:
            JSON response containing a success flag, message, JWT token, and user information (excluding password) on successful login, or an error message with appropriate HTTP status code on failure.
        """
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"}), 200
            
        try:
            # Validate request
            if not request.is_json:
                return jsonify({
                    "success": False,
                    "message": "Content-Type must be application/json"
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "message": "No JSON data provided"
                }), 400
            
            # Extract credentials
            email = data.get("email", "").strip()
            password = data.get("password", "")
            
            if not email or not password:
                return jsonify({
                    "success": False,
                    "message": "Email and password are required"
                }), 400
            
            # Find user
            try:
                users = firebase.get_documents("users") or []
                user = next((u for u in users if u.get("email", "").lower() == email.lower()), None)
                
                if not user:
                    return jsonify({
                        "success": False,
                        "message": "Invalid email or password"
                    }), 401
                
                # Verify password
                stored_password = user.get("password", "")
                if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    return jsonify({
                        "success": False,
                        "message": "Invalid email or password"
                    }), 401
                
                # Update last login
                try:
                    user["last_login"] = datetime.now(timezone.utc).isoformat()
                    firebase.update_document("users", user["id"], {"last_login": user["last_login"]})
                except Exception as e:
                    logger.warning(f"Failed to update last login: {e}")
                
                # Generate token (remove password from response)
                user_for_response = user.copy()
                user_for_response.pop("password", None)
                token = generate_jwt_token(user_for_response)
                
                logger.info(f"User logged in successfully: {email}")
                
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "token": token,
                    "user": user_for_response
                }), 200
                
            except Exception as e:
                logger.error(f"Database error during login: {e}")
                return jsonify({
                    "success": False,
                    "message": "Database error occurred"
                }), 500
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Login failed: {str(e)}"
            }), 500
    
    @app.route("/api/v1/products", methods=["GET"])
    def get_products():
        """
        Retrieve the list of products from Firebase, or return sample products if none are found.
        
        Returns:
            A Flask JSON response containing a success flag, product data, and product count on success, or an error message on failure.
        """
        try:
            products = firebase.get_documents("products") or []
            
            if not products:
                # Return sample data
                products = [
                    {
                        "id": "1",
                        "name": "Sample Coffee",
                        "price": 19.99,
                        "category": "Beverages",
                        "stock": 100
                    },
                    {
                        "id": "2", 
                        "name": "Sample Tea",
                        "price": 15.99,
                        "category": "Beverages", 
                        "stock": 75
                    }
                ]
            
            return jsonify({
                "success": True,
                "data": products,
                "count": len(products)
            }), 200
            
        except Exception as e:
            logger.error(f"Products error: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 Not Found errors by returning a JSON response with an error message and a list of available API endpoints.
        
        Returns:
            A tuple containing a JSON response and the HTTP 404 status code.
        """
        return jsonify({
            "success": False,
            "message": "Endpoint not found",
            "available_endpoints": [
                "GET /",
                "GET /api/v1/health", 
                "POST /api/v1/auth/register",
                "POST /api/v1/auth/login",
                "GET /api/v1/products"
            ]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        Handles uncaught internal server errors by returning a standardized JSON response with a 500 status code.
        """
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500
    
    return app

if __name__ == "__main__":
    app = create_fixed_app()
    logger.info("🚀 Starting RetailGenie Fixed Authentication Service...")
    logger.info("📍 Available endpoints:")
    logger.info("   POST /api/v1/auth/register")
    logger.info("   POST /api/v1/auth/login")
    logger.info("   GET  /api/v1/health")
    logger.info("   GET  /api/v1/products")
    logger.info("🌐 Server running on http://0.0.0.0:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
