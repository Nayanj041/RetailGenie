import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from app.controllers.ai_engine import AIEngine
from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class InventoryController:
    def __init__(self):
        self.ai_engine = AIEngine()
        self.firebase = FirebaseUtils()
        self.inventory_collection = "inventory"
        self.sales_collection = "sales"

    def forecast_demand(self, product_ids, days_ahead=30):
        """
        Generate demand forecast using LSTM/ARIMA models

        Args:
            product_ids (list): List of product IDs to forecast
            days_ahead (int): Number of days to forecast ahead

        Returns:
            dict: Forecast data for each product
        """
        try:
            forecasts = {}

            for product_id in product_ids:
                # Get historical sales data
                sales_data = self._get_historical_sales(product_id)

                if len(sales_data) < 30:  # Need at least 30 days of data
                    forecasts[product_id] = {
                        "forecast": [],
                        "confidence": "low",
                        "message": "Insufficient historical data",
                    }
                    continue

                # Generate forecast using AI engine
                forecast = self.ai_engine.forecast_demand(sales_data, days_ahead)

                forecasts[product_id] = {
                    "forecast": forecast,
                    "confidence": "high" if len(sales_data) > 90 else "medium",
                    "historical_average": np.mean(sales_data),
                    "trend": self._calculate_trend(sales_data),
                }

            return forecasts
        except Exception as e:
            logger.error(f"Error forecasting demand: {str(e)}")
            raise

    def get_optimization_recommendations(self, store_id):
        """
        Get inventory optimization recommendations

        Args:
            store_id (str): Store ID

        Returns:
            dict: Optimization recommendations
        """
        try:
            # Get current inventory levels
            inventory_data = self.firebase.get_documents(
                self.inventory_collection, {"store_id": store_id}
            )

            recommendations = {
                "reorder_needed": [],
                "overstock_items": [],
                "fast_moving": [],
                "slow_moving": [],
                "optimization_score": 0,
            }

            for item in inventory_data:
                product_id = item.get("product_id")
                current_stock = item.get("current_stock", 0)

                # Get sales velocity
                velocity = self._calculate_sales_velocity(product_id, store_id)

                # Calculate reorder point
                reorder_point = self._calculate_reorder_point(
                    velocity, item.get("lead_time", 7)
                )

                if current_stock <= reorder_point:
                    recommendations["reorder_needed"].append(
                        {
                            "product_id": product_id,
                            "current_stock": current_stock,
                            "reorder_point": reorder_point,
                            "suggested_order_quantity": self._calculate_optimal_order_quantity(
                                velocity
                            ),
                        }
                    )
                elif current_stock > velocity * 60:  # More than 60 days of stock
                    recommendations["overstock_items"].append(
                        {
                            "product_id": product_id,
                            "current_stock": current_stock,
                            "days_of_stock": current_stock / max(velocity, 1),
                            "suggested_action": (
                                "promotion"
                                if current_stock > velocity * 90
                                else "reduce_orders"
                            ),
                        }
                    )

                # Categorize by movement speed
                if velocity > 10:  # Fast moving
                    recommendations["fast_moving"].append(product_id)
                elif velocity < 1:  # Slow moving
                    recommendations["slow_moving"].append(product_id)

            # Calculate optimization score
            total_items = len(inventory_data)
            well_stocked = (
                total_items
                - len(recommendations["reorder_needed"])
                - len(recommendations["overstock_items"])
            )
            recommendations["optimization_score"] = (
                well_stocked / max(total_items, 1)
            ) * 100

            return recommendations
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {str(e)}")
            raise

    def get_stock_alerts(self, store_id):
        """
        Get stock alerts for low stock and overstock situations

        Args:
            store_id (str): Store ID

        Returns:
            dict: Stock alerts
        """
        try:
            inventory_data = self.firebase.get_documents(
                self.inventory_collection, {"store_id": store_id}
            )

            alerts = {
                "critical_low": [],
                "low_stock": [],
                "overstock": [],
                "out_of_stock": [],
            }

            for item in inventory_data:
                current_stock = item.get("current_stock", 0)
                product_id = item.get("product_id")

                # Get sales velocity for context
                velocity = self._calculate_sales_velocity(product_id, store_id)

                if current_stock == 0:
                    alerts["out_of_stock"].append(
                        {
                            "product_id": product_id,
                            "last_sale": self._get_last_sale_date(product_id, store_id),
                            "priority": "high" if velocity > 5 else "medium",
                        }
                    )
                elif current_stock <= velocity * 3:  # Less than 3 days of stock
                    alerts["critical_low"].append(
                        {
                            "product_id": product_id,
                            "current_stock": current_stock,
                            "days_remaining": current_stock / max(velocity, 1),
                            "priority": "urgent",
                        }
                    )
                elif current_stock <= velocity * 7:  # Less than 7 days of stock
                    alerts["low_stock"].append(
                        {
                            "product_id": product_id,
                            "current_stock": current_stock,
                            "days_remaining": current_stock / max(velocity, 1),
                            "priority": "high",
                        }
                    )
                elif current_stock > velocity * 60:  # More than 60 days of stock
                    alerts["overstock"].append(
                        {
                            "product_id": product_id,
                            "current_stock": current_stock,
                            "days_of_stock": current_stock / max(velocity, 1),
                            "priority": "medium",
                        }
                    )

            return alerts
        except Exception as e:
            logger.error(f"Error getting stock alerts: {str(e)}")
            raise

    def get_geo_insights(self, region):
        """
        Get geographic inventory insights

        Args:
            region (str): Geographic region

        Returns:
            dict: Geographic insights
        """
        try:
            # Get stores in the region
            stores = self.firebase.query_documents("stores", "region", "==", region)

            insights = {
                "region": region,
                "total_stores": len(stores),
                "inventory_distribution": {},
                "performance_by_store": [],
                "regional_trends": {},
            }

            for store in stores:
                store_id = store.get("id")

                # Get inventory data for this store
                inventory = self.firebase.get_documents(
                    self.inventory_collection, {"store_id": store_id}
                )

                # Calculate store performance metrics
                total_value = sum(
                    item.get("current_stock", 0) * item.get("unit_cost", 0)
                    for item in inventory
                )
                turnover_rate = self._calculate_inventory_turnover(store_id)

                insights["performance_by_store"].append(
                    {
                        "store_id": store_id,
                        "store_name": store.get("name"),
                        "inventory_value": total_value,
                        "turnover_rate": turnover_rate,
                        "stock_health": self._assess_stock_health(store_id),
                    }
                )

            # Calculate regional trends
            insights["regional_trends"] = self._calculate_regional_trends(region)

            return insights
        except Exception as e:
            logger.error(f"Error getting geo insights: {str(e)}")
            raise

    def _get_historical_sales(self, product_id, days=90):
        """Get historical sales data for a product"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            sales = self.firebase.query_documents(
                self.sales_collection, "product_id", "==", product_id
            )

            # Filter by date range and aggregate by day
            daily_sales = {}
            for sale in sales:
                sale_date = sale.get("date", "")
                if sale_date:
                    try:
                        sale_datetime = datetime.fromisoformat(
                            sale_date.replace("Z", "+00:00")
                        )
                        if start_date <= sale_datetime <= end_date:
                            day_key = sale_datetime.strftime("%Y-%m-%d")
                            daily_sales[day_key] = daily_sales.get(
                                day_key, 0
                            ) + sale.get("quantity", 0)
                    except:
                        continue

            # Convert to list of daily quantities
            sales_data = []
            current_date = start_date
            while current_date <= end_date:
                day_key = current_date.strftime("%Y-%m-%d")
                sales_data.append(daily_sales.get(day_key, 0))
                current_date += timedelta(days=1)

            return sales_data
        except Exception as e:
            logger.error(f"Error getting historical sales: {str(e)}")
            return []

    def _calculate_sales_velocity(self, product_id, store_id):
        """Calculate average daily sales velocity"""
        try:
            sales_data = self._get_historical_sales(product_id, 30)
            return np.mean(sales_data) if sales_data else 0
        except:
            return 0

    def _calculate_reorder_point(self, velocity, lead_time):
        """Calculate reorder point based on velocity and lead time"""
        safety_stock = velocity * 3  # 3 days of safety stock
        return (velocity * lead_time) + safety_stock

    def _calculate_optimal_order_quantity(self, velocity):
        """Calculate optimal order quantity using EOQ approximation"""
        # Simplified EOQ calculation
        # In practice, this would include holding costs, ordering costs, etc.
        return max(velocity * 30, 10)  # At least 30 days of stock or minimum 10 units

    def _calculate_trend(self, sales_data):
        """Calculate sales trend (increasing, decreasing, stable)"""
        if len(sales_data) < 10:
            return "insufficient_data"

        recent_avg = np.mean(sales_data[-10:])
        older_avg = (
            np.mean(sales_data[-30:-20])
            if len(sales_data) >= 30
            else np.mean(sales_data[:-10])
        )

        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def _get_last_sale_date(self, product_id, store_id):
        """Get the date of the last sale for a product"""
        try:
            sales = self.firebase.query_documents(
                self.sales_collection, "product_id", "==", product_id
            )

            store_sales = [s for s in sales if s.get("store_id") == store_id]
            if store_sales:
                # Sort by date and get the most recent
                store_sales.sort(key=lambda x: x.get("date", ""), reverse=True)
                return store_sales[0].get("date", "Unknown")

            return "No sales recorded"
        except:
            return "Unknown"

    def _calculate_inventory_turnover(self, store_id):
        """Calculate inventory turnover rate for a store"""
        try:
            # Get cost of goods sold (COGS) for the period
            # This is simplified - in practice would use actual COGS calculation
            return 6.0  # Placeholder - represents 6x annual turnover
        except:
            return 0.0

    def _assess_stock_health(self, store_id):
        """Assess overall stock health for a store"""
        try:
            alerts = self.get_stock_alerts(store_id)

            total_issues = (
                len(alerts["out_of_stock"]) * 3  # Weight out of stock heavily
                + len(alerts["critical_low"]) * 2
                + len(alerts["low_stock"]) * 1
                + len(alerts["overstock"]) * 0.5
            )

            if total_issues == 0:
                return "excellent"
            elif total_issues <= 2:
                return "good"
            elif total_issues <= 5:
                return "fair"
            else:
                return "poor"
        except:
            return "unknown"

    def _calculate_regional_trends(self, region):
        """Calculate regional inventory trends"""
        try:
            # This would analyze regional patterns, seasonal trends, etc.
            # Placeholder implementation
            return {
                "demand_pattern": "seasonal",
                "peak_months": ["November", "December"],
                "growth_rate": 5.2,
                "category_preferences": ["Electronics", "Clothing", "Home"],
            }
        except:
            return {}
