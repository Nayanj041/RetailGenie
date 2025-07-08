"""
Logging Middleware Configuration
Perfect Structure Implementation
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(app):
    """Configure comprehensive logging for the Flask application"""

    # Get log level from config
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper())

    # Create logs directory
    log_dir = Path(__file__).parent.parent.parent / "monitoring" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=10240000, backupCount=5  # 10MB
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s [%(pathname)s:%(lineno)d]: %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to app logger
    app.logger.handlers.clear()
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)

    # Request logging middleware
    @app.before_request
    def log_request_info():
        from flask import request

        app.logger.info(
            f"Request: {request.method} {request.url} - IP: {request.remote_addr}"
        )

    @app.after_request
    def log_response_info(response):
        from flask import request

        app.logger.info(
            f"Response: {request.method} {request.url} - Status: {response.status_code}"
        )
        return response

    app.logger.info("Logging middleware configured successfully")

    return app
