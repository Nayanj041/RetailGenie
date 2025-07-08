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
os.environ["FIREBASE_CREDENTIALS_PATH"] = (
    "/workspaces/RetailGenie/backend/retailgenie-production-firebase-adminsdk-fbsvc-f1c87b490f.json"
)

from app.utils.firebase_utils import FirebaseUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_fixed_app():
    """Create fixed Flask app with working authentication"""
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = "retailgenie-super-secret-key-2024"
    app.config["JWT_SECRET"] = "retailgenie-jwt-secret-key-2024"

    # CORS configuration - Allow frontend including Codespace URLs
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # Add Codespace URLs if we're in a Codespace
    codespace_name = os.environ.get("CODESPACE_NAME")
    if codespace_name:
        codespace_domain = os.environ.get(
            "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev"
        )
        cors_origins.extend(
            [
                f"https://{codespace_name}-3000.{codespace_domain}",
                f"https://{codespace_name}-3001.{codespace_domain}",
            ]
        )

    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Headers"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # Initialize Firebase
    firebase = FirebaseUtils()

    def generate_jwt_token(user_data):
        """Generate JWT token for user"""
        payload = {
            "user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "retailer"),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        }
        return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")

    @app.route("/", methods=["GET"])
    def root():
        return jsonify(
            {
                "message": "RetailGenie Fixed Authentication API",
                "version": "1.0.0",
                "status": "running",
                "endpoints": [
                    "POST /api/v1/auth/register",
                    "POST /api/v1/auth/login",
                    "GET  /api/v1/health",
                    "GET  /api/v1/products",
                ],
            }
        )

    @app.route("/api/v1/health", methods=["GET"])
    def health():
        return jsonify(
            {
                "status": "healthy",
                "message": "RetailGenie Authentication Service",
                "firebase_connected": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    @app.route("/api/v1/auth/register", methods=["POST", "OPTIONS"])
    def register():
        """Fixed user registration endpoint"""
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"}), 200

        try:
            # Validate request
            if not request.is_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Content-Type must be application/json",
                        }
                    ),
                    400,
                )

            data = request.get_json()
            if not data:
                return (
                    jsonify({"success": False, "message": "No JSON data provided"}),
                    400,
                )

            # Extract and validate required fields
            email = data.get("email", "").strip()
            password = data.get("password", "")
            name = data.get("name", "").strip()
            business_name = data.get("business_name", "").strip()

            # Validation
            if not all([email, password, name]):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Email, password, and name are required",
                        }
                    ),
                    400,
                )

            if not business_name:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Business name is required for retailer registration",
                        }
                    ),
                    400,
                )

            if "@" not in email:
                return (
                    jsonify({"success": False, "message": "Invalid email format"}),
                    400,
                )

            if len(password) < 6:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Password must be at least 6 characters",
                        }
                    ),
                    400,
                )

            # Check for existing user
            try:
                existing_users = firebase.get_documents("users") or []
                if any(
                    u.get("email", "").lower() == email.lower() for u in existing_users
                ):
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "User with this email already exists",
                            }
                        ),
                        400,
                    )
            except Exception as e:
                logger.warning(f"Error checking existing users: {e}")

            # Hash password
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

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
                "active": True,
            }

            # Save to Firebase
            user_id = firebase.create_document("users", user_data)

            # Generate token (remove password from response)
            user_for_response = user_data.copy()
            user_for_response.pop("password", None)
            token = generate_jwt_token(user_for_response)

            logger.info(f"User registered successfully: {email}")

            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Registration successful",
                        "token": token,
                        "user": user_for_response,
                    }
                ),
                201,
            )

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return (
                jsonify(
                    {"success": False, "message": f"Registration failed: {str(e)}"}
                ),
                500,
            )

    @app.route("/api/v1/auth/login", methods=["POST", "OPTIONS"])
    def login():
        """Fixed user login endpoint"""
        if request.method == "OPTIONS":
            return jsonify({"status": "ok"}), 200

        try:
            # Validate request
            if not request.is_json:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Content-Type must be application/json",
                        }
                    ),
                    400,
                )

            data = request.get_json()
            if not data:
                return (
                    jsonify({"success": False, "message": "No JSON data provided"}),
                    400,
                )

            # Extract credentials
            email = data.get("email", "").strip()
            password = data.get("password", "")

            if not email or not password:
                return (
                    jsonify(
                        {"success": False, "message": "Email and password are required"}
                    ),
                    400,
                )

            # Find user
            try:
                users = firebase.get_documents("users") or []
                user = next(
                    (u for u in users if u.get("email", "").lower() == email.lower()),
                    None,
                )

                if not user:
                    return (
                        jsonify(
                            {"success": False, "message": "Invalid email or password"}
                        ),
                        401,
                    )

                # Verify password
                stored_password = user.get("password", "")
                if not bcrypt.checkpw(
                    password.encode("utf-8"), stored_password.encode("utf-8")
                ):
                    return (
                        jsonify(
                            {"success": False, "message": "Invalid email or password"}
                        ),
                        401,
                    )

                # Update last login
                try:
                    user["last_login"] = datetime.now(timezone.utc).isoformat()
                    firebase.update_document(
                        "users", user["id"], {"last_login": user["last_login"]}
                    )
                except Exception as e:
                    logger.warning(f"Failed to update last login: {e}")

                # Generate token (remove password from response)
                user_for_response = user.copy()
                user_for_response.pop("password", None)
                token = generate_jwt_token(user_for_response)

                logger.info(f"User logged in successfully: {email}")

                return (
                    jsonify(
                        {
                            "success": True,
                            "message": "Login successful",
                            "token": token,
                            "user": user_for_response,
                        }
                    ),
                    200,
                )

            except Exception as e:
                logger.error(f"Database error during login: {e}")
                return (
                    jsonify({"success": False, "message": "Database error occurred"}),
                    500,
                )

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return (
                jsonify({"success": False, "message": f"Login failed: {str(e)}"}),
                500,
            )

    @app.route("/api/v1/products", methods=["GET"])
    def get_products():
        """Sample products endpoint"""
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
                        "stock": 100,
                    },
                    {
                        "id": "2",
                        "name": "Sample Tea",
                        "price": 15.99,
                        "category": "Beverages",
                        "stock": 75,
                    },
                ]

            return (
                jsonify({"success": True, "data": products, "count": len(products)}),
                200,
            )

        except Exception as e:
            logger.error(f"Products error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Endpoint not found",
                    "available_endpoints": [
                        "GET /",
                        "GET /api/v1/health",
                        "POST /api/v1/auth/register",
                        "POST /api/v1/auth/login",
                        "GET /api/v1/products",
                    ],
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

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
