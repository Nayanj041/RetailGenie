#!/usr/bin/env python3
"""
Simplified Backend Startup for Testing
"""

import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_simple_app():
    app = Flask(__name__)

    # CORS configuration
    CORS(
        app,
        origins=["http://localhost:3000", "http://localhost:3001"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    @app.route("/api/v1/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy", "message": "Backend is running"}), 200

    @app.route("/api/v1/auth/register", methods=["POST"])
    def register():
        try:
            if not request.is_json:
                return (
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
                    jsonify({"success": False, "error": "No JSON data provided"}),
                    400,
                )

            # Simple validation
            required_fields = ["name", "email", "password", "business_name"]
            for field in required_fields:
                if not data.get(field):
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": f"Missing required field: {field}",
                            }
                        ),
                        400,
                    )

            # Mock successful response
            return (
                jsonify(
                    {
                        "success": True,
                        "token": "mock-jwt-token-for-testing",
                        "user": {
                            "id": "mock-user-id",
                            "name": data["name"],
                            "email": data["email"],
                            "business_name": data["business_name"],
                            "role": "retailer",
                        },
                        "message": "Registration successful (test mode)",
                    }
                ),
                201,
            )

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/auth/login", methods=["POST"])
    def login():
        try:
            if not request.is_json:
                return (
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
                    jsonify({"success": False, "error": "No JSON data provided"}),
                    400,
                )

            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return (
                    jsonify({"success": False, "error": "Email and password required"}),
                    400,
                )

            # Mock successful response
            return (
                jsonify(
                    {
                        "success": True,
                        "token": "mock-jwt-token-for-testing",
                        "user": {
                            "id": "mock-user-id",
                            "name": "Test User",
                            "email": email,
                            "role": "retailer",
                        },
                        "message": "Login successful (test mode)",
                    }
                ),
                200,
            )

        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_simple_app()
    logger.info("🚀 Starting simplified RetailGenie Backend...")
    logger.info("🌐 Server will start at http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
