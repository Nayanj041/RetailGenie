"""
Authentication Middleware
Perfect Structure Implementation
"""

import functools
import logging
import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import jsonify, request, current_app
from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Authentication middleware for JWT token validation"""
    
    def __init__(self, app=None):
        self.app = app
        self.firebase = FirebaseUtils()
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.auth_middleware = self
        
        # Add before_request handler for protected routes
        @app.before_request
        def check_auth():
            # Skip auth for certain endpoints
            exempt_endpoints = [
                'health_check',
                'api_health_check',
                'simple_status',
                'root',
                'api_info',
                'list_all_routes',
                'get_test_token',
                'auth_bp.login',
                'auth_bp.register',
                'auth_bp.forgot_password'
            ]
            
            # Also skip auth for specific paths
            exempt_paths = [
                '/',
                '/status',
                '/api/v1/health',
                '/api/v1/routes',
                '/api/v1/auth/test-token',
                '/api/v1/auth/login',
                '/api/v1/auth/register',
                '/api/auth/login',
                '/api/auth/register',
                '/api/auth/forgot-password'
            ]
            
            if request.endpoint in exempt_endpoints or request.path in exempt_paths:
                return None
                
            # Skip auth for OPTIONS requests (CORS preflight)
            if request.method == 'OPTIONS':
                return None
                
            # Check for API key or JWT token
            return self._validate_request_auth()
    
    def _validate_request_auth(self):
        """Validate authentication for the current request"""
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header missing'}), 401
        
        try:
            # Handle Bearer token
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                payload = jwt.decode(
                    token,
                    current_app.config['JWT_SECRET_KEY'],
                    algorithms=['HS256']
                )
                
                # Check token expiration
                if payload.get('exp', 0) < datetime.utcnow().timestamp():
                    return jsonify({'error': 'Token expired'}), 401
                
                # Store user info in request context
                request.current_user = payload
                return None
                
            # Handle API key
            elif auth_header.startswith('ApiKey '):
                api_key = auth_header.split(' ')[1]
                # Validate API key logic here
                # For now, accept any API key starting with 'rg_'
                if api_key.startswith('rg_'):
                    request.current_user = {'type': 'api_key', 'key': api_key}
                    return None
                else:
                    return jsonify({'error': 'Invalid API key'}), 401
            
            else:
                return jsonify({'error': 'Invalid authorization format'}), 401
                
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f'Invalid JWT token: {e}')
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            current_app.logger.error(f'Auth middleware error: {e}')
            return jsonify({'error': 'Authentication failed'}), 500


def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_role(role):
    """Decorator to require a specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role')
            if user_role != role and user_role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
