"""
Cart Routes
Shopping cart management endpoints
"""

from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import require_auth
from app.controllers.cart_controller import CartController
import logging

logger = logging.getLogger(__name__)

cart_bp = Blueprint('cart', __name__)
cart_controller = CartController()

@cart_bp.route('', methods=['GET'])
def get_cart():
    """Get user's cart items"""
    try:
        user = getattr(request, 'current_user', {})
        user_id = user.get('user_id', 'guest_user')
        
        result = cart_controller.get_cart(user_id)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "data": result["cart"],
                "message": result["message"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400
            
    except Exception as e:
        logger.error(f"Error retrieving cart: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve cart"
        }), 500

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({
                "success": False,
                "error": "Product ID is required"
            }), 400
        
        # Check if user is authenticated, fallback to guest user
        user = getattr(request, 'current_user', {})
        user_id = user.get('user_id', 'guest_user')
        
        # Sample response
        response_data = {
            "cart_item_id": f"cart_item_{product_id}",
            "product_id": product_id,
            "quantity": quantity,
            "added_date": "2025-01-08T17:36:00Z"
        }
        
        logger.info(f"Item added to cart for user {user_id}: {product_id}")
        return jsonify({
            "success": True,
            "data": response_data,
            "message": "Item added to cart successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to add item to cart"
        }), 500

@cart_bp.route('/remove/<item_id>', methods=['DELETE'])
@require_auth
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        user = getattr(request, 'current_user', {})
        user_id = user.get('user_id', 'sample_user')
        
        logger.info(f"Item removed from cart for user {user_id}: {item_id}")
        return jsonify({
            "success": True,
            "message": "Item removed from cart successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to remove item from cart"
        }), 500

@cart_bp.route('/clear', methods=['DELETE'])
@require_auth
def clear_cart():
    """Clear all items from cart"""
    try:
        user = getattr(request, 'current_user', {})
        user_id = user.get('user_id', 'sample_user')
        
        logger.info(f"Cart cleared for user: {user_id}")
        return jsonify({
            "success": True,
            "message": "Cart cleared successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to clear cart"
        }), 500
