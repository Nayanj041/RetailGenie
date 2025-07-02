#!/usr/bin/env python3
"""
Environment Variables Validation Script
Tests all required environment variables and services
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_environment_variables():
    """Test all environment variables are set"""
    print("🔍 Testing Environment Variables")
    print("=" * 40)
    
    required_vars = {
        'SECRET_KEY': 'Flask secret key',
        'JWT_SECRET': 'JWT secret key',
        'FIREBASE_PROJECT_ID': 'Firebase project ID',
        'GEMINI_API_KEY': 'Google Gemini API key',
    }
    
    optional_vars = {
        'SMTP_SERVER': 'Email SMTP server',
        'SENDER_EMAIL': 'Email sender address',
        'REDIS_URL': 'Redis connection URL',
        'CORS_ORIGINS': 'CORS allowed origins',
    }
    
    all_good = True
    
    # Check required variables
    print("\n📋 Required Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var, '')
        if not value or value.startswith('your-'):
            print(f"❌ {var}: Not configured - {description}")
            all_good = False
        else:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    # Check optional variables
    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var, '')
        if not value or value.startswith('your-'):
            print(f"⚠️  {var}: Not configured - {description}")
        else:
            print(f"✅ {var}: {value}")
    
    return all_good

def test_firebase_connection():
    """Test Firebase connection"""
    print("\n🔥 Testing Firebase Connection")
    print("=" * 40)
    
    try:
        from app.utils.firebase_utils import FirebaseManager
        fm = FirebaseManager()
        print("✅ Firebase connection successful!")
        return True
    except Exception as e:
        print(f"❌ Firebase connection failed: {str(e)}")
        return False

def test_gemini_api():
    """Test Gemini API connection"""
    print("\n🤖 Testing Gemini API")
    print("=" * 40)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key.startswith('your-'):
            print("❌ GEMINI_API_KEY not configured")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Test a simple request
        response = model.generate_content("Say 'API connection successful' if you can read this.")
        print(f"✅ Gemini API response: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"❌ Gemini API connection failed: {str(e)}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\n💾 Testing Redis Connection")
    print("=" * 40)
    
    try:
        import redis
        
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        print("   Make sure Redis is installed and running")
        print("   Install: sudo apt install redis-server (Ubuntu)")
        print("   Start: sudo systemctl start redis-server")
        return False

def test_email_configuration():
    """Test email configuration (without sending)"""
    print("\n📧 Testing Email Configuration")
    print("=" * 40)
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        print("⚠️  Email configuration incomplete")
        print("   Missing one or more: SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD")
        return False
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        # Test SMTP connection (without sending)
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(sender_email, sender_password)
        server.quit()
        
        print("✅ Email SMTP connection successful!")
        return True
    except Exception as e:
        print(f"❌ Email SMTP connection failed: {str(e)}")
        print("   Check SMTP credentials and server settings")
        return False

def test_dependencies():
    """Test required Python dependencies"""
    print("\n📦 Testing Python Dependencies")
    print("=" * 40)
    
    required_packages = [
        'flask',
        'google.generativeai',
        'firebase_admin',
        'redis',
        'celery',
        'smtplib',  # Built-in
        'pytest',
    ]
    
    all_good = True
    for package in required_packages:
        try:
            if package == 'smtplib':
                import smtplib
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            all_good = False
    
    return all_good

def main():
    """Run all validation tests"""
    print("🚀 RetailGenie Environment Validation")
    print("=" * 50)
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env file")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")
    
    # Run all tests
    tests = [
        test_environment_variables,
        test_dependencies,
        test_firebase_connection,
        test_gemini_api,
        test_redis_connection,
        test_email_configuration,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n📊 Validation Summary")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! Your environment is ready.")
        print("\n🚀 You can now start the application with:")
        print("   ./start_enhanced.sh")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Please fix the issues above.")
        print("\n📚 For help, check:")
        print("   - docs/ENVIRONMENT_VARIABLES_GUIDE.md")
        print("   - Run ./setup_environment.sh for initial setup")
    
    print(f"\n✅ Validation complete!")
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
