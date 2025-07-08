#!/usr/bin/env python3
"""
RetailGenie Database Status and Management Tool
Checks database connectivity, collections, and provides initialization options
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_database_status():
    """Check the current status of the RetailGenie database"""
    print("🗄️ RetailGenie Database Status Check")
    print("=" * 40)

    try:
        # Import Firebase utils
        from app.utils.firebase_utils import FirebaseUtils

        print("✅ Firebase utils imported successfully")

        # Initialize Firebase
        firebase = FirebaseUtils()

        # Check if we're using real Firebase or mock
        if hasattr(firebase, "db") and firebase.db is not None:
            print("✅ Connected to Firebase Firestore")
            db = firebase.db

            # List all collections
            collections = list(db.collections())
            print(f"📊 Total collections: {len(collections)}")

            if collections:
                print("\n📁 Existing Collections:")
                for collection in collections:
                    try:
                        # Count documents in each collection
                        docs = list(collection.limit(10).stream())
                        print(f"   📂 {collection.id}: {len(docs)} documents")

                        # Show sample data from first document
                        if docs:
                            sample_doc = docs[0].to_dict()
                            sample_keys = list(sample_doc.keys())[:3]  # First 3 keys
                            print(f"      Sample fields: {sample_keys}")
                    except Exception as e:
                        print(f"   ❌ {collection.id}: Error reading - {str(e)}")
            else:
                print("📝 Database is empty - ready for initialization")

            # Check specific RetailGenie collections
            print("\n🎯 RetailGenie Collections Status:")
            expected_collections = [
                "products",
                "customers",
                "orders",
                "analytics",
                "feedback",
                "inventory",
                "users",
                "sales",
            ]

            for col_name in expected_collections:
                try:
                    collection_ref = db.collection(col_name)
                    docs = list(collection_ref.limit(1).stream())
                    if docs:
                        total_docs = len(list(collection_ref.stream()))
                        print(f"   📂 {col_name}: {total_docs} documents")
                    else:
                        print(f"   📁 {col_name}: Empty")
                except Exception as e:
                    print(f"   ❌ {col_name}: Error - {str(e)}")

            # Test basic database operations
            print("\n🧪 Testing Database Operations:")

            # Test write
            test_doc_ref = db.collection("system_tests").document("connectivity_test")
            test_data = {
                "timestamp": datetime.now().isoformat(),
                "test_type": "database_status_check",
                "status": "success",
            }
            test_doc_ref.set(test_data)
            print("   ✅ Write operation: Success")

            # Test read
            doc = test_doc_ref.get()
            if doc.exists:
                print("   ✅ Read operation: Success")
            else:
                print("   ❌ Read operation: Failed")

            # Test delete (cleanup)
            test_doc_ref.delete()
            print("   ✅ Delete operation: Success")

            print("\n🎉 Database is fully functional!")
            return True

        else:
            print("⚠️ Using mock database - Firebase not properly configured")
            print("   Check your Firebase credentials and project settings")
            return False

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def initialize_sample_data():
    """Initialize the database with sample data for testing"""
    print("\n🚀 Initializing Sample Data")
    print("=" * 30)

    try:
        from app.utils.firebase_utils import FirebaseUtils

        firebase = FirebaseUtils()

        if not hasattr(firebase, "db") or firebase.db is None:
            print("❌ Cannot initialize - database not connected")
            return False

        db = firebase.db

        # Sample products
        sample_products = [
            {
                "id": "prod_001",
                "name": "Premium Coffee Beans",
                "category": "Beverages",
                "price": 24.99,
                "stock_quantity": 150,
                "description": "High-quality arabica coffee beans",
                "created_at": datetime.now().isoformat(),
                "status": "active",
            },
            {
                "id": "prod_002",
                "name": "Organic Tea Set",
                "category": "Beverages",
                "price": 34.99,
                "stock_quantity": 75,
                "description": "Organic herbal tea collection",
                "created_at": datetime.now().isoformat(),
                "status": "active",
            },
            {
                "id": "prod_003",
                "name": "Artisan Chocolate",
                "category": "Food",
                "price": 15.99,
                "stock_quantity": 200,
                "description": "Handcrafted dark chocolate bars",
                "created_at": datetime.now().isoformat(),
                "status": "active",
            },
        ]

        # Add products
        for product in sample_products:
            db.collection("products").document(product["id"]).set(product)
            print(f"   ✅ Added product: {product['name']}")

        # Sample customers
        sample_customers = [
            {
                "id": "cust_001",
                "name": "John Smith",
                "email": "john.smith@example.com",
                "phone": "+1-555-0123",
                "loyalty_points": 250,
                "total_orders": 12,
                "created_at": datetime.now().isoformat(),
                "status": "active",
            },
            {
                "id": "cust_002",
                "name": "Sarah Johnson",
                "email": "sarah.j@example.com",
                "phone": "+1-555-0456",
                "loyalty_points": 180,
                "total_orders": 8,
                "created_at": datetime.now().isoformat(),
                "status": "active",
            },
        ]

        # Add customers
        for customer in sample_customers:
            db.collection("customers").document(customer["id"]).set(customer)
            print(f"   ✅ Added customer: {customer['name']}")

        # Sample analytics data
        analytics_data = {
            "daily_stats": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_sales": 1245.67,
                "total_orders": 23,
                "new_customers": 3,
                "top_product": "Premium Coffee Beans",
                "generated_at": datetime.now().isoformat(),
            }
        }

        db.collection("analytics").document("daily_summary").set(analytics_data)
        print("   ✅ Added analytics data")

        print("\n🎉 Sample data initialization complete!")
        print("📊 Database now contains sample products, customers, and analytics")
        return True

    except Exception as e:
        print(f"❌ Sample data initialization failed: {e}")
        return False


def main():
    """Main function"""
    print("🗄️ RetailGenie Database Management")
    print("=" * 50)

    # Check database status
    db_status = check_database_status()

    if db_status:
        print("\n" + "=" * 50)
        response = input("🤔 Would you like to initialize sample data? (y/N): ")

        if response.lower() in ["y", "yes"]:
            initialize_sample_data()
        else:
            print("✅ Skipping sample data initialization")

    print("\n📋 Database Management Complete!")
    print("🚀 Your RetailGenie database is ready for use")


if __name__ == "__main__":
    main()
