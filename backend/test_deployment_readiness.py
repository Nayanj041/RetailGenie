#!/usr/bin/env python3
"""
Test wsgi.py imports to verify deployment readiness
"""

import sys
import traceback
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_imports():
    """Test all imports from wsgi.py"""
    try:
        print("Testing wsgi.py imports...")

        # Test basic imports
        print("✓ Testing basic Python imports...")
        import os
        import sys
        from pathlib import Path

        # Test Flask imports
        print("✓ Testing Flask imports...")
        from flask import Flask
        from flask_cors import CORS
        import logging
        from datetime import datetime

        # Test config import
        print("✓ Testing config import...")
        from config.config import Config

        # Test route imports
        print("✓ Testing route imports...")
        from app.routes.auth_routes import auth_bp
        from app.routes.product_routes import product_bp
        from app.routes.inventory_routes import inventory_bp
        from app.routes.analytics_routes import analytics_bp
        from app.routes.ai_assistant_routes import ai_assistant_bp
        from app.routes.feedback_routes import feedback_bp
        from app.routes.pricing_routes import pricing_bp

        # Test middleware imports
        print("✓ Testing middleware imports...")
        from app.middleware.auth_middleware import AuthMiddleware
        from app.middleware.cors_middleware import setup_cors
        from app.middleware.logging_middleware import setup_logging

        # Test wsgi import
        print("✓ Testing wsgi import...")
        from wsgi import app, create_app

        print("\n🎉 All imports successful!")
        print(f"✓ App object type: {type(app)}")
        print(f"✓ App name: {app.name}")

        return True

    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False


def test_app_creation():
    """Test app creation"""
    try:
        print("\nTesting app creation...")
        from wsgi import create_app

        app = create_app()
        print(f"✓ App created successfully: {app.name}")

        # Test health endpoint
        with app.test_client() as client:
            response = client.get("/health")
            print(f"✓ Health check status: {response.status_code}")

        return True

    except Exception as e:
        print(f"❌ App creation failed: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    print("🔍 RetailGenie Deployment Readiness Test\n")

    success = True
    success &= test_imports()
    success &= test_app_creation()

    if success:
        print("\n✅ All tests passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Fix issues before deployment.")
        sys.exit(1)
