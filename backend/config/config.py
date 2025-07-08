"""
RetailGenie Backend Configuration
Perfect Structure Implementation
"""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base configuration class"""

    # Basic Flask configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1", "yes"]
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # API Configuration
    API_VERSION = '1.0.0'
    API_TITLE = 'RetailGenie API'
    API_DESCRIPTION = 'AI-powered retail management system'

    # JWT Configuration
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")

    # Email Configuration
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@retailgenie.com")

    # Google Gemini Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-pro")

    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")

    # PDF Reports Configuration
    PDF_OUTPUT_DIR = os.environ.get("PDF_OUTPUT_DIR", "reports")

    # CORS Configuration
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,https://retailgenie-1.onrender.com").split(",")

    # Pagination Configuration
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # Cache Configuration
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "simple")
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

    # Logging Configuration
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "app.log")

    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    RATELIMIT_DEFAULT = "100 per hour"

    # Security Configuration
    SESSION_COOKIE_SECURE = os.environ.get(
        "SESSION_COOKIE_SECURE", "False"
    ).lower() in ["true", "1", "yes"]
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # API Configuration
    API_VERSION = "v1"
    API_TITLE = "RetailGenie API"
    API_DESCRIPTION = "AI-powered retail management system"

    # Business Rules Configuration
    MIN_RATING = 1
    MAX_RATING = 5
    LOW_STOCK_THRESHOLD = 10
    LOW_RATING_THRESHOLD = 2

    # AI Configuration
    MAX_SEARCH_RESULTS = 50
    MAX_RECOMMENDATIONS = 15
    SENTIMENT_THRESHOLD = 0.5


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "https://retailgenie-1.onrender.com"]


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SESSION_COOKIE_SECURE = True

    # Override any production-specific settings
    LOG_LEVEL = "WARNING"
    RATELIMIT_DEFAULT = "1000 per hour"


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True

    # Use in-memory database for testing
    FIREBASE_CREDENTIALS_PATH = None

    # Disable email sending in tests
    SENDER_EMAIL = None

    # Use faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])


# Environment variables documentation
ENV_VARS_DOCUMENTATION = """
Required Environment Variables:
===============================

Core Configuration:
- SECRET_KEY: Flask secret key for sessions
- JWT_SECRET_KEY: JWT token signing key
- FLASK_ENV: Environment (development/production/testing)

Firebase Configuration:
- FIREBASE_CREDENTIALS_PATH: Path to Firebase service account JSON file
- FIREBASE_PROJECT_ID: Firebase project ID

Email Configuration:
- SMTP_SERVER: SMTP server address (default: smtp.gmail.com)
- SMTP_PORT: SMTP server port (default: 587)
- SENDER_EMAIL: Email address for sending notifications
- SENDER_PASSWORD: Password or app password for sender email
- ADMIN_EMAIL: Admin email for notifications

AI Configuration:
- GEMINI_API_KEY: Google Gemini API key for AI features

Optional Configuration:
- CORS_ORIGINS: Comma-separated list of allowed origins
- LOG_LEVEL: Logging level (DEBUG/INFO/WARNING/ERROR)
- UPLOAD_FOLDER: Directory for file uploads
- PDF_OUTPUT_DIR: Directory for PDF reports
- REDIS_URL: Redis URL for rate limiting (optional)

Example .env file:
==================
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=development

FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
FIREBASE_PROJECT_ID=your-firebase-project

SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
ADMIN_EMAIL=admin@yourcompany.com

GEMINI_API_KEY=your-gemini-api-key

CORS_ORIGINS=http://localhost:3000,https://yourfrontend.com
"""

if __name__ == "__main__":
    print(ENV_VARS_DOCUMENTATION)
