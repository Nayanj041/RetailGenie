"""
CORS Middleware Configuration
Perfect Structure Implementation
"""

from flask import request
from flask_cors import CORS


def setup_cors(app):
    """Configure CORS for the Flask application"""

    # Get allowed origins from config
    origins = app.config.get("CORS_ORIGINS", [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://retailgenie-1.onrender.com"
    ])

    # Ensure the frontend domain is always included
    frontend_domain = "https://retailgenie-1.onrender.com"
    if frontend_domain not in origins:
        origins.append(frontend_domain)

    # Configure CORS with comprehensive settings
    CORS(
        app,
        origins=origins,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
        allow_headers=[
            "Content-Type", 
            "Authorization", 
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        expose_headers=[
            "Content-Type",
            "Authorization"
        ],
        supports_credentials=True,
        max_age=86400,  # 24 hours
        send_wildcard=False,
        vary_header=True
    )

    # Add explicit after_request handler for additional CORS headers
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        
        # Only add CORS headers for allowed origins
        if origin in origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin, Access-Control-Request-Method, Access-Control-Request-Headers'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '86400'
            
        return response

    app.logger.info(f"CORS configured with origins: {origins}")

    return app
