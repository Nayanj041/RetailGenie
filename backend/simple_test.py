#!/usr/bin/env python3
"""
Simple Backend Test Script
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, "/workspaces/RetailGenie/backend")


def test_app_creation():
    """Test if we can create the Flask app"""
    try:
        # Import and create the app
        from app import create_app

        app = create_app()

        print("✅ App created successfully")

        # Test the app in test mode
        with app.test_client() as client:
            # Test health endpoint
            response = client.get("/api/v1/health")
            print(f"Health endpoint: {response.status_code} - {response.get_json()}")

            # Test registration endpoint
            test_data = {
                "name": "Test Retailer",
                "email": "test@store.com",
                "password": "test123",
                "business_name": "Test Store",
            }

            response = client.post(
                "/api/v1/auth/register",
                json=test_data,
                headers={"Content-Type": "application/json"},
            )

            print(f"Registration endpoint: {response.status_code}")
            print(f"Response: {response.get_json()}")

            if response.status_code in [200, 201]:
                print("✅ Registration endpoint works!")
            else:
                print("❌ Registration endpoint failed")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Testing RetailGenie Backend")
    print("=" * 40)
    test_app_creation()
