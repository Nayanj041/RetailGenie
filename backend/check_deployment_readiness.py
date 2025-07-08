#!/usr/bin/env python3
"""
RetailGenie Backend Deployment Readiness Check
Comprehensive validation for production deployment
"""

import os
import sys
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")


def print_section(title):
    """Print a section header"""
    print(f"\n🔍 {title}")
    print("-" * 50)


def check_environment_variables():
    """Check all required environment variables"""
    print_section("Environment Variables Check")

    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✅ Loaded .env file")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    except Exception as e:
        print(f"❌ Could not load .env file: {e}")
        return False

    # Critical variables for deployment
    critical_vars = {
        "SECRET_KEY": "Flask secret key for security",
        "JWT_SECRET": "JWT secret for authentication",
        "FIREBASE_PROJECT_ID": "Firebase project identifier",
        "FIREBASE_PRIVATE_KEY": "Firebase service account private key",
        "FIREBASE_CLIENT_EMAIL": "Firebase service account email",
        "GEMINI_API_KEY": "Google Gemini API key for AI features",
    }

    # Optional but recommended variables
    optional_vars = {
        "CORS_ORIGINS": "CORS allowed origins",
        "SMTP_SERVER": "Email server configuration",
        "REDIS_URL": "Redis connection for caching",
    }

    all_critical_set = True

    print("\n📋 Critical Variables (Required for deployment):")
    for var, description in critical_vars.items():
        value = os.getenv(var, "")
        if not value or value.startswith("your-"):
            print(f"❌ {var}: Missing - {description}")
            all_critical_set = False
        else:
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var:
                if len(value) > 15:
                    masked_value = value[:8] + "..." + value[-4:]
                else:
                    masked_value = "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")

    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var, "")
        if not value or value.startswith("your-"):
            print(f"⚠️  {var}: Not configured - {description}")
        else:
            print(f"✅ {var}: {value}")

    return all_critical_set


def check_dependencies():
    """Check Python dependencies"""
    print_section("Python Dependencies Check")

    required_packages = [
        "flask",
        "google.generativeai",
        "firebase_admin",
        "python_dotenv",
        "werkzeug",
        "flask_cors",
        "requests",
    ]

    optional_packages = ["redis", "celery", "pytest"]

    all_required = True

    print("\n📦 Required Packages:")
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            all_required = False

    print("\n📦 Optional Packages:")
    for package in optional_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️  {package} - not installed")

    return all_required


def check_firebase_connection():
    """Test Firebase connection"""
    print_section("Firebase Connection Test")

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Check if already initialized
        try:
            app = firebase_admin.get_app()
            print("✅ Firebase app already initialized")
        except ValueError:
            # Initialize Firebase
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace(
                    "\\n", "\n"
                ),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv(
                    "FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"
                ),
                "token_uri": os.getenv(
                    "FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"
                ),
            }

            # Validate required fields
            required_fields = ["project_id", "private_key", "client_email"]
            for field in required_fields:
                if not cred_dict.get(field):
                    print(f"❌ Missing Firebase credential: {field}")
                    return False

            cred = credentials.Certificate(cred_dict)
            app = firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized")

        # Test Firestore connection
        db = firestore.client()
        collections = list(db.collections())
        print(f"✅ Firestore connection working - {len(collections)} collections found")

        return True

    except ImportError:
        print("❌ Firebase Admin SDK not installed")
        return False
    except Exception as e:
        print(f"❌ Firebase connection failed: {str(e)}")
        return False


def check_gemini_api():
    """Test Gemini API connection"""
    print_section("Gemini API Test")

    try:
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not configured")
            return False

        genai.configure(api_key=api_key)

        # Test with gemini-1.5-flash model
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)

        response = model.generate_content(
            "Say 'API test successful' if you can read this."
        )
        print(f"✅ Gemini API working - Response: {response.text.strip()}")
        return True

    except ImportError:
        print("❌ google-generativeai package not installed")
        return False
    except Exception as e:
        print(f"❌ Gemini API test failed: {str(e)}")
        print("   Check API key validity and quota limits")
        return False


def check_app_structure():
    """Check application file structure"""
    print_section("Application Structure Check")

    required_files = [
        "app.py",
        "requirements.txt",
        "wsgi.py",
        ".env",
        "app/__init__.py",
        "app/routes/",
        "app/controllers/",
        "app/utils/",
        "config/config.py",
    ]

    all_present = True

    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                print(f"✅ Directory: {file_path}")
            else:
                print(f"✅ File: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_present = False

    return all_present


def check_deployment_files():
    """Check deployment configuration files"""
    print_section("Deployment Files Check")

    deployment_files = {
        "Dockerfile": "Docker containerization",
        "docker-compose.yml": "Docker Compose configuration",
        "render.yaml": "Render.com deployment",
        "deployment/Procfile": "Process file for cloud platforms",
        "requirements.txt": "Python dependencies",
    }

    for file_path, description in deployment_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path} - {description}")
        else:
            print(f"⚠️  {file_path} - {description} (optional)")


