#!/usr/bin/env python3
"""
RetailGenie Backend - Main Application Entry Point
Perfect Structure Implementation
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
current_dir = Path(__file__).parent
app_dir = current_dir / "app"
sys.path.insert(0, str(app_dir))

from flask import Flask
from flask_cors import CORS
import logging
from datetime import datetime

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
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(product_bp, url_prefix='/api/v1/products')
    app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    app.register_blueprint(ai_assistant_bp, url_prefix='/api/v1/ai')
    app.register_blueprint(feedback_bp, url_prefix='/api/v1/feedback')
    app.register_blueprint(pricing_bp, url_prefix='/api/v1/pricing')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': app.config.get('ENV', 'development')
        }
    
    # API info endpoint
    @app.route('/api/info')
    def api_info():
        return {
            'name': 'RetailGenie API',
            'version': '1.0.0',
            'description': 'AI-powered retail management system',
            'endpoints': {
                'auth': '/api/v1/auth',
                'products': '/api/v1/products',
                'inventory': '/api/v1/inventory',
                'analytics': '/api/v1/analytics',
                'ai_assistant': '/api/v1/ai',
                'feedback': '/api/v1/feedback',
                'pricing': '/api/v1/pricing'
            },
            'documentation': '/docs',
            'health': '/health'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal server error'}, 500
    
    return app

def main():
    """Main application entry point"""
    app = create_app()
    
    # Get configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    🚀 RetailGenie Backend Starting...
    
    📍 Server: http://{host}:{port}
    🔧 Environment: {app.config.get('ENV', 'development')}
    🐛 Debug Mode: {debug}
    📊 Health Check: http://{host}:{port}/health
    📝 API Info: http://{host}:{port}/api/info
    
    📁 Perfect Structure Implemented ✅
    """)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()
