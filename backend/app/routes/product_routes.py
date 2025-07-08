from flask import Blueprint, jsonify, request

from app.controllers.product_controller import ProductController

product_bp = Blueprint("products", __name__)
product_controller = ProductController()


@product_bp.route("/", methods=["GET"])
def get_products():
    """Get all products with optional filters"""
    try:
        filters = request.args.to_dict()
        products = product_controller.get_products(filters) or []
        
        # If no products exist, return sample data
        if not products:
            products = [
                {
                    "id": "sample_001",
                    "name": "Sample Coffee Beans",
                    "description": "Premium arabica coffee beans",
                    "category": "Beverages",
                    "price": 19.99,
                    "stock_quantity": 100,
                    "sku": "COFFEE-001",
                    "status": "active",
                    "image_url": "/api/placeholder/product1.jpg"
                },
                {
                    "id": "sample_002", 
                    "name": "Organic Tea",
                    "description": "Premium organic green tea",
                    "category": "Beverages",
                    "price": 12.99,
                    "stock_quantity": 75,
                    "sku": "TEA-001",
                    "status": "active",
                    "image_url": "/api/placeholder/product2.jpg"
                },
                {
                    "id": "sample_003",
                    "name": "Artisan Chocolate",
                    "description": "Handcrafted dark chocolate",
                    "category": "Food",
                    "price": 8.99,
                    "stock_quantity": 50,
                    "sku": "CHOC-001", 
                    "status": "active",
                    "image_url": "/api/placeholder/product3.jpg"
                }
            ]
        
        return jsonify({
            "success": True,
            "data": products,
            "count": len(products),
            "message": "Products retrieved successfully" + (" (sample data)" if not product_controller.get_products(filters) else "")
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve products"
        }), 500


@product_bp.route("/<product_id>", methods=["GET"])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = product_controller.get_product_by_id(product_id)
        if not product:
            return jsonify({"success": False, "message": "Product not found"}), 404

        return (
            jsonify(
                {
                    "success": True,
                    "data": product,
                    "message": "Product retrieved successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to retrieve product",
                }
            ),
            500,
        )


@product_bp.route("/search", methods=["POST"])
def search_products():
    """Search products using AI-powered search"""
    try:
        data = request.get_json()
        query = data.get("query", "")

        if not query:
            return (
                jsonify({"success": False, "message": "Search query is required"}),
                400,
            )

        results = product_controller.search_products(query)
        return (
            jsonify(
                {
                    "success": True,
                    "data": results,
                    "message": "Search completed successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify({"success": False, "error": str(e), "message": "Search failed"}),
            500,
        )


@product_bp.route("/recommendations", methods=["POST"])
def get_recommendations():
    """Get AI-powered product recommendations"""
    try:
        data = request.get_json()
        user_preferences = data.get("preferences", {})

        recommendations = product_controller.get_recommendations(user_preferences)
        return (
            jsonify(
                {
                    "success": True,
                    "data": recommendations,
                    "message": "Recommendations generated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to generate recommendations",
                }
            ),
            500,
        )


@product_bp.route("/", methods=["POST"])
def create_product():
    """Create a new product"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            # Handle form data (including file uploads)
            data = request.form.to_dict()

            # Handle file upload if present
            if "image" in request.files:
                file = request.files["image"]
                if file and file.filename:
                    # In a real implementation, save the file and store the path
                    data["image_url"] = f"/uploads/{file.filename}"

        # Validate required fields
        required_fields = ["name", "price", "category"]
        for field in required_fields:
            if field not in data or not data[field]:
                return (
                    jsonify(
                        {"success": False, "message": f"Missing required field: {field}"}
                    ),
                    400,
                )

        # Create the product
        product_id = product_controller.create_product(data)

        return (
            jsonify(
                {
                    "success": True,
                    "data": {"product_id": product_id},
                    "message": "Product created successfully",
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to create product",
                }
            ),
            500,
        )
