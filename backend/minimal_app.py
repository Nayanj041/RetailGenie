#!/usr/bin/env python3
"""
Minimal RetailGenie Backend for Testing Registration
"""
import os
import sys
import uuid
import bcrypt
import jwt
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add the current directory to Python path
sys.path.insert(0, "/workspaces/RetailGenie/backend")


def create_minimal_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["JWT_SECRET"] = "test-jwt-secret"

    # CORS configuration
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    def get_json_data():
        """Helper to get JSON data from request"""
        try:
            if not request.is_json:
                return (
                    None,
                    jsonify(
                        {
                            "success": False,
                            "error": "Content-Type must be application/json",
                        }
                    ),
                    400,
                )
            data = request.get_json()
            if not data:
                return (
                    None,
                    jsonify({"success": False, "error": "No JSON data provided"}),
                    400,
                )
            return data, None, None
        except Exception as e:
            return (
                None,
                jsonify({"success": False, "error": f"Invalid JSON: {str(e)}"}),
                400,
            )

    def generate_jwt_token(user_data):
        """Generate JWT token for user"""
        payload = {
            "user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "retailer"),
            "exp": datetime.now(timezone.utc).timestamp() + 86400,  # 24 hours
        }
        return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")

    @app.route("/api/v1/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "message": "RetailGenie Backend is running"})

    @app.route("/api/v1/auth/register", methods=["POST"])
    def register():
        """Retailer registration - business accounts only"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            # Extract data
            email = data.get("email")
            password = data.get("password")
            name = data.get("name")
            business_name = data.get("business_name")

            print(f"Registration attempt: {email}, business: {business_name}")

            # Validation
            if not all([email, password, name]):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Email, password, and name required",
                        }
                    ),
                    400,
                )

            if not business_name:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Business name is required for retailer registration",
                        }
                    ),
                    400,
                )

            if "@" not in email:
                return jsonify({"success": False, "error": "Invalid email format"}), 400

            if len(password) < 6:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Password must be at least 6 characters",
                        }
                    ),
                    400,
                )

            # For testing, we'll simulate successful registration without database
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            user_data = {
                "id": str(uuid.uuid4()),
                "email": email,
                "name": name,
                "business_name": business_name,
                "role": "retailer",
                "created_at": datetime.now().isoformat(),
                "active": True,
            }

            # Generate token
            token = generate_jwt_token(user_data)

            print(f"✅ Registration successful for {email}")

            return (
                jsonify(
                    {
                        "success": True,
                        "user_id": user_data["id"],
                        "token": token,
                        "user": user_data,
                        "message": "Retailer registered successfully",
                    }
                ),
                201,
            )

        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/auth/login", methods=["POST"])
    def login():
        """Login endpoint for testing"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            email = data.get("email")
            password = data.get("password")

            if not all([email, password]):
                return (
                    jsonify({"success": False, "error": "Email and password required"}),
                    400,
                )

            # Mock login success
            user_data = {
                "id": "test-user-id",
                "email": email,
                "name": "Test User",
                "role": "retailer",
            }

            token = generate_jwt_token(user_data)

            return (
                jsonify(
                    {
                        "success": True,
                        "token": token,
                        "user": user_data,
                        "message": "Login successful",
                    }
                ),
                200,
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return app


if __name__ == "__main__":
    print("🚀 Starting Minimal RetailGenie Backend...")
    app = create_minimal_app()
    print("✅ App created successfully")
    print("🌐 Starting server on http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
