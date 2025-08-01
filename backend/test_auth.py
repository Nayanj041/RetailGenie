#!/usr/bin/env python3
"""
Test script for authentication and Firebase connection
"""

import os
import sys
import json
from datetime import datetime

# Set the Firebase credentials path
os.environ["FIREBASE_CREDENTIALS_PATH"] = (
    "/workspaces/RetailGenie/backend/retailgenie-production-firebase-adminsdk-fbsvc-f1c87b490f.json"
)


def test_firebase_connection():
    """Test Firebase connection"""
    try:
        from app.utils.firebase_utils import FirebaseUtils

        firebase = FirebaseUtils()
        print("✅ Firebase connection successful")
        return firebase
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return None


def test_auth_imports():
    """Test authentication related imports"""
    try:
        import bcrypt
        import jwt

        print("✅ Auth imports successful")
        return True
    except Exception as e:
        print(f"❌ Auth imports failed: {e}")
        return False


def test_user_registration(firebase):
    """Test user registration functionality"""
    try:
        import bcrypt
        import uuid

        # Sample user data
        user_data = {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "name": "Test User",
            "business_name": "Test Business",
            "password": bcrypt.hashpw(
                "testpass123".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            "role": "retailer",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "active": True,
        }

        # Try to create user
        user_id = firebase.create_document("users", user_data)
        print(f"✅ User registration test successful: {user_id}")

        # Clean up test user
        firebase.delete_document("users", user_id)
        print("✅ Test user cleaned up")

        return True
    except Exception as e:
        print(f"❌ User registration test failed: {e}")
        return False


def test_jwt_generation():
    """Test JWT token generation"""
    try:
        import jwt
        from datetime import timedelta

        payload = {
            "user_id": "test123",
            "email": "test@example.com",
            "role": "retailer",
            "exp": datetime.utcnow() + timedelta(hours=24),
        }

        token = jwt.encode(payload, "test-secret", algorithm="HS256")
        decoded = jwt.decode(token, "test-secret", algorithms=["HS256"])

        print("✅ JWT generation and verification successful")
        return True
    except Exception as e:
        print(f"❌ JWT test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Authentication System...")
    print("=" * 50)

    # Test auth imports
    auth_imports_ok = test_auth_imports()

    # Test Firebase connection
    firebase = test_firebase_connection()

    # Test JWT
    jwt_ok = test_jwt_generation()

    # Test registration if Firebase is working
    registration_ok = False
    if firebase:
        registration_ok = test_user_registration(firebase)

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Auth Imports: {'✅' if auth_imports_ok else '❌'}")
    print(f"Firebase Connection: {'✅' if firebase else '❌'}")
    print(f"JWT Generation: {'✅' if jwt_ok else '❌'}")
    print(f"User Registration: {'✅' if registration_ok else '❌'}")

    if all([auth_imports_ok, firebase, jwt_ok, registration_ok]):
        print("\n🎉 All authentication tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)
