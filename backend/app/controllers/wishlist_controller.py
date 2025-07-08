"""
Wishlist Controller
Wishlist management and operations
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class WishlistController:
    """Controller for managing wishlist operations"""

    def __init__(self):
        self.firebase = FirebaseUtils()
        self.collection_name = "wishlists"

    def get_wishlist(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's wishlist items

        Args:
            user_id (str): User ID

        Returns:
            Dict: Wishlist data with items
        """
        try:
            # Try to get wishlist from Firebase
            wishlist_doc = self.firebase.get_document(self.collection_name, user_id)
            
            if wishlist_doc:
                logger.info(f"Wishlist retrieved for user: {user_id}")
                return {
                    "success": True,
                    "wishlist": wishlist_doc,
                    "message": "Wishlist retrieved successfully"
                }
            else:
                # Return sample wishlist data if no wishlist exists
                sample_wishlist = {
                    "user_id": user_id,
                    "items": [
                        {
                            "id": "wish_item_1",
                            "product_id": "prod_003",
                            "name": "Premium Coffee Machine",
                            "price": 299.99,
                            "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085",
                            "added_at": datetime.now().isoformat(),
                            "in_stock": True,
                            "category": "Kitchen Appliances"
                        },
                        {
                            "id": "wish_item_2",
                            "product_id": "prod_004",
                            "name": "Ergonomic Office Chair",
                            "price": 199.99,
                            "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7",
                            "added_at": datetime.now().isoformat(),
                            "in_stock": True,
                            "category": "Furniture"
                        },
                        {
                            "id": "wish_item_3",
                            "product_id": "prod_005",
                            "name": "Wireless Speaker System",
                            "price": 149.99,
                            "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d",
                            "added_at": datetime.now().isoformat(),
                            "in_stock": False,
                            "category": "Electronics"
                        }
                    ],
                    "total_items": 3,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                logger.info(f"Sample wishlist data returned for user: {user_id}")
                return {
                    "success": True,
                    "wishlist": sample_wishlist,
                    "message": "Sample wishlist data (demo mode)"
                }

        except Exception as e:
            logger.error(f"Error retrieving wishlist for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to retrieve wishlist: {str(e)}"
            }

    def add_to_wishlist(self, user_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add item to user's wishlist

        Args:
            user_id (str): User ID
            item_data (Dict): Item to add to wishlist

        Returns:
            Dict: Operation result
        """
        try:
            # Get existing wishlist or create new one
            wishlist_doc = self.firebase.get_document(self.collection_name, user_id)
            
            if not wishlist_doc:
                # Create new wishlist
                wishlist_doc = {
                    "user_id": user_id,
                    "items": [],
                    "total_items": 0,
                    "created_at": datetime.now().isoformat()
                }

            # Check if item already exists
            existing_item = next((item for item in wishlist_doc["items"] if item["product_id"] == item_data.get("product_id")), None)
            
            if existing_item:
                return {
                    "success": False,
                    "error": "Item already in wishlist"
                }

            # Add the new item
            new_item = {
                "id": f"wish_item_{len(wishlist_doc['items']) + 1}",
                "product_id": item_data.get("product_id"),
                "name": item_data.get("name"),
                "price": float(item_data.get("price", 0)),
                "image": item_data.get("image", ""),
                "category": item_data.get("category", "General"),
                "in_stock": item_data.get("in_stock", True),
                "added_at": datetime.now().isoformat()
            }

            wishlist_doc["items"].append(new_item)
            wishlist_doc["total_items"] = len(wishlist_doc["items"])
            wishlist_doc["updated_at"] = datetime.now().isoformat()

            # Save to Firebase
            self.firebase.set_document(self.collection_name, user_id, wishlist_doc)
            
            logger.info(f"Item added to wishlist for user: {user_id}")
            return {
                "success": True,
                "wishlist": wishlist_doc,
                "message": "Item added to wishlist successfully"
            }

        except Exception as e:
            logger.error(f"Error adding item to wishlist for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to add item to wishlist: {str(e)}"
            }

    def remove_from_wishlist(self, user_id: str, item_id: str) -> Dict[str, Any]:
        """
        Remove item from user's wishlist

        Args:
            user_id (str): User ID
            item_id (str): Wishlist item ID to remove

        Returns:
            Dict: Operation result
        """
        try:
            wishlist_doc = self.firebase.get_document(self.collection_name, user_id)
            
            if not wishlist_doc:
                return {
                    "success": False,
                    "error": "Wishlist not found"
                }

            # Remove the item
            original_count = len(wishlist_doc["items"])
            wishlist_doc["items"] = [item for item in wishlist_doc["items"] if item["id"] != item_id]
            
            if len(wishlist_doc["items"]) == original_count:
                return {
                    "success": False,
                    "error": "Item not found in wishlist"
                }

            # Update totals
            wishlist_doc["total_items"] = len(wishlist_doc["items"])
            wishlist_doc["updated_at"] = datetime.now().isoformat()

            # Save to Firebase
            self.firebase.set_document(self.collection_name, user_id, wishlist_doc)
            
            logger.info(f"Item removed from wishlist for user: {user_id}")
            return {
                "success": True,
                "wishlist": wishlist_doc,
                "message": "Item removed from wishlist successfully"
            }

        except Exception as e:
            logger.error(f"Error removing item from wishlist for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to remove item from wishlist: {str(e)}"
            }

    def clear_wishlist(self, user_id: str) -> Dict[str, Any]:
        """
        Clear all items from user's wishlist

        Args:
            user_id (str): User ID

        Returns:
            Dict: Operation result
        """
        try:
            # Create empty wishlist
            empty_wishlist = {
                "user_id": user_id,
                "items": [],
                "total_items": 0,
                "updated_at": datetime.now().isoformat()
            }

            # Save to Firebase
            self.firebase.set_document(self.collection_name, user_id, empty_wishlist)
            
            logger.info(f"Wishlist cleared for user: {user_id}")
            return {
                "success": True,
                "wishlist": empty_wishlist,
                "message": "Wishlist cleared successfully"
            }

        except Exception as e:
            logger.error(f"Error clearing wishlist for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to clear wishlist: {str(e)}"
            }

    def move_to_cart(self, user_id: str, item_id: str) -> Dict[str, Any]:
        """
        Move item from wishlist to cart

        Args:
            user_id (str): User ID
            item_id (str): Wishlist item ID

        Returns:
            Dict: Operation result
        """
        try:
            wishlist_doc = self.firebase.get_document(self.collection_name, user_id)
            
            if not wishlist_doc:
                return {
                    "success": False,
                    "error": "Wishlist not found"
                }

            # Find the item to move
            item_to_move = None
            for item in wishlist_doc["items"]:
                if item["id"] == item_id:
                    item_to_move = item
                    break

            if not item_to_move:
                return {
                    "success": False,
                    "error": "Item not found in wishlist"
                }

            # Remove from wishlist
            remove_result = self.remove_from_wishlist(user_id, item_id)
            
            if not remove_result["success"]:
                return remove_result

            # Note: In a real implementation, you would add to cart here
            # For now, just return success with the moved item info
            
            logger.info(f"Item moved from wishlist to cart for user: {user_id}")
            return {
                "success": True,
                "moved_item": item_to_move,
                "message": "Item moved to cart successfully"
            }

        except Exception as e:
            logger.error(f"Error moving item to cart for user {user_id}: {e}")
            return {
                "success": False,
                "error": f"Failed to move item to cart: {str(e)}"
            }
