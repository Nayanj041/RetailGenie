#!/usr/bin/env python3
"""
RetailGenie Complete Production Backend
Includes authentication, products, analytics, and AI features
"""

import os
import uuid
import jwt
import bcrypt
import logging
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

# Set environment variables for Firebase
os.environ['FIREBASE_CREDENTIALS_PATH'] = '/workspaces/RetailGenie/backend/retailgenie-production-firebase-adminsdk-fbsvc-f1c87b490f.json'

from app.utils.firebase_utils import FirebaseUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_complete_app():
    """Create complete Flask app with all features"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'retailgenie-super-secret-key-2024')
    app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', 'retailgenie-jwt-secret-key-2024')
    
    # CORS configuration
    cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001').split(',')
    
    # Add Codespace URLs if we're in a Codespace
    codespace_name = os.environ.get('CODESPACE_NAME')
    if codespace_name:
        codespace_domain = os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'app.github.dev')
        cors_origins.extend([
            f'https://{codespace_name}-3000.{codespace_domain}',
            f'https://{codespace_name}-3001.{codespace_domain}'
        ])
    
    CORS(app, 
         origins=cors_origins, 
         supports_credentials=True, 
         allow_headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Headers'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Initialize Firebase
    firebase = FirebaseUtils()
    
    # JWT helper functions
    def generate_jwt_token(user_data):
        """Generate JWT token for user"""
        payload = {
            'user_id': user_data['id'],
            'email': user_data['email'],
            'role': user_data.get('role', 'customer'),
            'exp': datetime.now(timezone.utc) + timedelta(days=7)
        }
        return jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')
    
    def verify_jwt_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    # Routes
    @app.route('/', methods=['GET'])
    def home():
        """API information and available endpoints"""
        return jsonify({
            'message': 'RetailGenie Complete API',
            'status': 'running',
            'version': '1.0.0',
            'endpoints': [
                'POST /api/v1/auth/register',
                'POST /api/v1/auth/login',
                'GET  /api/v1/health',
                'GET  /api/v1/products',
                'GET  /api/v1/analytics',
                'POST /api/v1/ai/chat',
                'GET  /api/v1/feedback'
            ]
        })
    
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        try:
            firebase_status = firebase.db is not None
            
            return jsonify({
                'status': 'healthy',
                'message': 'RetailGenie Authentication Service',
                'firebase_connected': firebase_status,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'message': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
    
    @app.route('/api/v1/auth/register', methods=['POST'])
    def register():
        """User registration endpoint"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'email', 'password']
            if not all(field in data for field in required_fields):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            # Check if user already exists
            users_ref = firebase.db.collection('users')
            existing_user = users_ref.where('email', '==', data['email']).limit(1).get()
            
            if len(existing_user) > 0:
                return jsonify({'success': False, 'error': 'User already exists'}), 400
            
            # Hash password
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            
            # Create user data
            user_data = {
                'id': str(uuid.uuid4()),
                'name': data['name'],
                'email': data['email'],
                'password': hashed_password.decode('utf-8'),
                'role': data.get('userType', 'customer'),
                'business_name': data.get('business_name', ''),
                'phone': data.get('phone', ''),
                'active': True,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Save to Firebase
            users_ref.document(user_data['id']).set(user_data)
            
            # Generate token
            token = generate_jwt_token(user_data)
            
            # Remove password from response
            user_response = {k: v for k, v in user_data.items() if k != 'password'}
            
            logger.info(f"User registered successfully: {data['email']}")
            
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'token': token,
                'user': user_response
            })
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return jsonify({'success': False, 'error': 'Registration failed'}), 500
    
    @app.route('/api/v1/auth/login', methods=['POST'])
    def login():
        """User login endpoint"""
        try:
            data = request.get_json()
            
            if not data or 'email' not in data or 'password' not in data:
                return jsonify({'success': False, 'error': 'Email and password required'}), 400
            
            # Find user by email
            users_ref = firebase.db.collection('users')
            user_docs = users_ref.where('email', '==', data['email']).limit(1).get()
            
            if len(user_docs) == 0:
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
            user_doc = user_docs[0]
            user_data = user_doc.to_dict()
            
            # Verify password
            if not bcrypt.checkpw(data['password'].encode('utf-8'), user_data['password'].encode('utf-8')):
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
            # Update last login
            users_ref.document(user_data['id']).update({
                'last_login': datetime.now(timezone.utc).isoformat()
            })
            
            # Generate token
            token = generate_jwt_token(user_data)
            
            # Remove password from response
            user_response = {k: v for k, v in user_data.items() if k != 'password'}
            user_response['last_login'] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"User logged in successfully: {data['email']}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'user': user_response
            })
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return jsonify({'success': False, 'error': 'Login failed'}), 500
    
    @app.route('/api/v1/products', methods=['GET'])
    def get_products():
        """Get all products"""
        try:
            products_ref = firebase.db.collection('products')
            products = []
            
            for doc in products_ref.stream():
                product_data = doc.to_dict()
                product_data['id'] = doc.id
                products.append(product_data)
            
            return jsonify({
                'success': True,
                'data': products,
                'count': len(products)
            })
            
        except Exception as e:
            logger.error(f"Products fetch error: {e}")
            return jsonify({'success': False, 'error': 'Failed to fetch products'}), 500
    
    @app.route('/api/v1/analytics', methods=['GET'])
    def get_analytics():
        """Get analytics data for dashboard"""
        try:
            time_range = request.args.get('time_range', 'week')
            
            # Mock analytics data (in production, integrate with real data and ML models)
            analytics_data = {
                "overview": {
                    "total_revenue": 125340.50,
                    "revenue_change": 12.5,
                    "total_orders": 1234,
                    "orders_change": 8.3,
                    "total_customers": 856,
                    "customers_change": 15.2,
                    "conversion_rate": 3.4,
                    "conversion_change": -2.1,
                },
                "sales_trend": [
                    {"date": "2025-07-01", "revenue": 12000, "orders": 120},
                    {"date": "2025-07-02", "revenue": 15000, "orders": 145},
                    {"date": "2025-07-03", "revenue": 18000, "orders": 160},
                    {"date": "2025-07-04", "revenue": 14000, "orders": 135},
                    {"date": "2025-07-05", "revenue": 22000, "orders": 180},
                    {"date": "2025-07-06", "revenue": 19000, "orders": 165},
                    {"date": "2025-07-07", "revenue": 25000, "orders": 200},
                ],
                "top_products": [
                    {"name": "Smart Headphones", "sales": 450, "revenue": 89910},
                    {"name": "Cotton T-Shirt", "sales": 320, "revenue": 9597},
                    {"name": "Programming Book", "sales": 180, "revenue": 8998},
                    {"name": "Running Shoes", "sales": 150, "revenue": 14985},
                    {"name": "Coffee Mug", "sales": 280, "revenue": 4200},
                ],
                "category_distribution": [
                    {"name": "Electronics", "value": 45, "revenue": 67500},
                    {"name": "Clothing", "value": 30, "revenue": 22500},
                    {"name": "Books", "value": 15, "revenue": 11250},
                    {"name": "Home & Garden", "value": 10, "revenue": 7500},
                ],
                "customer_segments": [
                    {"segment": "Premium", "count": 156, "percentage": 18.2},
                    {"segment": "Regular", "count": 445, "percentage": 52.0},
                    {"segment": "New", "count": 255, "percentage": 29.8},
                ]
            }
            
            logger.info(f"Analytics data retrieved for time range: {time_range}")
            return jsonify(analytics_data)
            
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return jsonify({'error': 'Failed to fetch analytics data'}), 500
    
    @app.route('/api/v1/ai/chat', methods=['POST'])
    def ai_chat():
        """AI chat assistant endpoint"""
        try:
            data = request.get_json()
            
            if not data or 'message' not in data:
                return jsonify({'error': 'Message required'}), 400
            
            message = data['message'].lower()
            
            # Simple AI responses (in production, integrate with Gemini AI)
            if 'product' in message or 'find' in message:
                response = {
                    'text': 'I can help you find products! What are you looking for?',
                    'intent': 'product_search',
                    'suggestions': ['Show electronics', 'Show clothing', 'Show books']
                }
            elif 'price' in message:
                response = {
                    'text': 'I can help you with pricing information. Which product interests you?',
                    'intent': 'price_inquiry',
                    'suggestions': ['Compare prices', 'Show deals', 'Price history']
                }
            elif 'recommendation' in message:
                response = {
                    'text': 'Based on your preferences, I recommend these top products:',
                    'intent': 'recommendations',
                    'products': [
                        {'name': 'Smart Headphones', 'price': 199.99},
                        {'name': 'Cotton T-Shirt', 'price': 29.99}
                    ]
                }
            else:
                response = {
                    'text': 'Hello! I\'m your RetailGenie AI assistant. How can I help you today?',
                    'intent': 'greeting',
                    'suggestions': ['Find products', 'Get recommendations', 'Check prices']
                }
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return jsonify({'error': 'AI chat unavailable'}), 500
    
    @app.route('/api/v1/feedback', methods=['GET'])
    def get_feedback():
        """Get customer feedback with sentiment analysis"""
        try:
            # Mock feedback data (in production, get from Firebase and run sentiment analysis)
            feedback_data = {
                "feedback": [
                    {
                        "id": "fb_001",
                        "customer": "John Doe",
                        "rating": 5,
                        "comment": "Excellent product quality and fast delivery!",
                        "sentiment": "positive",
                        "sentiment_score": 0.92,
                        "date": "2025-07-06",
                        "product": "Smart Headphones"
                    },
                    {
                        "id": "fb_002", 
                        "customer": "Jane Smith",
                        "rating": 4,
                        "comment": "Good product but shipping was slow.",
                        "sentiment": "neutral",
                        "sentiment_score": 0.65,
                        "date": "2025-07-05",
                        "product": "Cotton T-Shirt"
                    },
                    {
                        "id": "fb_003",
                        "customer": "Mike Johnson", 
                        "rating": 2,
                        "comment": "Product didn't match description. Disappointed.",
                        "sentiment": "negative",
                        "sentiment_score": 0.15,
                        "date": "2025-07-04",
                        "product": "Programming Book"
                    }
                ],
                "sentiment_summary": {
                    "positive": 45,
                    "neutral": 35, 
                    "negative": 20,
                    "average_rating": 4.2,
                    "total_feedback": 150
                }
            }
            
            return jsonify(feedback_data)
            
        except Exception as e:
            logger.error(f"Feedback error: {e}")
            return jsonify({'error': 'Failed to fetch feedback'}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'available_endpoints': [
                'GET /',
                'GET /api/v1/health',
                'POST /api/v1/auth/register',
                'POST /api/v1/auth/login',
                'GET /api/v1/products',
                'GET /api/v1/analytics',
                'POST /api/v1/ai/chat',
                'GET /api/v1/feedback'
            ]
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    return app

# Create app instance
app = create_complete_app()

# Main execution
if __name__ == '__main__':
    logger.info("🚀 Starting RetailGenie Complete Service...")
    logger.info("📍 Available endpoints:")
    logger.info("   POST /api/v1/auth/register")
    logger.info("   POST /api/v1/auth/login")
    logger.info("   GET  /api/v1/health")
    logger.info("   GET  /api/v1/products")
    logger.info("   GET  /api/v1/analytics")
    logger.info("   POST /api/v1/ai/chat")
    logger.info("   GET  /api/v1/feedback")
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🌐 Server running on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
