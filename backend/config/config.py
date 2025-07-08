"""
RetailGenie Backend Configuration
Production-ready configuration for Render deployment with proper CORS settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BaseConfig:
    """Base configuration with common settings"""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-jwt-secret-change-in-production")

    # Firebase configuration
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "retailgenie-demo")
    FIREBASE_PRIVATE_KEY_ID = os.environ.get("FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY = os.environ.get("FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL = os.environ.get("FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID = os.environ.get("FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_URI = os.environ.get(
        "FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
    )
    FIREBASE_TOKEN_URI = os.environ.get(
        "FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"
    )
    FIREBASE_CLIENT_CERT_URL = os.environ.get("FIREBASE_CLIENT_CERT_URL")

    # API settings
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"

    # CORS settings - Include all necessary origins for production
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://retailgenie-1.onrender.com",  # Render frontend  # Another potential frontend URL
    ]

    # Additional CORS from environment (comma-separated)
    env_cors = os.environ.get("CORS_ORIGINS", "")
    if env_cors:
        CORS_ORIGINS.extend(
            [origin.strip() for origin in env_cors.split(",") if origin.strip()]
        )

    # Remove duplicates while preserving order
    CORS_ORIGINS = list(dict.fromkeys(CORS_ORIGINS))

    # Security settings
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Methods",
    ]
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

    # Database settings
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # ML/AI settings
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")

    # Session settings
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    DEBUG = True
    TESTING = False

    # Keep all CORS origins for development (don't override)
    # This ensures local development works with Render backend


class ProductionConfig(BaseConfig):
    """Production configuration for Render deployment"""

    DEBUG = False
    TESTING = False

    # Production security
    SESSION_COOKIE_SECURE = True

    # Production logging
    LOG_LEVEL = "WARNING"

    # Ensure production secrets are set
    def __init__(self):
        super().__init__()
        if self.SECRET_KEY == "dev-secret-key-change-in-production":
            print("⚠️  WARNING: Using default SECRET_KEY in production!")
        if self.JWT_SECRET == "dev-jwt-secret-change-in-production":
            print("⚠️  WARNING: Using default JWT_SECRET in production!")


class TestingConfig(BaseConfig):
    """Testing configuration"""

    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

    # Use in-memory database for testing
    DATABASE_URL = "sqlite:///:memory:"


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config.get(env, config["default"])


# For direct import
Config = get_config()

# Debug information
if __name__ == "__main__":
    print("RetailGenie Configuration")
    print("=" * 50)
    current_config = get_config()()
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug: {current_config.DEBUG}")
    print(f"CORS Origins: {current_config.CORS_ORIGINS}")
    print(f"API Prefix: {current_config.API_PREFIX}")
    print(f"Firebase Project: {current_config.FIREBASE_PROJECT_ID}")
