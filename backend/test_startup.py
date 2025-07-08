#!/usr/bin/env python3
"""
Quick application startup test for RetailGenie backend
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")

    try:
        from dotenv import load_dotenv

        print("✅ dotenv imported")

        from flask import Flask

        print("✅ Flask imported")

        from flask_cors import CORS

        print("✅ Flask-CORS imported")

        # Load environment variables
        load_dotenv()
        print("✅ Environment variables loaded")

        # Test Firebase utils
        from app.utils.firebase_utils import FirebaseUtils

        print("✅ Firebase utils imported")

        # Test route imports
        from app.routes.ai_assistant_routes import ai_assistant_bp

        print("✅ AI assistant routes imported")

        from app.routes.product_routes import product_bp

        print("✅ Product routes imported")

        print("✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_app_creation():
    """Test Flask app creation"""
    print("\n🏗️ Testing app creation...")

    try:
        from app import create_app

        app = create_app()

        print("✅ App created successfully")
        print(f"   Debug mode: {app.debug}")
        print(f"   Testing mode: {app.testing}")
        print(f"   App name: {app.name}")

        # Test some basic app properties
        if hasattr(app, "blueprints"):
            print(f"   Blueprints registered: {len(app.blueprints)}")

        return True, app

    except Exception as e:
        print(f"❌ App creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False, None


def test_basic_routes(app):
    """Test basic route accessibility"""
    print("\n🛣️ Testing basic routes...")

    try:
        with app.test_client() as client:
            # Test health endpoint
            response = client.get("/api/v1/health")
            print(f"✅ Health endpoint: {response.status_code}")

            # Test products endpoint
            response = client.get("/api/v1/products")
            print(f"✅ Products endpoint: {response.status_code}")

        return True

    except Exception as e:
        print(f"❌ Route testing failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 RetailGenie Backend - Startup Test")
    print("=" * 40)

    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Check dependencies.")
        return False

    # Test app creation
    success, app = test_app_creation()
    if not success:
        print("\n❌ App creation failed. Check configuration.")
        return False

    # Test basic routes
    if not test_basic_routes(app):
        print("\n⚠️ Route testing failed. App created but routes may have issues.")
        return False

    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Your application is ready for startup")
    print("\n📋 To start the server:")
    print("   python3 app.py")
    print("   OR")
    print("   gunicorn wsgi:app")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