def check_security_settings():
    """Check security configuration"""
    print_section("Security Settings Check")

    issues = []

    # Check Flask environment
    flask_env = os.getenv("FLASK_ENV", "development")
    flask_debug = os.getenv("FLASK_DEBUG", "True").lower()

    if flask_env == "development":
        print("⚠️  FLASK_ENV=development (change to 'production' for deployment)")
        issues.append("Flask environment is development")
    else:
        print("✅ FLASK_ENV=production")

    if flask_debug == "true":
        print("⚠️  FLASK_DEBUG=True (should be False for production)")
        issues.append("Debug mode enabled")
    else:
        print("✅ FLASK_DEBUG=False")

    # Check secret keys
    secret_key = os.getenv("SECRET_KEY", "")
    if len(secret_key) < 32:
        print("❌ SECRET_KEY too short (should be 32+ characters)")
        issues.append("Weak SECRET_KEY")
    else:
        print("✅ SECRET_KEY is adequately long")

    jwt_secret = os.getenv("JWT_SECRET", "")
    if len(jwt_secret) < 32:
        print("❌ JWT_SECRET too short (should be 32+ characters)")
        issues.append("Weak JWT_SECRET")
    else:
        print("✅ JWT_SECRET is adequately long")

    return len(issues) == 0, issues


def check_app_startup():
    """Test if the app can start"""
    print_section("Application Startup Test")

    try:
        # Import main app
        sys.path.insert(0, ".")
        from app import create_app

        app = create_app()
        print("✅ Flask app created successfully")

        # Check if app has routes
        if app.url_map.rules:
            print(f"✅ App has {len(app.url_map.rules)} routes registered")
        else:
            print("⚠️  No routes found in app")

        return True

    except ImportError as e:
        print(f"❌ Cannot import app: {e}")
        return False
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False


def generate_deployment_report():
    """Generate comprehensive deployment readiness report"""
    print_header("RetailGenie Backend Deployment Readiness Check")

    # Run all checks
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Python Dependencies", check_dependencies),
        ("Firebase Connection", check_firebase_connection),
        ("Gemini API", check_gemini_api),
        ("Application Structure", check_app_structure),
        ("Deployment Files", check_deployment_files),
        ("Application Startup", check_app_startup),
    ]

    results = {}
    security_passed, security_issues = check_security_settings()

    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ {check_name} check failed with error: {e}")
            results[check_name] = False

    # Summary
    print_header("Deployment Readiness Summary")

    passed_checks = sum(results.values())
    total_checks = len(results)

    print(f"\n📊 Overall Score: {passed_checks}/{total_checks} checks passed")

    print(f"\n✅ Passed Checks:")
    for check_name, passed in results.items():
        if passed:
            print(f"   • {check_name}")

    failed_checks = [name for name, passed in results.items() if not passed]
    if failed_checks:
        print(f"\n❌ Failed Checks:")
        for check_name in failed_checks:
            print(f"   • {check_name}")

    if security_issues:
        print(f"\n⚠️  Security Issues:")
        for issue in security_issues:
            print(f"   • {issue}")

    # Deployment readiness assessment
    critical_checks = [
        "Environment Variables",
        "Python Dependencies",
        "Firebase Connection",
        "Gemini API",
    ]
    critical_passed = all(results.get(check, False) for check in critical_checks)

    print(f"\n🚀 Deployment Readiness Assessment:")
    if critical_passed and passed_checks >= total_checks - 1:
        print("🎉 READY FOR DEPLOYMENT!")
        print("   All critical components are working correctly.")
        if security_issues:
            print("   ⚠️  Consider fixing security issues before production deployment.")
    elif critical_passed:
        print("✅ MOSTLY READY")
        print("   Core functionality works, but some optional features may be limited.")
    else:
        print("❌ NOT READY FOR DEPLOYMENT")
        print("   Critical issues need to be resolved first.")

    # Recommendations
    print(f"\n📋 Recommendations:")
    if not critical_passed:
        print("   1. Fix critical component issues (Firebase, Gemini API, etc.)")
    if security_issues:
        print("   2. Address security configuration issues")
        print("   3. Set FLASK_ENV=production and FLASK_DEBUG=False for production")
    if results.get("Deployment Files", True):
        print("   4. Deployment files are ready - choose your deployment platform")

    print(f"\n🔗 Next Steps:")
    print("   • Fix any failed checks listed above")
    print("   • Review security settings for production")
    print("   • Choose deployment platform (Docker, Render, Heroku, etc.)")
    print("   • Set up production environment variables")
    print("   • Configure production database and Redis (if needed)")

    return critical_passed and passed_checks >= total_checks - 1


if __name__ == "__main__":
    ready = generate_deployment_report()
    sys.exit(0 if ready else 1)
