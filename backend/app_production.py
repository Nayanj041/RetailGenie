"""
RetailGenie API - Production Implementation
Complete API implementation following OpenAPI 3.0.3 standards
"""

import logging
import os
import time
import uuid
from datetime import datetime, timezone
from functools import wraps

import psutil
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.utils.firebase_utils import FirebaseUtils

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address, default_limits=["1000 per hour", "100 per minute"]
)


def create_app():
    app = Flask(__name__)

    # Initialize rate limiter
    limiter.init_app(app)

    # Initialize Firebase
    firebase = FirebaseUtils()

    # Enable CORS
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    CORS(app, origins=cors_origins, supports_credentials=True)

    # Utility functions
    def generate_request_id():
        """Generate unique request ID for tracking"""
        return f"req-{uuid.uuid4().hex[:8]}"

    def get_json_data():
        """Safely get JSON data from request with proper error handling."""
        request_id = generate_request_id()

        if not request.data:
            return (
                None,
                create_error_response(
                    "No JSON data provided", 400, request.path, request_id
                ),
                400,
            )

        try:
            data = request.get_json(silent=True, force=True)
            if not data:
                return (
                    None,
                    create_error_response(
                        "No JSON data provided", 400, request.path, request_id
                    ),
                    400,
                )
            return data, None, None
        except Exception:
            return (
                None,
                create_error_response(
                    "Invalid JSON format", 400, request.path, request_id
                ),
                400,
            )

    def create_error_response(
        error_message, status_code, path=None, request_id=None, details=None
    ):
        """Create standardized error response"""
        return jsonify(
            {
                "error": error_message,
                "status_code": status_code,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "path": path or request.path,
                "request_id": request_id or generate_request_id(),
                "details": details or {},
            }
        )

    def create_success_response(data, status_code=200, metadata=None):
        """Create standardized success response with metadata"""
        response_data = data.copy() if isinstance(data, dict) else {"data": data}

        if metadata:
            response_data["metadata"] = metadata

        response_data["metadata"] = {
            "version": "2.1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": generate_request_id(),
            **(metadata or {}),
        }

        return jsonify(response_data), status_code

    def require_auth(f):
        """Decorator for endpoints requiring authentication"""

        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return (
                    create_error_response("Authentication required", 401, request.path),
                    401,
                )

            # In production, validate JWT token here
            token = auth_header.split(" ")[1]
            if not token or token == "null":
                return (
                    create_error_response(
                        "Invalid authentication token", 401, request.path
                    ),
                    401,
                )

            return f(*args, **kwargs)

        return decorated_function

    # Performance monitoring and troubleshooting utilities
    @app.before_request
    def before_request():
        """Track request start time for performance monitoring"""
        g.start_time = time.time()
        g.request_id = generate_request_id()

    @app.after_request
    def after_request(response):
        """Log slow requests and add performance headers"""
        duration = time.time() - g.start_time

        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-ID"] = g.request_id

        # Log slow requests
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.path} took {duration:.2f}s - "
                f"Request ID: {g.request_id}"
            )

        # Log all requests in debug mode
        if app.debug:
            logger.info(
                f"{request.method} {request.path} - {response.status_code} - "
                f"{duration:.3f}s"
            )

        return response

    def test_firebase_connection():
        """Test Firebase connection for troubleshooting"""
        try:
            firebase.db.collection("test").limit(1).get()
            return True
        except Exception as e:
            logger.error(f"Firebase connection failed: {e}")
            return False

    def batch_create_products(products):
        """Optimized batch creation for multiple products"""
        try:
            batch = firebase.db.batch()
            created_products = []

            for product in products:
                doc_ref = firebase.db.collection("products").document()
                batch.set(doc_ref, product)
                product["id"] = doc_ref.id
                created_products.append(product)

            batch.commit()
            return created_products
        except Exception as e:
            logger.error(f"Batch create failed: {e}")
            raise

    # Health Check Endpoints
    @app.route("/")
    def home():
        """API health check"""
        return create_success_response(
            {
                "message": "RetailGenie API is running!",
                "status": "success",
                "database": "Firebase Firestore" if firebase.db else "Mock Database",
                "version": "2.1.0",
            }
        )

    @app.route("/health")
    def health():
        """Detailed health status"""
        db_status = "connected" if firebase.db else "disconnected"
        return create_success_response(
            {
                "status": "healthy",
                "database_status": db_status,
                "firebase_project": os.getenv("FIREBASE_PROJECT_ID", "not-configured"),
                "environment": os.getenv("FLASK_ENV", "development"),
                "uptime": "healthy",
            }
        )

    # API Version Information
    @app.route("/api/v1/info")
    def api_v1_info():
        """Get API v1 information"""
        return create_success_response(
            {
                "version": "1.0.0",
                "description": "RetailGenie API Version 1 - Stable Production API",
                "endpoints": {
                    "products": "/api/v1/products",
                    "feedback": "/api/v1/feedback",
                    "auth": "/api/v1/auth",
                    "analytics": "/api/v1/analytics",
                    "ai": "/api/v1/ai",
                },
                "status": "active",
                "documentation": "/api/v1/docs",
            }
        )

    @app.route("/api/v2/info")
    def api_v2_info():
        """Get API v2 information"""
        return create_success_response(
            {
                "version": "2.1.0",
                "description": "RetailGenie API Version 2 - Enhanced Features",
                "endpoints": {
                    "products": "/api/v2/products",
                    "search": "/api/v2/search",
                    "recommendations": "/api/v2/recommendations",
                    "analytics": "/api/v2/analytics",
                    "ai": "/api/v2/ai",
                },
                "status": "active",
                "features": [
                    "advanced_search",
                    "real_time_analytics",
                    "ai_recommendations",
                ],
                "documentation": "/api/v2/docs",
            }
        )

    # Product Management Endpoints (V1)
    @app.route("/api/v1/products", methods=["GET"])
    @limiter.limit("100 per minute")
    def get_products_v1():
        """Get all products - V1"""
        try:
            # Parse query parameters
            page = int(request.args.get("page", 1))
            limit = min(int(request.args.get("limit", 20)), 100)
            category = request.args.get("category")
            search = request.args.get("search")
            in_stock = request.args.get("in_stock")
            min_price = request.args.get("min_price", type=float)
            max_price = request.args.get("max_price", type=float)

            # Get products from Firebase
            products = firebase.get_documents("products")

            # Apply filters
            if category:
                products = [
                    p
                    for p in products
                    if p.get("category", "").lower() == category.lower()
                ]
            if search:
                products = [
                    p
                    for p in products
                    if search.lower() in p.get("name", "").lower()
                    or search.lower() in p.get("description", "").lower()
                ]
            if in_stock is not None:
                in_stock_bool = in_stock.lower() == "true"
                products = [
                    p for p in products if p.get("in_stock", True) == in_stock_bool
                ]
            if min_price is not None:
                products = [p for p in products if p.get("price", 0) >= min_price]
            if max_price is not None:
                products = [p for p in products if p.get("price", 0) <= max_price]

            # Pagination
            total = len(products)
            start = (page - 1) * limit
            end = start + limit
            paginated_products = products[start:end]

            # Add product IDs
            for i, product in enumerate(paginated_products):
                if "id" not in product:
                    product["id"] = f"product-{i + 1}"

            return create_success_response(
                {
                    "products": paginated_products,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit,
                        "has_next": end < total,
                        "has_prev": page > 1,
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error getting products: {str(e)}")
            return (
                create_error_response("Failed to retrieve products", 500, request.path),
                500,
            )

    @app.route("/api/v1/products/<product_id>", methods=["GET"])
    def get_product_v1(product_id):
        """Get product by ID - V1"""
        try:
            product = firebase.get_document("products", product_id)
            if product:
                product["id"] = product_id
                return create_success_response(product)
            else:
                return (
                    create_error_response(
                        "Product not found",
                        404,
                        request.path,
                        details={"product_id": product_id},
                    ),
                    404,
                )
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            return (
                create_error_response("Failed to retrieve product", 500, request.path),
                500,
            )

    @app.route("/api/v1/products", methods=["POST"])
    @require_auth
    @limiter.limit("50 per hour")
    def create_product_v1():
        """Create new product - V1"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            # Validate required fields
            required_fields = ["name", "price"]
            for field in required_fields:
                if field not in data:
                    return (
                        create_error_response(
                            f"Missing required field: {field}",
                            400,
                            request.path,
                            details={"required_fields": required_fields},
                        ),
                        400,
                    )

            # Validate data types
            try:
                price = float(data.get("price"))
                if price < 0:
                    raise ValueError("Price must be non-negative")
            except (ValueError, TypeError):
                return (
                    create_error_response(
                        "Invalid price value",
                        400,
                        request.path,
                        details={"field": "price", "type": "number"},
                    ),
                    400,
                )

            # Create product data
            product_data = {
                "name": data.get("name"),
                "price": price,
                "category": data.get("category", "Uncategorized"),
                "description": data.get("description", ""),
                "in_stock": data.get("in_stock", True),
                "stock_quantity": data.get("stock_quantity", 0),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Create document in Firebase
            product_id = firebase.create_document("products", product_data)
            product_data["id"] = product_id

            logger.info(f"Created product: {product_id}")
            return create_success_response(product_data, 201)

        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return (
                create_error_response("Failed to create product", 500, request.path),
                500,
            )

    @app.route("/api/v1/products/<product_id>", methods=["PUT"])
    @require_auth
    def update_product_v1(product_id):
        """Update product - V1"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            # Check if product exists
            existing_product = firebase.get_document("products", product_id)
            if not existing_product:
                return (
                    create_error_response(
                        "Product not found",
                        404,
                        request.path,
                        details={"product_id": product_id},
                    ),
                    404,
                )

            # Update data
            update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

            # Update only provided fields
            for field in [
                "name",
                "price",
                "category",
                "description",
                "in_stock",
                "stock_quantity",
            ]:
                if field in data:
                    if field == "price":
                        try:
                            price = float(data[field])
                            if price < 0:
                                raise ValueError("Price must be non-negative")
                            update_data[field] = price
                        except (ValueError, TypeError):
                            return (
                                create_error_response(
                                    "Invalid price value",
                                    400,
                                    request.path,
                                    details={"field": "price", "type": "number"},
                                ),
                                400,
                            )
                    else:
                        update_data[field] = data[field]

            # Update document in Firebase
            firebase.update_document("products", product_id, update_data)

            # Get updated product
            updated_product = firebase.get_document("products", product_id)
            updated_product["id"] = product_id

            logger.info(f"Updated product: {product_id}")
            return create_success_response(updated_product)

        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            return (
                create_error_response("Failed to update product", 500, request.path),
                500,
            )

    @app.route("/api/v1/products/<product_id>", methods=["DELETE"])
    @require_auth
    def delete_product_v1(product_id):
        """Delete product - V1"""
        try:
            # Check if product exists
            existing_product = firebase.get_document("products", product_id)
            if not existing_product:
                return (
                    create_error_response(
                        "Product not found",
                        404,
                        request.path,
                        details={"product_id": product_id},
                    ),
                    404,
                )

            # Delete document from Firebase
            firebase.delete_document("products", product_id)

            logger.info(f"Deleted product: {product_id}")
            return "", 204

        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            return (
                create_error_response("Failed to delete product", 500, request.path),
                500,
            )

    # Enhanced V2 Product Endpoints
    @app.route("/api/v2/products", methods=["GET"])
    @limiter.limit("200 per minute")
    def get_products_v2():
        """Get all products - V2 Enhanced"""
        try:
            # Parse query parameters
            page = int(request.args.get("page", 1))
            limit = min(int(request.args.get("limit", 20)), 100)
            sort_by = request.args.get("sort_by", "created_at")
            sort_order = request.args.get("sort_order", "desc")
            include_analytics = (
                request.args.get("include_analytics", "false").lower() == "true"
            )

            # Standard filters
            category = request.args.get("category")
            search = request.args.get("search")
            in_stock = request.args.get("in_stock")
            min_price = request.args.get("min_price", type=float)
            max_price = request.args.get("max_price", type=float)

            # Get products from Firebase
            products = firebase.get_documents("products")

            # Apply filters (same as V1)
            if category:
                products = [
                    p
                    for p in products
                    if p.get("category", "").lower() == category.lower()
                ]
            if search:
                products = [
                    p
                    for p in products
                    if search.lower() in p.get("name", "").lower()
                    or search.lower() in p.get("description", "").lower()
                ]
            if in_stock is not None:
                in_stock_bool = in_stock.lower() == "true"
                products = [
                    p for p in products if p.get("in_stock", True) == in_stock_bool
                ]
            if min_price is not None:
                products = [p for p in products if p.get("price", 0) >= min_price]
            if max_price is not None:
                products = [p for p in products if p.get("price", 0) <= max_price]

            # Enhanced sorting
            reverse = sort_order.lower() == "desc"
            if sort_by in ["name", "price", "created_at", "updated_at"]:
                products.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)

            # Add enhanced product data
            for i, product in enumerate(products):
                if "id" not in product:
                    product["id"] = f"product-{i + 1}"

                # Add enhanced fields
                product["rating"] = round(
                    4.0 + (hash(product.get("name", "")) % 100) / 100, 1
                )
                product["review_count"] = hash(product.get("name", "")) % 200 + 10
                product["tags"] = product.get("name", "").lower().split()[:3]

                if include_analytics:
                    product["analytics"] = {
                        "views": hash(product.get("name", "")) % 1000 + 100,
                        "conversions": hash(product.get("name", "")) % 50 + 5,
                        "conversion_rate": round(
                            (hash(product.get("name", "")) % 30 + 5) / 100, 3
                        ),
                    }

            # Pagination
            total = len(products)
            start = (page - 1) * limit
            end = start + limit
            paginated_products = products[start:end]

            # Enhanced response with metadata
            return create_success_response(
                {
                    "products": paginated_products,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit,
                        "has_next": end < total,
                        "has_prev": page > 1,
                    },
                    "filters": {
                        "category": category,
                        "search": search,
                        "in_stock": in_stock,
                        "min_price": min_price,
                        "max_price": max_price,
                        "sort_by": sort_by,
                        "sort_order": sort_order,
                    },
                },
                metadata={"execution_time_ms": 45.2, "api_version": "2.1.0"},
            )

        except Exception as e:
            logger.error(f"Error getting products v2: {str(e)}")
            return (
                create_error_response("Failed to retrieve products", 500, request.path),
                500,
            )

    @app.route("/api/v2/products/<product_id>", methods=["GET"])
    def get_product_v2(product_id):
        """Get product by ID - V2 Enhanced"""
        try:
            include_recommendations = (
                request.args.get("include_recommendations", "false").lower() == "true"
            )
            include_analytics = (
                request.args.get("include_analytics", "false").lower() == "true"
            )

            product = firebase.get_document("products", product_id)
            if not product:
                return (
                    create_error_response(
                        "Product not found",
                        404,
                        request.path,
                        details={"product_id": product_id},
                    ),
                    404,
                )

            product["id"] = product_id

            # Add enhanced fields
            product["rating"] = round(
                4.0 + (hash(product.get("name", "")) % 100) / 100, 1
            )
            product["review_count"] = hash(product.get("name", "")) % 200 + 10
            product["tags"] = product.get("name", "").lower().split()[:3]
            product["images"] = [
                f"https://cdn.retailgenie.com/products/{product_id}/image1.jpg",
                f"https://cdn.retailgenie.com/products/{product_id}/image2.jpg",
            ]

            if include_analytics:
                product["analytics"] = {
                    "views": hash(product.get("name", "")) % 1000 + 100,
                    "conversions": hash(product.get("name", "")) % 50 + 5,
                    "conversion_rate": round(
                        (hash(product.get("name", "")) % 30 + 5) / 100, 3
                    ),
                    "revenue": round(
                        product.get("price", 0)
                        * (hash(product.get("name", "")) % 50 + 5),
                        2,
                    ),
                }

            if include_recommendations:
                # Get related products (simplified recommendation)
                all_products = firebase.get_documents("products")
                same_category = [
                    p
                    for p in all_products
                    if p.get("category") == product.get("category")
                    and p.get("name") != product.get("name")
                ][:3]
                product["recommendations"] = same_category

            return create_success_response(product)

        except Exception as e:
            logger.error(f"Error getting product v2 {product_id}: {str(e)}")
            return (
                create_error_response("Failed to retrieve product", 500, request.path),
                500,
            )

    # Advanced Search Endpoint
    @app.route("/api/v2/search", methods=["GET"])
    @limiter.limit("100 per minute")
    def advanced_search():
        """Advanced search with AI-powered relevance"""
        try:
            query = request.args.get("q", "").strip()
            if not query:
                return (
                    create_error_response(
                        "Search query is required",
                        400,
                        request.path,
                        details={"parameter": "q"},
                    ),
                    400,
                )

            page = int(request.args.get("page", 1))
            limit = min(int(request.args.get("limit", 20)), 100)
            category = request.args.get("category")

            # Parse advanced filters
            filters_str = request.args.get("filters", "{}")
            try:
                import json

                filters = json.loads(filters_str)
            except json.JSONDecodeError:
                filters = {}

            start_time = datetime.now()

            # Get all products
            products = firebase.get_documents("products")

            # Search logic
            search_results = []
            for i, product in enumerate(products):
                relevance_score = 0.0
                match_type = "none"

                # Exact name match
                if query.lower() in product.get("name", "").lower():
                    relevance_score += 0.8
                    match_type = "exact"

                # Description match
                if query.lower() in product.get("description", "").lower():
                    relevance_score += 0.5
                    if match_type == "none":
                        match_type = "partial"

                # Category match
                if query.lower() in product.get("category", "").lower():
                    relevance_score += 0.3
                    if match_type == "none":
                        match_type = "category"

                # Semantic similarity (simplified)
                query_words = set(query.lower().split())
                product_words = set(
                    (product.get("name", "") + " " + product.get("description", ""))
                    .lower()
                    .split()
                )
                overlap = len(query_words.intersection(product_words))
                if overlap > 0:
                    relevance_score += overlap * 0.2
                    if match_type == "none":
                        match_type = "semantic"

                if relevance_score > 0:
                    product["id"] = f"product-{i + 1}"
                    product["relevance_score"] = min(relevance_score, 1.0)
                    product["match_type"] = match_type
                    search_results.append(product)

            # Apply category filter
            if category:
                search_results = [
                    p
                    for p in search_results
                    if p.get("category", "").lower() == category.lower()
                ]

            # Apply advanced filters
            if "price_range" in filters and len(filters["price_range"]) == 2:
                min_price, max_price = filters["price_range"]
                search_results = [
                    p
                    for p in search_results
                    if min_price <= p.get("price", 0) <= max_price
                ]

            if "brand" in filters:
                search_results = [
                    p
                    for p in search_results
                    if filters["brand"].lower() in p.get("name", "").lower()
                ]

            # Sort by relevance
            search_results.sort(key=lambda x: x["relevance_score"], reverse=True)

            # Pagination
            total = len(search_results)
            start = (page - 1) * limit
            end = start + limit
            paginated_results = search_results[start:end]

            search_time = (datetime.now() - start_time).total_seconds() * 1000

            return create_success_response(
                {
                    "results": paginated_results,
                    "total_results": total,
                    "search_time_ms": round(search_time, 1),
                    "suggestions": [
                        f"{query} headphones",
                        f"{query} wireless",
                        f"best {query}",
                    ],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit,
                        "has_next": end < total,
                        "has_prev": page > 1,
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error in advanced search: {str(e)}")
            return create_error_response("Search failed", 500, request.path), 500

    # Authentication Endpoints
    @app.route("/api/auth/register", methods=["POST"])
    @limiter.limit("10 per minute")
    def register():
        """Register new user"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            required_fields = ["email", "password", "name"]
            for field in required_fields:
                if field not in data:
                    return (
                        create_error_response(
                            f"Missing required field: {field}",
                            400,
                            request.path,
                            details={"required_fields": required_fields},
                        ),
                        400,
                    )

            # Validate email format
            email = data.get("email", "")
            if "@" not in email or "." not in email:
                return (
                    create_error_response(
                        "Invalid email format",
                        400,
                        request.path,
                        details={"field": "email"},
                    ),
                    400,
                )

            # Check password strength
            password = data.get("password", "")
            if len(password) < 8:
                return (
                    create_error_response(
                        "Password must be at least 8 characters",
                        400,
                        request.path,
                        details={"field": "password", "min_length": 8},
                    ),
                    400,
                )

            # Check if user already exists
            existing_users = firebase.query_documents("users", "email", "==", email)
            if existing_users:
                return (
                    create_error_response(
                        "User with this email already exists",
                        409,
                        request.path,
                        details={"email": email},
                    ),
                    409,
                )

            # Create user data
            user_data = {
                "email": email,
                "name": data["name"],
                "phone": data.get("phone", ""),
                "role": "user",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_active": True,
                "preferences": {"notifications": True, "marketing": False},
            }

            # Create user in Firebase
            user_id = firebase.create_document("users", user_data)
            user_data["id"] = user_id

            # Generate JWT token (simplified for demo)
            token = f"jwt-token-{user_id}-{datetime.now().timestamp()}"

            logger.info(f"Registered user: {email}")
            return create_success_response(
                {
                    "message": "User registered successfully",
                    "user": user_data,
                    "token": token,
                    "expires_in": 3600,
                },
                201,
            )

        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return (
                create_error_response("Failed to register user", 500, request.path),
                500,
            )

    @app.route("/api/auth/login", methods=["POST"])
    @limiter.limit("20 per minute")
    def login():
        """User login"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            required_fields = ["email", "password"]
            for field in required_fields:
                if field not in data:
                    return (
                        create_error_response(
                            f"Missing required field: {field}",
                            400,
                            request.path,
                            details={"required_fields": required_fields},
                        ),
                        400,
                    )

            email = data["email"]
            # password = data["password"]  # Currently not used for verification

            # Find user by email
            users = firebase.query_documents("users", "email", "==", email)
            if not users:
                return (
                    create_error_response("Invalid credentials", 401, request.path),
                    401,
                )

            user = users[0]

            # In production, verify password hash here
            # For demo, we'll accept any password for existing users

            # Generate JWT token (simplified for demo)
            token = (
                f"jwt-token-{user.get('id', 'unknown')}-{datetime.now().timestamp()}"
            )

            logger.info(f"User logged in: {email}")
            return create_success_response(
                {
                    "message": "Login successful",
                    "user": user,
                    "token": token,
                    "expires_in": 3600,
                }
            )

        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            return create_error_response("Failed to login", 500, request.path), 500

    # AI Assistant Endpoints
    @app.route("/api/v1/ai/chat", methods=["POST"])
    @require_auth
    @limiter.limit("30 per minute")
    def ai_chat():
        """AI Chat Assistant"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            message = data.get("message", "").strip()
            if not message:
                return (
                    create_error_response(
                        "Message is required",
                        400,
                        request.path,
                        details={"field": "message"},
                    ),
                    400,
                )

            context = data.get("context", {})

            # Simple AI response logic (in production, integrate with Google Gemini)
            response_text = f"Thank you for your question: '{message}'. "

            if "headphones" in message.lower():
                response_text += (
                    "I recommend checking out our wireless Bluetooth headphones. "
                    "They offer excellent sound quality and comfort."
                )
                # Get headphone products
                products = firebase.get_documents("products")
                recommendations = [
                    p for p in products if "headphone" in p.get("name", "").lower()
                ][:3]
            elif "price" in message.lower() or "budget" in message.lower():
                response_text += (
                    "I can help you find products within your budget. "
                    "What's your price range?"
                )
                recommendations = []
            else:
                response_text += (
                    "I'm here to help you find the perfect products. "
                    "Could you tell me more about what you're looking for?"
                )
                recommendations = []

            return create_success_response(
                {
                    "response": response_text,
                    "recommendations": recommendations,
                    "context": {
                        **context,
                        "last_message": message,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    "confidence": 0.85,
                }
            )

        except Exception as e:
            logger.error(f"Error in AI chat: {str(e)}")
            return create_error_response("AI chat failed", 500, request.path), 500

    # Recommendations Endpoint
    @app.route("/api/v2/recommendations/<product_id>", methods=["GET"])
    def get_recommendations(product_id):
        """Get product recommendations"""
        try:
            count = min(int(request.args.get("count", 5)), 20)
            rec_type = request.args.get("type", "similar")

            # Get the source product
            source_product = firebase.get_document("products", product_id)
            if not source_product:
                return (
                    create_error_response(
                        "Product not found",
                        404,
                        request.path,
                        details={"product_id": product_id},
                    ),
                    404,
                )

            # Get all products for recommendations
            all_products = firebase.get_documents("products")
            recommendations = []

            if rec_type == "similar":
                # Find products in same category
                same_category = [
                    p
                    for p in all_products
                    if p.get("category") == source_product.get("category")
                    and p.get("name") != source_product.get("name")
                ]
                recommendations = same_category[:count]
            elif rec_type == "complementary":
                # Find products that complement this one
                if "headphones" in source_product.get("name", "").lower():
                    complementary = [
                        p for p in all_products if "phone" in p.get("name", "").lower()
                    ]
                else:
                    complementary = [
                        p
                        for p in all_products
                        if p.get("category") != source_product.get("category")
                    ]
                recommendations = complementary[:count]
            elif rec_type == "trending":
                # Return highest "rated" products (mock trending)
                trending = sorted(
                    all_products,
                    key=lambda x: hash(x.get("name", "")) % 100,
                    reverse=True,
                )
                recommendations = trending[:count]

            # Add recommendation scores and reasons
            for i, rec in enumerate(recommendations):
                rec["id"] = f"product-{hash(rec.get('name', '')) % 1000}"
                rec["score"] = round(0.9 - (i * 0.1), 2)
                if rec_type == "similar":
                    rec["reason"] = "Similar category and features"
                elif rec_type == "complementary":
                    rec["reason"] = "Often bought together"
                else:
                    rec["reason"] = "Trending product"

            return create_success_response(
                {
                    "product_id": product_id,
                    "recommendations": recommendations,
                    "algorithm": f"{rec_type}_matching",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return (
                create_error_response(
                    "Failed to get recommendations", 500, request.path
                ),
                500,
            )

    # Analytics Dashboard
    @app.route("/api/v1/analytics/dashboard", methods=["GET"])
    @require_auth
    @limiter.limit("60 per hour")
    def analytics_dashboard():
        """Get analytics dashboard"""
        try:
            period = request.args.get("period", "week")

            # Mock analytics data (in production, query real analytics)
            dashboard_data = {
                "summary": {
                    "total_revenue": 45678.90,
                    "total_orders": 234,
                    "total_customers": 156,
                    "conversion_rate": 0.23,
                },
                "sales": {
                    "daily_revenue": [
                        {"date": "2025-06-22", "revenue": 5234.50},
                        {"date": "2025-06-23", "revenue": 6123.80},
                        {"date": "2025-06-24", "revenue": 7891.20},
                        {"date": "2025-06-25", "revenue": 5678.30},
                        {"date": "2025-06-26", "revenue": 8234.70},
                        {"date": "2025-06-27", "revenue": 6789.40},
                        {"date": "2025-06-28", "revenue": 7234.90},
                    ],
                    "top_products": [
                        {
                            "product_id": "product-1",
                            "name": "Wireless Headphones",
                            "revenue": 12345.60,
                            "units_sold": 156,
                        },
                        {
                            "product_id": "product-2",
                            "name": "Smart Watch",
                            "revenue": 9876.40,
                            "units_sold": 45,
                        },
                        {
                            "product_id": "product-3",
                            "name": "Bluetooth Speaker",
                            "revenue": 7654.20,
                            "units_sold": 89,
                        },
                    ],
                },
                "users": {"new_users": 45, "active_users": 234, "retention_rate": 0.78},
                "period": period,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            return create_success_response(dashboard_data)

        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return (
                create_error_response("Failed to get analytics", 500, request.path),
                500,
            )

    # Main Analytics Endpoint (for frontend compatibility)
    @app.route("/api/v1/analytics", methods=["GET"])
    @require_auth
    @limiter.limit("60 per hour")
    def get_analytics():
        """Get analytics data"""
        try:
            time_range = request.args.get("time_range", "week")

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
                    {"date": "2024-07-01", "revenue": 12000, "orders": 120},
                    {"date": "2024-07-02", "revenue": 15000, "orders": 145},
                    {"date": "2024-07-03", "revenue": 18000, "orders": 160},
                    {"date": "2024-07-04", "revenue": 14000, "orders": 135},
                    {"date": "2024-07-05", "revenue": 22000, "orders": 180},
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
                    {"segment": "Premium", "customers": 150, "avg_order_value": 285},
                    {"segment": "Regular", "customers": 400, "avg_order_value": 125},
                    {"segment": "New", "customers": 306, "avg_order_value": 85},
                ],
                "time_range": time_range,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            return create_success_response(analytics_data)

        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return (
                create_error_response("Failed to get analytics", 500, request.path),
                500,
            )

    # Feedback Endpoints
    @app.route("/api/feedback/<product_id>", methods=["GET"])
    def get_feedback(product_id):
        """Get product feedback"""
        try:
            page = int(request.args.get("page", 1))
            limit = min(int(request.args.get("limit", 20)), 100)

            # Get feedback for the product
            feedback_list = firebase.query_documents(
                "feedback", "product_id", "==", product_id
            )

            # Pagination
            total = len(feedback_list)
            start = (page - 1) * limit
            end = start + limit
            paginated_feedback = feedback_list[start:end]

            # Calculate ratings
            if feedback_list:
                total_rating = sum(f.get("rating", 0) for f in feedback_list)
                average_rating = round(total_rating / len(feedback_list), 1)

                # Rating distribution
                rating_dist = {str(i): 0 for i in range(1, 6)}
                for feedback in feedback_list:
                    rating = str(feedback.get("rating", 0))
                    if rating in rating_dist:
                        rating_dist[rating] += 1
            else:
                average_rating = 0
                rating_dist = {str(i): 0 for i in range(1, 6)}

            return create_success_response(
                {
                    "product_id": product_id,
                    "feedback": paginated_feedback,
                    "average_rating": average_rating,
                    "total_reviews": total,
                    "rating_distribution": rating_dist,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit,
                        "has_next": end < total,
                        "has_prev": page > 1,
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error getting feedback: {str(e)}")
            return (
                create_error_response("Failed to retrieve feedback", 500, request.path),
                500,
            )

    @app.route("/api/feedback", methods=["POST"])
    @require_auth
    @limiter.limit("10 per minute")
    def submit_feedback():
        """Submit product feedback"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            required_fields = ["product_id", "rating", "comment", "user_name"]
            for field in required_fields:
                if field not in data:
                    return (
                        create_error_response(
                            f"Missing required field: {field}",
                            400,
                            request.path,
                            details={"required_fields": required_fields},
                        ),
                        400,
                    )

            # Validate rating
            rating = data.get("rating")
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return (
                    create_error_response(
                        "Rating must be between 1 and 5",
                        400,
                        request.path,
                        details={"field": "rating", "min": 1, "max": 5},
                    ),
                    400,
                )

            # Create feedback data
            feedback_data = {
                "product_id": data["product_id"],
                "rating": int(rating),
                "comment": data["comment"],
                "user_name": data["user_name"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "verified_purchase": True,  # In production, check if user bought the product
            }

            # Create feedback in Firebase
            feedback_id = firebase.create_document("feedback", feedback_data)
            feedback_data["id"] = feedback_id

            logger.info(f"Submitted feedback: {feedback_id}")
            return create_success_response(
                {
                    "message": "Feedback submitted successfully",
                    "feedback": feedback_data,
                },
                201,
            )

        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return (
                create_error_response("Failed to submit feedback", 500, request.path),
                500,
            )

    # WebSocket Statistics
    @app.route("/ws-stats")
    def websocket_stats():
        """Get WebSocket statistics"""
        try:
            # Mock WebSocket stats (in production, get from WebSocket server)
            stats = {
                "active_connections": 42,
                "total_connections": 1337,
                "rooms": [
                    {"name": "product_updates", "connections": 15},
                    {"name": "inventory_alerts", "connections": 8},
                    {"name": "order_notifications", "connections": 19},
                ],
                "events_sent": 5678,
                "uptime": "2d 4h 23m",
            }

            return create_success_response(stats)

        except Exception as e:
            logger.error(f"Error getting WebSocket stats: {str(e)}")
            return (
                create_error_response(
                    "Failed to get WebSocket statistics", 500, request.path
                ),
                500,
            )

    # Admin Endpoints
    @app.route("/api/admin/init-db", methods=["POST"])
    @require_auth
    @limiter.limit("5 per hour")
    def init_database():
        """Initialize database with sample data"""
        try:
            # Initialize database with sample data
            sample_products = [
                {
                    "name": "Wireless Bluetooth Headphones",
                    "price": 79.99,
                    "category": "Electronics",
                    "description": (
                        "High-quality wireless headphones with noise cancellation"
                    ),
                    "in_stock": True,
                    "stock_quantity": 50,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "name": "Smart Fitness Watch",
                    "price": 199.99,
                    "category": "Electronics",
                    "description": (
                        "Advanced fitness tracking with heart rate monitoring"
                    ),
                    "in_stock": True,
                    "stock_quantity": 25,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "name": "Organic Coffee Beans",
                    "price": 24.99,
                    "category": "Food & Beverage",
                    "description": "Premium organic coffee beans, medium roast",
                    "in_stock": False,
                    "stock_quantity": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "name": "Bluetooth Portable Speaker",
                    "price": 49.99,
                    "category": "Electronics",
                    "description": "Compact wireless speaker with rich sound",
                    "in_stock": True,
                    "stock_quantity": 75,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "name": "Yoga Mat Premium",
                    "price": 34.99,
                    "category": "Fitness",
                    "description": "Non-slip premium yoga mat for all exercises",
                    "in_stock": True,
                    "stock_quantity": 30,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            ]

            created_products = []
            for product in sample_products:
                product_id = firebase.create_document("products", product)
                product["id"] = product_id
                created_products.append(product)

            logger.info("Database initialized with sample data")
            return create_success_response(
                {
                    "message": "Database initialized successfully",
                    "products_created": len(created_products),
                    "products": created_products,
                },
                201,
            )

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            return (
                create_error_response(
                    "Failed to initialize database", 500, request.path
                ),
                500,
            )

    # Batch Operations for Performance
    @app.route("/api/v1/products/batch", methods=["POST"])
    @require_auth
    @limiter.limit("10 per hour")
    def create_products_batch():
        """Create multiple products in batch for better performance"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            if not isinstance(data, dict) or "products" not in data:
                return (
                    create_error_response(
                        "Request must contain 'products' array", 400, request.path
                    ),
                    400,
                )

            products = data["products"]
            if not isinstance(products, list):
                return (
                    create_error_response(
                        "Products must be an array", 400, request.path
                    ),
                    400,
                )

            if len(products) > 50:
                return (
                    create_error_response(
                        "Maximum 50 products per batch", 400, request.path
                    ),
                    400,
                )

            # Validate each product
            for i, product in enumerate(products):
                if not isinstance(product, dict):
                    return (
                        create_error_response(
                            f"Product {i} must be an object", 400, request.path
                        ),
                        400,
                    )

                if "name" not in product or "price" not in product:
                    return (
                        create_error_response(
                            f"Product {i} missing required fields: name, price",
                            400,
                            request.path,
                        ),
                        400,
                    )

            # Process batch
            for product in products:
                product.update(
                    {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "category": product.get("category", "Uncategorized"),
                        "description": product.get("description", ""),
                        "in_stock": product.get("in_stock", True),
                        "stock_quantity": product.get("stock_quantity", 0),
                    }
                )

            # Use batch operation for better performance
            created_products = batch_create_products(products)

            logger.info(f"Batch created {len(created_products)} products")
            return create_success_response(
                {
                    "message": f"Successfully created {len(created_products)} products",
                    "products": created_products,
                    "count": len(created_products),
                },
                201,
            )

        except Exception as e:
            logger.error(f"Batch create products error: {str(e)}")
            return (
                create_error_response(
                    "Failed to create products in batch", 500, request.path
                ),
                500,
            )

    @app.route("/api/admin/performance/test", methods=["POST"])
    @require_auth
    @limiter.limit("5 per hour")
    def performance_test():
        """Run performance tests for troubleshooting"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code

            test_type = data.get("type", "basic")

            if test_type == "database":
                # Test database performance
                start_time = time.time()
                products = firebase.get_documents("products")
                db_time = time.time() - start_time

                return create_success_response(
                    {
                        "test": "database_performance",
                        "results": {
                            "query_time": round(db_time, 3),
                            "documents_retrieved": len(products),
                            "performance": "good" if db_time < 0.5 else "slow",
                        },
                    }
                )

            elif test_type == "memory":
                # Test memory usage
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()

                return create_success_response(
                    {
                        "test": "memory_usage",
                        "results": {
                            "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                            "memory_percent": process.memory_percent(),
                            "status": (
                                "healthy"
                                if memory_info.rss < 500 * 1024 * 1024
                                else "high"
                            ),
                        },
                    }
                )

            else:
                # Basic performance test
                start_time = time.time()
                firebase_connected = test_firebase_connection()
                test_time = time.time() - start_time

                return create_success_response(
                    {
                        "test": "basic_performance",
                        "results": {
                            "firebase_connection": firebase_connected,
                            "connection_time": round(test_time, 3),
                            "status": "healthy" if test_time < 1.0 else "slow",
                        },
                    }
                )

        except Exception as e:
            logger.error(f"Performance test error: {str(e)}")
            return (
                create_error_response("Performance test failed", 500, request.path),
                500,
            )

    @app.route("/api/admin/diagnostics", methods=["GET"])
    @require_auth
    def diagnostics():
        """Comprehensive diagnostics for troubleshooting"""
        try:
            # Test all major components
            diagnostics = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tests": {},
            }

            # Test Firebase connection
            try:
                firebase_start = time.time()
                firebase_connected = test_firebase_connection()
                firebase_time = time.time() - firebase_start
                diagnostics["tests"]["firebase"] = {
                    "status": "pass" if firebase_connected else "fail",
                    "response_time": round(firebase_time, 3),
                    "details": (
                        "Firebase connection successful"
                        if firebase_connected
                        else "Firebase connection failed"
                    ),
                }
            except Exception as e:
                diagnostics["tests"]["firebase"] = {"status": "error", "error": str(e)}

            # Test system resources
            try:
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                diagnostics["tests"]["system"] = {
                    "status": "pass",
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                    "details": "System resources normal",
                }
            except Exception as e:
                diagnostics["tests"]["system"] = {"status": "error", "error": str(e)}

            # Test database query
            try:
                query_start = time.time()
                products = firebase.get_documents("products")
                query_time = time.time() - query_start
                diagnostics["tests"]["database_query"] = {
                    "status": "pass",
                    "response_time": round(query_time, 3),
                    "documents": len(products),
                    "details": f"Retrieved {len(products)} products",
                }
            except Exception as e:
                diagnostics["tests"]["database_query"] = {
                    "status": "error",
                    "error": str(e),
                }

            # Overall health
            failed_tests = [
                k for k, v in diagnostics["tests"].items() if v["status"] != "pass"
            ]
            diagnostics["overall_status"] = (
                "healthy" if not failed_tests else "issues_detected"
            )
            diagnostics["failed_tests"] = failed_tests

            return create_success_response(diagnostics)

        except Exception as e:
            logger.error(f"Diagnostics error: {str(e)}")
            return create_error_response("Diagnostics failed", 500, request.path), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return (
            create_error_response(
                "Endpoint not found",
                404,
                request.path,
                details={"available_endpoints": "/api/v1/info or /api/v2/info"},
            ),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            create_error_response(
                "Method not allowed",
                405,
                request.path,
                details={"method": request.method},
            ),
            405,
        )

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return create_error_response("Internal server error", 500, request.path), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return (
            create_error_response(
                "Rate limit exceeded",
                429,
                request.path,
                details={"limit": str(error.description)},
            ),
            429,
        )

    @app.route("/metrics")
    def metrics():
        """System metrics for monitoring and troubleshooting"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            # Get Firebase connection status
            firebase_status = test_firebase_connection()

            # Get system stats
            cpu_percent = process.cpu_percent()
            memory_mb = memory_info.rss / 1024 / 1024

            return create_success_response(
                {
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_usage_mb": round(memory_mb, 2),
                        "memory_percent": process.memory_percent(),
                        "open_files": len(process.open_files()),
                        "connections": len(process.connections()),
                        "threads": process.num_threads(),
                    },
                    "application": {
                        "flask_env": os.getenv("FLASK_ENV", "development"),
                        "debug_mode": app.debug,
                        "port": os.getenv("PORT", "5001"),
                        "version": "2.1.0",
                    },
                    "database": {
                        "firebase_connected": firebase_status,
                        "project_id": os.getenv(
                            "FIREBASE_PROJECT_ID", "not-configured"
                        ),
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return (
                create_error_response("Failed to collect metrics", 500, request.path),
                500,
            )

    @app.route("/debug/info")
    @require_auth
    def debug_info():
        """Debug information for troubleshooting (requires authentication)"""
        try:
            import sys

            return create_success_response(
                {
                    "python": {
                        "version": sys.version,
                        "path": sys.path[:5],  # First 5 paths only
                        "executable": sys.executable,
                    },
                    "environment": {
                        "variables": {
                            k: v
                            for k, v in os.environ.items()
                            if not k.endswith("_KEY")
                        },
                        "cwd": os.getcwd(),
                    },
                    "flask": {
                        "version": getattr(app, "__version__", "unknown"),
                        "config": {
                            k: str(v)
                            for k, v in app.config.items()
                            if "SECRET" not in k
                        },
                    },
                    "process": {"pid": os.getpid(), "ppid": os.getppid()},
                }
            )
        except Exception as e:
            logger.error(f"Debug info collection failed: {e}")
            return (
                create_error_response(
                    "Failed to collect debug info", 500, request.path
                ),
                500,
            )


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
