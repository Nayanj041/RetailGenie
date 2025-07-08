"""
Pricing Controller for RetailGenie
Handles dynamic pricing, discounts, and pricing strategies
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class PricingController:
    def __init__(self):
        """Initialize Pricing Controller"""
        self.firebase = FirebaseUtils()

    def get_product_pricing(self, product_id: str) -> Dict[str, Any]:
        """Get pricing information for a product"""
        try:
            # Get product from database
            product = self.firebase.get_document("products", product_id)

            if not product:
                return {"success": False, "error": "Product not found"}

            # Calculate dynamic pricing
            base_price = product.get("price", 0)

            pricing_info = {
                "product_id": product_id,
                "base_price": base_price,
                "current_price": base_price,
                "discount_percentage": 0,
                "pricing_strategy": "standard",
                "last_updated": datetime.now().isoformat(),
            }

            # Apply any active discounts
            discounts = self._get_active_discounts(product_id)
            if discounts:
                best_discount = max(discounts, key=lambda x: x.get("percentage", 0))
                discount_amount = base_price * (best_discount["percentage"] / 100)
                pricing_info.update(
                    {
                        "current_price": base_price - discount_amount,
                        "discount_percentage": best_discount["percentage"],
                        "discount_reason": best_discount.get("reason", "Special offer"),
                        "pricing_strategy": "discounted",
                    }
                )

            logger.info(f"Pricing retrieved for product {product_id}")
            return {"success": True, "data": pricing_info}

        except Exception as e:
            logger.error(f"Error getting product pricing: {str(e)}")
            return {"success": False, "error": str(e)}

    def apply_discount(
        self, product_id: str, discount_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a discount to a product"""
        try:
            discount = {
                "product_id": product_id,
                "percentage": discount_data.get("percentage", 0),
                "reason": discount_data.get("reason", "Manual discount"),
                "start_date": discount_data.get(
                    "start_date", datetime.now().isoformat()
                ),
                "end_date": discount_data.get("end_date"),
                "created_by": discount_data.get("created_by", "system"),
                "active": True,
                "created_at": datetime.now().isoformat(),
            }

            # Store discount
            discount_id = self.firebase.create_document("discounts", discount)

            logger.info(
                f"Discount applied to product {product_id}: {discount['percentage']}%"
            )
            return {"success": True, "discount_id": discount_id, "data": discount}

        except Exception as e:
            logger.error(f"Error applying discount: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_pricing_analytics(self) -> Dict[str, Any]:
        """Get pricing analytics and recommendations"""
        try:
            analytics = {
                "average_margin": 35.2,
                "total_discounts_active": 8,
                "revenue_impact": {
                    "discount_revenue": 2345.67,
                    "full_price_revenue": 8976.43,
                    "total_revenue": 11322.10,
                },
                "pricing_recommendations": [
                    {
                        "product_id": "prod_001",
                        "current_price": 24.99,
                        "recommended_price": 27.99,
                        "reason": "High demand, low stock",
                    },
                    {
                        "product_id": "prod_003",
                        "current_price": 15.99,
                        "recommended_price": 13.99,
                        "reason": "Slow moving inventory",
                    },
                ],
            }

            logger.info("Pricing analytics retrieved successfully")
            return {"success": True, "data": analytics}

        except Exception as e:
            logger.error(f"Error getting pricing analytics: {str(e)}")
            return {"success": False, "error": str(e)}

    def bulk_pricing_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update pricing for multiple products"""
        try:
            updated_products = []
            errors = []

            for update in updates:
                product_id = update.get("product_id")
                new_price = update.get("price")

                if not product_id or new_price is None:
                    errors.append(f"Invalid update data: {update}")
                    continue

                try:
                    # Update product price
                    self.firebase.update_document(
                        "products", product_id, {"price": new_price}
                    )
                    updated_products.append(product_id)

                except Exception as e:
                    errors.append(f"Failed to update {product_id}: {str(e)}")

            result = {
                "updated_count": len(updated_products),
                "updated_products": updated_products,
                "errors": errors,
            }

            logger.info(
                f"Bulk pricing update completed: {len(updated_products)} products updated"
            )
            return {"success": True, "data": result}

        except Exception as e:
            logger.error(f"Error in bulk pricing update: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_active_discounts(self, product_id: str) -> List[Dict[str, Any]]:
        """Get active discounts for a product"""
        try:
            # Query active discounts
            discounts = self.firebase.query_documents(
                "discounts", {"product_id": product_id, "active": True}
            )

            # Filter by date range
            now = datetime.now()
            active_discounts = []

            for discount in discounts:
                start_date = datetime.fromisoformat(
                    discount.get("start_date", now.isoformat())
                )
                end_date_str = discount.get("end_date")

                if start_date <= now:
                    if not end_date_str or datetime.fromisoformat(end_date_str) >= now:
                        active_discounts.append(discount)

            return active_discounts

        except Exception as e:
            logger.error(f"Error getting active discounts: {str(e)}")
            return []
