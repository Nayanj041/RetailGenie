#!/usr/bin/env python3
"""
Simple Firebase Configuration Test
Tests the Firebase credentials and connection
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def test_firebase_config():
    """Test Firebase configuration and connection"""
    print("🔥 Firebase Configuration Test")
    print("=" * 40)

    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✅ Loaded .env file")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")

    # Check Firebase environment variables
    firebase_vars = {
        "FIREBASE_PROJECT_ID": "Firebase Project ID",
        "FIREBASE_PRIVATE_KEY_ID": "Firebase Private Key ID",
        "FIREBASE_PRIVATE_KEY": "Firebase Private Key",
        "FIREBASE_CLIENT_EMAIL": "Firebase Client Email",
        "FIREBASE_CLIENT_ID": "Firebase Client ID",
    }

    print("\n📋 Firebase Environment Variables:")
    all_set = True
    for var, description in firebase_vars.items():
        value = os.getenv(var, "")
        if not value:
            print(f"❌ {var}: Not set - {description}")
            all_set = False
        else:
            # Mask sensitive values
            if "KEY" in var and len(value) > 20:
                masked_value = value[:15] + "..." + value[-10:]
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")

    if not all_set:
        print("\n❌ Some Firebase variables are missing!")
        return False

    # Test Firebase Admin SDK initialization
    print("\n🔧 Testing Firebase Admin SDK:")
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Check if Firebase app is already initialized
        try:
            app = firebase_admin.get_app()
            print("✅ Firebase app already initialized")
        except ValueError:
            # Initialize Firebase Admin SDK
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv(
                    "FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
                ),
                "token_uri": os.getenv(
                    "FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"
                ),
            }

            cred = credentials.Certificate(cred_dict)
            app = firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized successfully")

        # Test Firestore connection
        db = firestore.client()
        print("✅ Firestore client created successfully")

        # Test a simple operation (list collections)
        collections = list(db.collections())
        print(f"✅ Firestore connection working - Found {len(collections)} collections")

        return True

    except ImportError as e:
        print(f"❌ Firebase Admin SDK not installed: {e}")
        print("   Install with: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return False


def main():
    """Run Firebase configuration test"""
    print("🚀 RetailGenie Firebase Test")
    print("=" * 50)

    success = test_firebase_config()

    print(f"\n📊 Test Result:")
    if success:
        print("🎉 Firebase configuration is working correctly!")
        print("\n✅ Your Firebase setup is ready for production use.")
        print("✅ You can now start the RetailGenie backend application.")
    else:
        print("❌ Firebase configuration has issues that need to be resolved.")
        print("\n📚 Check the troubleshooting guide:")
        print("   docs/ENVIRONMENT_VARIABLES_GUIDE.md#firebase-configuration")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
