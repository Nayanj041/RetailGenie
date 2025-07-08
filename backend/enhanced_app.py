#!/usr/bin/env python3
"""
Enhanced RetailGenie Backend App
Includes core functionality without problematic imports
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load environment variables
load_dotenv()


def create_enhanced_app():
    """Create an enhanced Flask app with RetailGenie functionality"""
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
    app.config["DEBUG"] = False

    # Enable CORS
    CORS(app)

    # Sample data for demonstration
    sample_products = [
        {
            "id": "prod_001",
            "name": "Premium Coffee Beans",
            "category": "Beverages",
            "price": 24.99,
            "stock": 150,
            "description": "High-quality arabica coffee beans",
            "status": "active",
        },
        {
            "id": "prod_002",
            "name": "Organic Tea Set",
            "category": "Beverages",
            "price": 34.99,
            "stock": 75,
            "description": "Organic herbal tea collection",
            "status": "active",
        },
        {
            "id": "prod_003",
            "name": "Artisan Chocolate",
            "category": "Food",
            "price": 15.99,
            "stock": 200,
            "description": "Handcrafted dark chocolate bars",
            "status": "active",
        },
    ]

    sample_customers = [
        {
            "id": "cust_001",
            "name": "John Smith",
            "email": "john.smith@example.com",
            "loyalty_points": 250,
            "total_orders": 12,
            "status": "active",
        },
        {
            "id": "cust_002",
            "name": "Sarah Johnson",
            "email": "sarah.j@example.com",
            "loyalty_points": 180,
            "total_orders": 8,
            "status": "active",
        },
    ]

    # Health endpoint
    @app.route("/api/v1/health")
    def health():
        return jsonify(
            {
                "status": "healthy",
                "message": "RetailGenie Backend is running",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "features": ["products", "customers", "analytics", "orders"],
            }
        )

    # Products endpoints
    @app.route("/api/v1/products", methods=["GET"])
    def get_products():
        return jsonify(
            {
                "success": True,
                "data": sample_products,
                "total": len(sample_products),
                "message": "Products retrieved successfully",
            }
        )

    @app.route("/api/v1/products/<product_id>", methods=["GET"])
    def get_product(product_id):
        product = next((p for p in sample_products if p["id"] == product_id), None)
        if product:
            return jsonify(
                {"success": True, "data": product, "message": "Product found"}
            )
        else:
            return jsonify({"success": False, "error": "Product not found"}), 404

    # Customers endpoints
    @app.route("/api/v1/customers", methods=["GET"])
    def get_customers():
        return jsonify(
            {
                "success": True,
                "data": sample_customers,
                "total": len(sample_customers),
                "message": "Customers retrieved successfully",
            }
        )

    @app.route("/api/v1/customers/<customer_id>", methods=["GET"])
    def get_customer(customer_id):
        customer = next((c for c in sample_customers if c["id"] == customer_id), None)
        if customer:
            return jsonify(
                {"success": True, "data": customer, "message": "Customer found"}
            )
        else:
            return jsonify({"success": False, "error": "Customer not found"}), 404

    # Analytics endpoint
    @app.route("/api/v1/analytics/dashboard", methods=["GET"])
    def get_dashboard_analytics():
        analytics = {
            "total_products": len(sample_products),
            "total_customers": len(sample_customers),
            "total_revenue": 15678.90,
            "total_orders": 157,
            "average_order_value": 99.86,
            "growth_metrics": {
                "revenue_growth": 15.2,
                "customer_growth": 8.7,
                "order_growth": 12.1,
            },
            "top_products": [
                {"name": "Premium Coffee Beans", "sales": 2345.67},
                {"name": "Organic Tea Set", "sales": 1876.32},
            ],
            "generated_at": datetime.now().isoformat(),
        }

        return jsonify(
            {
                "success": True,
                "data": analytics,
                "message": "Dashboard analytics retrieved",
            }
        )

    # Orders endpoint
    @app.route("/api/v1/orders", methods=["GET"])
    def get_orders():
        sample_orders = [
            {
                "id": "order_001",
                "customer_id": "cust_001",
                "customer_name": "John Smith",
                "total": 59.98,
                "status": "completed",
                "items": [
                    {
                        "product_id": "prod_001",
                        "name": "Premium Coffee Beans",
                        "quantity": 2,
                        "price": 24.99,
                    },
                    {
                        "product_id": "prod_003",
                        "name": "Artisan Chocolate",
                        "quantity": 1,
                        "price": 15.99,
                    },
                ],
                "created_at": "2025-07-01T10:30:00Z",
            },
            {
                "id": "order_002",
                "customer_id": "cust_002",
                "customer_name": "Sarah Johnson",
                "total": 34.99,
                "status": "pending",
                "items": [
                    {
                        "product_id": "prod_002",
                        "name": "Organic Tea Set",
                        "quantity": 1,
                        "price": 34.99,
                    }
                ],
                "created_at": "2025-07-02T14:15:00Z",
            },
        ]

        return jsonify(
            {
                "success": True,
                "data": sample_orders,
                "total": len(sample_orders),
                "message": "Orders retrieved successfully",
            }
        )

    # Inventory endpoint
    @app.route("/api/v1/inventory", methods=["GET"])
    def get_inventory():
        inventory = []
        for product in sample_products:
            inventory.append(
                {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "current_stock": product["stock"],
                    "reorder_level": 20,
                    "status": "in_stock" if product["stock"] > 20 else "low_stock",
                    "last_updated": datetime.now().isoformat(),
                }
            )

        return jsonify(
            {
                "success": True,
                "data": inventory,
                "total": len(inventory),
                "message": "Inventory retrieved successfully",
            }
        )

    # AI chat endpoint (mock response since Gemini API is expired)
    @app.route("/api/v1/ai/chat", methods=["POST"])
    def ai_chat():
        try:
            data = request.get_json()
            user_message = data.get("message", "") if data else ""

            # Mock AI responses
            ai_responses = [
                f"I understand you're asking about: '{user_message}'. Based on your RetailGenie data, I can help you with product recommendations, sales analysis, and inventory management.",
                f"Regarding '{user_message}', I suggest checking your top-selling products: Premium Coffee Beans and Organic Tea Set are performing well this month.",
                f"For '{user_message}', here's what I found in your analytics: Total revenue is $15,678.90 with 157 orders. Your customer retention rate is strong at 75%.",
                "I'm your RetailGenie AI assistant! I can help with inventory management, sales analytics, customer insights, and business recommendations. What would you like to know?",
            ]

            import random

            response = random.choice(ai_responses)

            return jsonify(
                {
                    "success": True,
                    "data": {
                        "response": response,
                        "user_message": user_message,
                        "timestamp": datetime.now().isoformat(),
                        "ai_model": "RetailGenie Assistant (Demo Mode)",
                    },
                    "message": "AI response generated successfully",
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": f"AI chat error: {str(e)}"}), 500

    # API routes listing
    @app.route("/api/v1/routes", methods=["GET"])
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != "static":
                routes.append(
                    {
                        "endpoint": rule.endpoint,
                        "methods": list(rule.methods - {"HEAD", "OPTIONS"}),
                        "url": str(rule),
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": routes,
                "total": len(routes),
                "message": "Available API routes",
            }
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Endpoint not found",
                    "message": "The requested URL was not found. Use /api/v1/routes to see available endpoints.",
                    "available_endpoints": [
                        "/api/v1/health",
                        "/api/v1/products",
                        "/api/v1/customers",
                        "/api/v1/orders",
                        "/api/v1/inventory",
                        "/api/v1/analytics/dashboard",
                        "/api/v1/ai/chat",
                        "/api/v1/routes",
                    ],
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                }
            ),
            500,
        )

    return app


def main():
    """Main function to run the enhanced app"""
    print("🚀 RetailGenie Enhanced Backend")
    print("=" * 35)
    print("Starting enhanced backend with full API functionality...")

    app = create_enhanced_app()

    print("✅ Enhanced app created successfully")
    print("🌐 Available endpoints:")
    print("   • GET  /api/v1/health")
    print("   • GET  /api/v1/products")
    print("   • GET  /api/v1/customers")
    print("   • GET  /api/v1/orders")
    print("   • GET  /api/v1/inventory")
    print("   • GET  /api/v1/analytics/dashboard")
    print("   • POST /api/v1/ai/chat")
    print("   • GET  /api/v1/routes")
    print("")
    print("🌐 Server starting on http://localhost:5000")
    print("📋 Use /api/v1/routes to see all available endpoints")

    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
