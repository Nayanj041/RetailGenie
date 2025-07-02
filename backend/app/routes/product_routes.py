from flask import Blueprint, jsonify, request

from app.controllers.product_controller import ProductController

product_bp = Blueprint("products", __name__)
product_controller = ProductController()


@product_bp.route("/", methods=["GET"])
def get_products():
    """Get all products with optional filters"""
    try:
        filters = request.args.to_dict()
        products = product_controller.get_products(filters)
        return (
            jsonify(
                {
                    "success": True,
                    "data": products,
                    "message": "Products retrieved successfully",
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
                    "message": "Failed to retrieve products",
                }
            ),
            500,
        )


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
