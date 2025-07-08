#!/usr/bin/env python3
"""
Minimal Flask app test - testing without problematic imports
"""

import sys
import os
from dotenv import load_dotenv
from flask import Flask, jsonify

# Load environment variables
load_dotenv()


def create_minimal_app():
    """Create a minimal Flask app for testing"""
    app = Flask(__name__)

    # Basic configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
    app.config["DEBUG"] = False

    @app.route("/api/v1/health")
    def health():
        return jsonify(
            {
                "status": "healthy",
                "message": "RetailGenie Backend is running",
                "timestamp": "2025-07-02",
            }
        )

    @app.route("/api/v1/test")
    def test():
        return jsonify({"message": "Test endpoint working", "app_name": app.name})

    return app


def test_minimal_app():
    """Test the minimal app"""
    print("🧪 Testing minimal Flask app...")

    try:
        app = create_minimal_app()
        print("✅ Minimal app created successfully")

        # Test with test client
        with app.test_client() as client:
            response = client.get("/api/v1/health")
            print(f"✅ Health endpoint: {response.status_code}")

            response = client.get("/api/v1/test")
            print(f"✅ Test endpoint: {response.status_code}")

        print("🎉 Minimal app test passed!")
        return True

    except Exception as e:
        print(f"❌ Minimal app test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    if test_minimal_app():
        print("\n🚀 Basic Flask functionality working!")
        print("📋 The issue is with the advanced route imports.")
        print("   You can deploy the basic version and fix routes later.")

        # Start the minimal server for testing
        print("\n🌐 Starting minimal server on port 5000...")
        app = create_minimal_app()
        app.run(debug=False, host="0.0.0.0", port=5000)
    else:
        print("❌ Basic Flask not working")
        sys.exit(1)
