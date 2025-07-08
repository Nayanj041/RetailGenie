#!/usr/bin/env python3

# Simple test to identify the issue
print("Starting debug test...")

try:
    print("1. Testing basic imports...")
    import os
    import sys
    from dotenv import load_dotenv

    print("   ✅ Basic imports OK")

    print("2. Loading .env...")
    load_dotenv()
    print("   ✅ .env loaded")

    print("3. Testing Firebase...")
    try:
        from app.utils.firebase_utils import FirebaseUtils

        print("   ✅ Firebase utils imported")

        firebase = FirebaseUtils()
        print("   ✅ Firebase initialized")
    except Exception as e:
        print(f"   ❌ Firebase error: {e}")

    print("4. Testing Flask app creation...")
    from flask import Flask

    app = Flask(__name__)
    print("   ✅ Basic Flask app created")

    print("✅ Basic test completed!")

except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback

    traceback.print_exc()
