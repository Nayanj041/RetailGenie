#!/usr/bin/env python3
"""
RetailGenie Backend - Production-Ready Version
Simplified main app with error handling for problematic imports
"""

import logging
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_json_data():
    """Safely get JSON data from request with proper error handling."""
    if not request.data:
        return None, jsonify({"error": "No JSON data provided"}), 400

    try:
        data = request.get_json(silent=True, force=True)
        if not data:
            return None, jsonify({"error": "No JSON data provided"}), 400
        return data, None, None
    except Exception:
        return None, jsonify({"error": "Invalid JSON format"}), 400


def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Import Firebase utils with error handling
    try:
        from app.utils.firebase_utils import FirebaseUtils
        firebase = FirebaseUtils()
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e}")
        firebase = None
    
    # Health endpoint
    @app.route('/api/v1/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'message': 'RetailGenie Backend is running',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected' if firebase else 'unavailable'
        })
    
    # List all routes
    @app.route('/api/v1/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.rule,
                'methods': list(rule.methods - {'OPTIONS', 'HEAD'})
            })
        return jsonify({
            'success': True,
            'total_routes': len(routes),
            'routes': routes
        })
    
    # Products endpoints
    @app.route('/api/v1/products', methods=['GET'])
    def get_products():
        try:
            if firebase:
                # Try to get products from Firebase
                products = firebase.get_documents('products')
                return jsonify({
                    'success': True,
                    'count': len(products),
                    'products': products
                })
            else:
                # Return mock data
                mock_products = [
                    {
                        'id': 'prod_001',
                        'name': 'Premium Coffee Beans',
                        'price': 24.99,
                        'category': 'Beverages',
                        'stock': 150,
                        'description': 'High-quality arabica coffee beans'
                    },
                    {
                        'id': 'prod_002',
                        'name': 'Organic Tea Set',
                        'price': 34.99,
                        'category': 'Beverages',
                        'stock': 75,
                        'description': 'Organic herbal tea collection'
                    }
                ]
                return jsonify({
                    'success': True,
                    'count': len(mock_products),
                    'products': mock_products,
                    'note': 'Mock data - database not connected'
                })
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/v1/products', methods=['POST'])
    def create_product():
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            # Validate required fields
            required_fields = ['name', 'price', 'category']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            # Create product data
            product_data = {
                'id': data.get('id', f"prod_{uuid.uuid4().hex[:8]}"),
                'name': data['name'],
                'price': float(data['price']),
                'category': data['category'],
                'stock': data.get('stock', 0),
                'description': data.get('description', ''),
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            if firebase:
                # Save to Firebase
                doc_id = firebase.create_document('products', product_data, product_data['id'])
                return jsonify({
                    'success': True,
                    'message': 'Product created successfully',
                    'product_id': doc_id,
                    'product': product_data
                }), 201
            else:
                return jsonify({
                    'success': True,
                    'message': 'Product would be created (database not connected)',
                    'product': product_data
                })
                
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Customers endpoints
    @app.route('/api/v1/customers', methods=['GET'])
    def get_customers():
        try:
            if firebase:
                customers = firebase.get_documents('customers')
                return jsonify({
                    'success': True,
                    'count': len(customers),
                    'customers': customers
                })
            else:
                mock_customers = [
                    {
                        'id': 'cust_001',
                        'name': 'John Smith',
                        'email': 'john.smith@example.com',
                        'phone': '+1-555-0123',
                        'loyalty_points': 250,
                        'total_orders': 12
                    },
                    {
                        'id': 'cust_002',
                        'name': 'Sarah Johnson',
                        'email': 'sarah.j@example.com',
                        'phone': '+1-555-0456',
                        'loyalty_points': 180,
                        'total_orders': 8
                    }
                ]
                return jsonify({
                    'success': True,
                    'count': len(mock_customers),
                    'customers': mock_customers,
                    'note': 'Mock data - database not connected'
                })
        except Exception as e:
            logger.error(f"Error getting customers: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Analytics endpoints
    @app.route('/api/v1/analytics/dashboard', methods=['GET'])
    def get_dashboard():
        try:
            dashboard_data = {
                'total_sales': 12456.78,
                'total_orders': 145,
                'total_customers': 89,
                'total_products': 23,
                'revenue_growth': 15.2,
                'top_products': [
                    {'name': 'Premium Coffee', 'sales': 2345.67},
                    {'name': 'Organic Tea', 'sales': 1876.32}
                ],
                'generated_at': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': dashboard_data
            })
        except Exception as e:
            logger.error(f"Error getting dashboard: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # AI Chat endpoint (simplified without Gemini)
    @app.route('/api/v1/ai/chat', methods=['POST'])
    def ai_chat():
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            user_message = data.get('message', '')
            
            # Simple AI response (replace with Gemini when API key is fixed)
            if 'product' in user_message.lower():
                ai_response = "I can help you with product recommendations! Our premium coffee beans are very popular."
            elif 'order' in user_message.lower():
                ai_response = "I can assist with order management. What would you like to know about orders?"
            elif 'hello' in user_message.lower() or 'hi' in user_message.lower():
                ai_response = "Hello! I'm your RetailGenie AI assistant. How can I help you today?"
            else:
                ai_response = "I'm here to help with your retail management needs. Feel free to ask about products, orders, or analytics!"
            
            response_data = {
                'response': ai_response,
                'user_message': user_message,
                'timestamp': datetime.now().isoformat(),
                'note': 'Basic AI response - Gemini integration pending API key update'
            }
            
            return jsonify({
                'success': True,
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Database initialization endpoint
    @app.route('/api/v1/init-database', methods=['POST'])
    def init_database():
        try:
            if not firebase:
                return jsonify({
                    'success': False,
                    'error': 'Database not connected'
                }), 500
            
            # Sample data initialization
            sample_products = [
                {
                    'id': 'prod_001',
                    'name': 'Premium Coffee Beans',
                    'price': 24.99,
                    'category': 'Beverages',
                    'stock': 150,
                    'description': 'High-quality arabica coffee beans',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 'prod_002',
                    'name': 'Organic Tea Set',
                    'price': 34.99,
                    'category': 'Beverages',
                    'stock': 75,
                    'description': 'Organic herbal tea collection',
                    'created_at': datetime.now().isoformat()
                }
            ]
            
            created_products = []
            for product in sample_products:
                try:
                    firebase.create_document('products', product, product['id'])
                    created_products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to create product {product['id']}: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Database initialized with sample data',
                'products_created': len(created_products)
            })
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'message': 'The requested URL was not found. Use /api/v1/routes to see available endpoints.',
            'available_endpoints': [
                '/api/v1/health',
                '/api/v1/products',
                '/api/v1/customers', 
                '/api/v1/analytics/dashboard',
                '/api/v1/ai/chat',
                '/api/v1/routes'
            ]
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'Something went wrong on the server'
        }), 500

    return app


if __name__ == "__main__":
    app = create_app()
    logger.info("🚀 Starting RetailGenie Backend...")
    logger.info("📊 Database: Firebase Firestore")
    logger.info("🤖 AI: Simplified mode (pending Gemini API key)")
    logger.info("🌐 Server starting on http://0.0.0.0:5000")
    
    app.run(debug=False, host="0.0.0.0", port=5000)
