from flask import Blueprint, jsonify, request

from app.controllers.pricing_controller import PricingController

pricing_bp = Blueprint("pricing", __name__)
pricing_controller = PricingController()


@pricing_bp.route("/optimize", methods=["POST"])
def optimize_pricing():
    """Get dynamic pricing recommendations"""
    try:
        data = request.get_json()
        product_ids = data.get("product_ids", [])
        market_conditions = data.get("market_conditions", {})

        pricing_recommendations = pricing_controller.optimize_prices(
            product_ids, market_conditions
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": pricing_recommendations,
                    "message": "Pricing optimization completed successfully",
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
                    "message": "Failed to optimize pricing",
                }
            ),
            500,
        )


@pricing_bp.route("/competitor-analysis", methods=["GET"])
def get_competitor_analysis():
    """Get competitor pricing analysis"""
    try:
        product_id = request.args.get("product_id")

        if not product_id:
            return jsonify({"success": False, "message": "Product ID is required"}), 400

        analysis = pricing_controller.analyze_competitor_pricing(product_id)

        return (
            jsonify(
                {
                    "success": True,
                    "data": analysis,
                    "message": "Competitor analysis completed successfully",
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
                    "message": "Failed to analyze competitor pricing",
                }
            ),
            500,
        )


@pricing_bp.route("/demand-based", methods=["POST"])
def demand_based_pricing():
    """Calculate demand-based pricing"""
    try:
        data = request.get_json()
        product_id = data.get("product_id")
        demand_data = data.get("demand_data", {})

        pricing = pricing_controller.calculate_demand_based_pricing(
            product_id, demand_data
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": pricing,
                    "message": "Demand-based pricing calculated successfully",
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
                    "message": "Failed to calculate demand-based pricing",
                }
            ),
            500,
        )
