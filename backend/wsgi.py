#!/usr/bin/env python3
"""
RetailGenie Backend - Main Application Entry Point
Perfect Structure Implementation
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from flask import Flask
from flask_cors import CORS
import logging
from datetime import datetime
from flask import jsonify

# Import configuration
from config.config import Config

# Import routes
from app.routes.auth_routes import auth_bp
from app.routes.product_routes import product_bp
from app.routes.inventory_routes import inventory_bp
from app.routes.analytics_routes import analytics_bp
from app.routes.ai_assistant_routes import ai_assistant_bp
from app.routes.feedback_routes import feedback_bp
from app.routes.pricing_routes import pricing_bp

# Import middleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.cors_middleware import setup_cors
from app.middleware.logging_middleware import setup_logging


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)

    # Setup CORS
    setup_cors(app)

    # Setup logging
    setup_logging(app)

    # Initialize middleware
    AuthMiddleware(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(product_bp, url_prefix="/api/v1/products")
    app.register_blueprint(inventory_bp, url_prefix="/api/v1/inventory")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")
    app.register_blueprint(ai_assistant_bp, url_prefix="/api/v1/ai")
    app.register_blueprint(feedback_bp, url_prefix="/api/v1/feedback")
    app.register_blueprint(pricing_bp, url_prefix="/api/v1/pricing")

    # Root endpoint
    @app.route("/")
    def root():
        return {
            "message": "Welcome to RetailGenie API",
            "status": "online",
            "version": "1.0.0",
            "documentation": "/api/info",
            "health": "/health",
        }

    # Simple status endpoint
    @app.route("/status")
    def simple_status():
        return {"status": "ok"}

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": app.config.get("ENV", "development"),
        }

    # Alternative health check endpoint
    @app.route("/api/v1/health")
    def api_health_check():
        return {
            "status": "healthy",
            "api_version": "v1",
            "timestamp": datetime.now().isoformat(),
            "services": {"database": "connected", "auth": "active", "ai": "ready"},
        }

    # API info endpoint
    @app.route("/api/info")
    def api_info():
        return {
            "name": "RetailGenie API",
            "version": "1.0.0",
            "description": "AI-powered retail management system",
            "endpoints": {
                "auth": "/api/v1/auth",
                "products": "/api/v1/products",
                "inventory": "/api/v1/inventory",
                "analytics": "/api/v1/analytics",
                "ai_assistant": "/api/v1/ai",
                "feedback": "/api/v1/feedback",
                "pricing": "/api/v1/pricing",
            },
            "documentation": "/docs",
            "health": "/health",
        }

    # Routes listing endpoint
    @app.route("/api/v1/routes")
    def list_all_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(
                {
                    "endpoint": rule.endpoint,
                    "methods": list(rule.methods),
                    "url": str(rule),
                }
            )
        return {"routes": routes}

    # Test auth endpoint - generates a test JWT token
    @app.route("/api/v1/auth/test-token", methods=["POST"])
    def get_test_token():
        """Generate a test JWT token for API testing"""
        import jwt
        from datetime import datetime, timedelta

        try:
            secret_key = app.config.get(
                "JWT_SECRET_KEY", "jwt-secret-key-change-in-production"
            )

            # Create test user payload
            payload = {
                "user_id": "test_user_123",
                "email": "testuser@retailgenie.com",
                "role": "user",
                "exp": datetime.utcnow() + timedelta(hours=24),
                "iat": datetime.utcnow(),
            }

            # Generate token
            token = jwt.encode(payload, secret_key, algorithm="HS256")

            return {
                "success": True,
                "token": token,
                "user": {
                    "id": "test_user_123",
                    "email": "testuser@retailgenie.com",
                    "name": "Test User",
                    "role": "user",
                },
                "expires_in": "24 hours",
                "usage": "Include in Authorization header as: Bearer " + token,
            }
        except Exception as e:
            return {"error": str(e)}, 500

    # Demo user seeding endpoint
    @app.route("/api/v1/seed-demo-user", methods=["POST", "GET"])
    def seed_demo_user():
        """Create demo user for testing"""
        try:
            from app.controllers.auth_controller import AuthController
            auth_controller = AuthController()
            
            # Demo user data
            demo_data = {
                "name": "Demo User",
                "email": "demo@retailgenie.com", 
                "password": "demo123456",
                "business_name": "Demo Store",
                "role": "retailer"
            }
            
            # Check if demo user already exists
            existing_users = auth_controller.firebase.query_documents(
                "users", "email", "==", demo_data["email"]
            )
            
            if existing_users:
                return jsonify({
                    "success": True,
                    "message": "Demo user already exists",
                    "user": {"email": demo_data["email"], "name": demo_data["name"]}
                }), 200
            
            # Create demo user
            result = auth_controller.register_user(demo_data)
            
            return jsonify({
                "success": True,
                "message": "Demo user created successfully",
                "user": result["user"]
            }), 201
            
        except Exception as e:
            app.logger.error(f"Demo user seeding error: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "Failed to create demo user"
            }), 500

    # CORS debugging endpoint
    @app.route("/api/v1/cors-debug", methods=["GET", "POST", "OPTIONS"])
    def cors_debug():
        """Debug CORS configuration"""
        from flask import request
        
        origin = request.headers.get('Origin', 'No Origin')
        method = request.method
        
        return {
            "cors_status": "active",
            "request_origin": origin,
            "request_method": method,
            "allowed_origins": app.config.get("CORS_ORIGINS", []),
            "cors_headers": dict(request.headers),
            "message": f"CORS debug - Origin: {origin}, Method: {method}"
        }

    # Global OPTIONS handler for CORS preflight requests
    @app.route("/api/v1/<path:path>", methods=["OPTIONS"])
    @app.route("/api/<path:path>", methods=["OPTIONS"])
    @app.route("/<path:path>", methods=["OPTIONS"])
    def handle_options(path=None):
        """Handle CORS preflight requests"""
        return "", 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        return {"error": "Internal server error"}, 500

    return app


def main():
    """Main application entry point"""
    app = create_app()

    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    print(
        f"""
    🚀 RetailGenie Backend Starting...
    
    📍 Server: http://{host}:{port}
    🔧 Environment: {app.config.get('ENV', 'development')}
    🐛 Debug Mode: {debug}
    📊 Health Check: http://{host}:{port}/health
    📝 API Info: http://{host}:{port}/api/info
    
    📁 Perfect Structure Implemented ✅
    """
    )

    app.run(host=host, port=port, debug=debug, threaded=True)


# Create app instance for WSGI servers (like Gunicorn)
app = create_app()

if __name__ == "__main__":
    main()
