"""
Cart Controller
Shopping cart management and operations
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class CartController:
    """Controller for managing shopping cart operations"""

    def __init__(self):
        self.firebase = FirebaseUtils()
        self.collection_name = "carts"

    def get_cart(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's cart items

        Args:
            user_id (str): User ID

        Returns:
            Dict: Cart data with items
        """
        try:
            # Try to get cart from Firebase
            cart_doc = self.firebase.get_document(self.collection_name, user_id)
            
            if cart_doc:
                logger.info(f"Cart retrieved for user: {user_id}")
                return {
                    "success": True,
                    "cart": cart_doc,
                    "message": "Cart retrieved successfully"
                }
            else:
                # Return sample cart data if no cart exists
                sample_cart = {
                    "user_id": user_id,
                    "items": [
                        {
                            "id": "cart_item_1",
                            "product_id": "prod_001",
                            "name": "Wireless Bluetooth Headphones",
                            "price": 79.99,
                            "quantity": 1,
                            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
                            "added_at": datetime.now().isoformat()
                        },
                        {
                            "id": "cart_item_2",
                            "product_id": "prod_002",
                            "name": "Smart Fitness Watch",
                            "price": 199.99,
                            "quantity": 1,
                            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
                            "added_at": datetime.now().isoformat()
                        }
                    ],
                    "total_items": 2,
                    "total_amount": 279.98,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                logger.info(f"Sample cart data returned for user: {user_id}")
                return {
                    "success": True,
                    "cart": sample_cart,
                    "message": "Sample cart data (demo mode)"
                }

        except Exception as e:
            logger.error(f"Error retrieving cart for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to retrieve cart: {str(e)}"
            }

    def add_to_cart(self, user_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add item to user's cart

        Args:
            user_id (str): User ID
            item_data (Dict): Item to add to cart

        Returns:
            Dict: Operation result
        """
        try:
            # Get existing cart or create new one
            cart_doc = self.firebase.get_document(self.collection_name, user_id)
            
            if not cart_doc:
                # Create new cart
                cart_doc = {
                    "user_id": user_id,
                    "items": [],
                    "total_items": 0,
                    "total_amount": 0.0,
                    "created_at": datetime.now().isoformat()
                }

            # Add the new item
            new_item = {
                "id": f"cart_item_{len(cart_doc['items']) + 1}",
                "product_id": item_data.get("product_id"),
                "name": item_data.get("name"),
                "price": float(item_data.get("price", 0)),
                "quantity": int(item_data.get("quantity", 1)),
                "image": item_data.get("image", ""),
                "added_at": datetime.now().isoformat()
            }

            cart_doc["items"].append(new_item)
            cart_doc["total_items"] = len(cart_doc["items"])
            cart_doc["total_amount"] = sum(item["price"] * item["quantity"] for item in cart_doc["items"])
            cart_doc["updated_at"] = datetime.now().isoformat()

            # Save to Firebase
            self.firebase.set_document(self.collection_name, user_id, cart_doc)
            
            logger.info(f"Item added to cart for user: {user_id}")
            return {
                "success": True,
                "cart": cart_doc,
                "message": "Item added to cart successfully"
            }

        except Exception as e:
            logger.error(f"Error adding item to cart for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to add item to cart: {str(e)}"
            }

    def update_cart_item(self, user_id: str, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update cart item quantity or details

        Args:
            user_id (str): User ID
            item_id (str): Cart item ID
            update_data (Dict): Update data

        Returns:
            Dict: Operation result
        """
        try:
            cart_doc = self.firebase.get_document(self.collection_name, user_id)
            
            if not cart_doc:
                return {
                    "success": False,
                    "error": "Cart not found"
                }

            # Find and update the item
            item_found = False
            for item in cart_doc["items"]:
                if item["id"] == item_id:
                    if "quantity" in update_data:
                        item["quantity"] = int(update_data["quantity"])
                    item_found = True
                    break

            if not item_found:
                return {
                    "success": False,
                    "error": "Item not found in cart"
                }

            # Recalculate totals
            cart_doc["total_items"] = len(cart_doc["items"])
            cart_doc["total_amount"] = sum(item["price"] * item["quantity"] for item in cart_doc["items"])
            cart_doc["updated_at"] = datetime.now().isoformat()

            # Save to Firebase
            self.firebase.set_document(self.collection_name, user_id, cart_doc)
            
            logger.info(f"Cart item updated for user: {user_id}")
            return {
                "success": True,
                "cart": cart_doc,
                "message": "Cart item updated successfully"
            }

        except Exception as e:
            logger.error(f"Error updating cart item for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to update cart item: {str(e)}"
            }

    def remove_from_cart(self, user_id: str, item_id: str) -> Dict[str, Any]:
        """
        Remove item from user's cart

        Args:
            user_id (str): User ID
            item_id (str): Cart item ID to remove

        Returns:
            Dict: Operation result
        """
        try:
            cart_doc = self.firebase.get_document(self.collection_name, user_id)
            
            if not cart_doc:
                return {
                    "success": False,
                    "error": "Cart not found"
                }

            # Remove the item
            original_count = len(cart_doc["items"])
            cart_doc["items"] = [item for item in cart_doc["items"] if item["id"] != item_id]
            
            if len(cart_doc["items"]) == original_count:
                return {
                    "success": False,
                    "error": "Item not found in cart"
                }

            # Recalculate totals
            cart_doc["total_items"] = len(cart_doc["items"])
            cart_doc["total_amount"] = sum(item["price"] * item["quantity"] for item in cart_doc["items"])
            cart_doc["updated_at"] = datetime.now().isoformat()

            # Save to Firebase
            self.firebase.set_document(self.collection_name, user_id, cart_doc)
            
            logger.info(f"Item removed from cart for user: {user_id}")
            return {
                "success": True,
                "cart": cart_doc,
                "message": "Item removed from cart successfully"
            }

        except Exception as e:
            logger.error(f"Error removing item from cart for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to remove item from cart: {str(e)}"
            }

    def clear_cart(self, user_id: str) -> Dict[str, Any]:
        """
        Clear all items from user's cart

        Args:
            user_id (str): User ID

        Returns:
            Dict: Operation result
        """
        try:
            # Create empty cart
            empty_cart = {
                "user_id": user_id,
                "items": [],
                "total_items": 0,
                "total_amount": 0.0,
                "updated_at": datetime.now().isoformat()
            }

            # Save to Firebase
            self.firebase.set_document(self.collection_name, user_id, empty_cart)
            
            logger.info(f"Cart cleared for user: {user_id}")
            return {
                "success": True,
                "cart": empty_cart,
                "message": "Cart cleared successfully"
            }

        except Exception as e:
            logger.error(f"Error clearing cart for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to clear cart: {str(e)}"
            }
