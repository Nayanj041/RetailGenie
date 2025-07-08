"""
CORS Middleware Configuration
Perfect Structure Implementation
"""

from flask_cors import CORS


def setup_cors(app):
    """Configure CORS for the Flask application"""

    # Get allowed origins from config
    origins = app.config.get("CORS_ORIGINS", ["*"])

    # Configure CORS
    CORS(
        app,
        origins=origins,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        supports_credentials=True,
        max_age=86400,  # 24 hours
    )

    app.logger.info(f"CORS configured with origins: {origins}")

    return app
