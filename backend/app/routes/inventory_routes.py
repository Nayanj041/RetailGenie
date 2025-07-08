from flask import Blueprint, jsonify, request

from app.controllers.inventory_controller import InventoryController

inventory_bp = Blueprint("inventory", __name__)
inventory_controller = InventoryController()


@inventory_bp.route("/forecast", methods=["POST"])
def forecast_demand():
    """Generate demand forecast for products"""
    try:
        data = request.get_json()
        product_ids = data.get("product_ids", [])
        days_ahead = data.get("days_ahead", 30)

        forecasts = inventory_controller.forecast_demand(product_ids, days_ahead)

        return (
            jsonify(
                {
                    "success": True,
                    "data": forecasts,
                    "message": "Demand forecast generated successfully",
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
                    "message": "Failed to generate forecast",
                }
            ),
            500,
        )


@inventory_bp.route("/optimization", methods=["POST"])
def optimize_inventory():
    """Get inventory optimization recommendations"""
    try:
        data = request.get_json()
        store_id = data.get("store_id")

        recommendations = inventory_controller.get_optimization_recommendations(
            store_id
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": recommendations,
                    "message": "Optimization recommendations generated",
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


@inventory_bp.route("/stock-alerts", methods=["GET"])
def get_stock_alerts():
    """Get low stock and overstock alerts"""
    try:
        store_id = request.args.get("store_id")
        alerts = inventory_controller.get_stock_alerts(store_id)

        return (
            jsonify(
                {
                    "success": True,
                    "data": alerts,
                    "message": "Stock alerts retrieved successfully",
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
                    "message": "Failed to retrieve alerts",
                }
            ),
            500,
        )


@inventory_bp.route("/geo-insights", methods=["GET"])
def get_geo_insights():
    """Get geographic inventory insights"""
    try:
        region = request.args.get("region")
        insights = inventory_controller.get_geo_insights(region)

        return (
            jsonify(
                {
                    "success": True,
                    "data": insights,
                    "message": "Geographic insights retrieved successfully",
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
                    "message": "Failed to retrieve insights",
                }
            ),
            500,
        )


@inventory_bp.route("/", methods=["GET"])
def get_inventory():
    """Get all inventory items"""
    try:
        # Get query parameters for filtering
        category = request.args.get("category")
        low_stock = request.args.get("low_stock", type=bool)

        items = inventory_controller.get_all_inventory(
            category_filter=category, low_stock_only=low_stock
        )

        return (
            jsonify(
                {
                    "success": True,
                    "items": items,
                    "count": len(items),
                    "message": "Inventory retrieved successfully",
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
                    "message": "Failed to retrieve inventory",
                }
            ),
            500,
        )


@inventory_bp.route("/", methods=["POST"])
def add_inventory_item():
    """Add new inventory item"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["name", "sku", "quantity", "price"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify(
                        {"success": False, "message": f"Missing required field: {field}"}
                    ),
                    400,
                )

        item_id = inventory_controller.add_inventory_item(data)

        return (
            jsonify(
                {
                    "success": True,
                    "data": {"item_id": item_id},
                    "message": "Inventory item added successfully",
                }
            ),
            201,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to add inventory item",
                }
            ),
            500,
        )
