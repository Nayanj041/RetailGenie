from flask import Blueprint, jsonify, request

from app.controllers.analytics_controller import AnalyticsController

analytics_bp = Blueprint("analytics", __name__)
analytics_controller = AnalyticsController()


@analytics_bp.route("/dashboard", methods=["GET"])
def get_dashboard_data():
    """Get dashboard analytics data"""
    try:
        store_id = request.args.get("store_id")
        date_range = request.args.get("date_range", "7d")

        dashboard_data = analytics_controller.get_dashboard_analytics(
            store_id, date_range
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": dashboard_data,
                    "message": "Dashboard data retrieved successfully",
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
                    "message": "Failed to retrieve dashboard data",
                }
            ),
            500,
        )


@analytics_bp.route("/customer-insights", methods=["GET"])
def get_customer_insights():
    """Get customer behavior insights"""
    try:
        store_id = request.args.get("store_id")
        segment = request.args.get("segment", "all")

        insights = analytics_controller.get_customer_insights(store_id, segment)

        return (
            jsonify(
                {
                    "success": True,
                    "data": insights,
                    "message": "Customer insights retrieved successfully",
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
                    "message": "Failed to retrieve customer insights",
                }
            ),
            500,
        )


@analytics_bp.route("/performance/manager", methods=["GET"])
def get_manager_performance():
    """Get manager performance metrics"""
    try:
        manager_id = request.args.get("manager_id")
        period = request.args.get("period", "month")

        performance = analytics_controller.get_manager_performance(manager_id, period)

        return (
            jsonify(
                {
                    "success": True,
                    "data": performance,
                    "message": "Manager performance retrieved successfully",
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
                    "message": "Failed to retrieve performance data",
                }
            ),
            500,
        )


@analytics_bp.route("/reports/generate", methods=["POST"])
def generate_report():
    """Generate analytics report"""
    try:
        data = request.get_json()
        report_type = data.get("report_type", "daily")
        store_id = data.get("store_id")
        email_recipients = data.get("email_recipients", [])

        report_path = analytics_controller.generate_analytics_report(
            report_type, store_id, email_recipients
        )

        return (
            jsonify(
                {
                    "success": True,
                    "data": {"report_path": report_path},
                    "message": "Report generated successfully",
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
                    "message": "Failed to generate report",
                }
            ),
            500,
        )


@analytics_bp.route("/gamification/leaderboard", methods=["GET"])
def get_gamification_leaderboard():
    """Get manager gamification leaderboard"""
    try:
        region = request.args.get("region")
        period = request.args.get("period", "month")

        leaderboard = analytics_controller.get_gamification_leaderboard(region, period)

        return (
            jsonify(
                {
                    "success": True,
                    "data": leaderboard,
                    "message": "Leaderboard retrieved successfully",
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
                    "message": "Failed to retrieve leaderboard",
                }
            ),
            500,
        )


@analytics_bp.route("/", methods=["GET"])
@analytics_bp.route("", methods=["GET"])
def get_analytics():
    """Get general analytics data"""
    try:
        time_range = request.args.get("time_range", "7d")

        # Get analytics data from controller
        analytics_data = analytics_controller.get_general_analytics(time_range)

        return jsonify(
            {"success": True, "data": analytics_data, "message": "Analytics retrieved successfully"}
        ), 200

    except Exception as e:
        # Return fallback analytics data
        fallback_data = {
            "overview": {
                "total_revenue": 15750.00,
                "revenue_change": 12.5,
                "total_orders": 156,
                "orders_change": 8.3,
                "total_customers": 89,
                "customers_change": 15.2,
                "conversion_rate": 3.2,
                "conversion_change": -0.5,
            },
            "sales_trend": [
                {"date": "2025-07-01", "revenue": 2100, "orders": 28},
                {"date": "2025-07-02", "revenue": 2350, "orders": 32},
                {"date": "2025-07-03", "revenue": 1980, "orders": 25},
                {"date": "2025-07-04", "revenue": 2200, "orders": 29},
                {"date": "2025-07-05", "revenue": 2400, "orders": 34},
                {"date": "2025-07-06", "revenue": 2150, "orders": 30},
                {"date": "2025-07-07", "revenue": 2570, "orders": 38},
            ],
            "top_products": [
                {"name": "Coffee Beans", "sales": 45, "revenue": 899.55},
                {"name": "Organic Tea", "sales": 32, "revenue": 415.68},
                {"name": "Artisan Chocolate", "sales": 28, "revenue": 251.72},
            ],
            "category_distribution": [
                {"name": "Electronics", "value": 5200},
                {"name": "Clothing", "value": 3800},
                {"name": "Books", "value": 2100},
                {"name": "Home", "value": 2900},
                {"name": "Sports", "value": 1650},
            ],
            "customer_segments": [
                {"segment": "Premium", "customers": 23, "avg_order_value": 125.50},
                {"segment": "Regular", "customers": 45, "avg_order_value": 78.30},
                {"segment": "New", "customers": 21, "avg_order_value": 45.20},
            ],
            "time_range": time_range,
        }

        return (
            jsonify(
                {
                    "success": True,
                    "data": fallback_data,
                    "message": "Analytics retrieved successfully (sample data)",
                }
            ),
            200,
        )


@analytics_bp.route("/ml-analysis", methods=["GET"])
def get_ml_product_analysis():
    """Get ML-powered product analysis"""
    try:
        store_id = request.args.get("store_id")
        
        ml_analysis = analytics_controller.get_ml_product_analysis(store_id)
        
        return jsonify({
            "success": True,
            "data": ml_analysis["data"],
            "message": "ML product analysis completed successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to generate ML analysis"
        }), 500

@analytics_bp.route("/product-insights", methods=["GET"])
def get_product_insights():
    """Get AI-powered product insights and recommendations"""
    try:
        product_id = request.args.get("product_id")
        
        if product_id:
            # Get insights for specific product
            ml_analysis = analytics_controller.get_ml_product_analysis()
            if ml_analysis["success"]:
                product_data = {}
                for key in ["demand_forecasting", "sentiment_analysis", "pricing_recommendations"]:
                    if product_id in ml_analysis["data"].get(key, {}):
                        product_data[key] = ml_analysis["data"][key][product_id]
                
                # Find product insights
                product_insights = next(
                    (p for p in ml_analysis["data"].get("product_insights", []) if p["product_id"] == product_id),
                    None
                )
                
                return jsonify({
                    "success": True,
                    "product_id": product_id,
                    "insights": product_insights,
                    "detailed_analysis": product_data,
                    "message": f"Product insights for {product_id}"
                }), 200
            else:
                return jsonify(ml_analysis), 500
        else:
            # Get insights for all products
            ml_analysis = analytics_controller.get_ml_product_analysis()
            return jsonify(ml_analysis), 200 if ml_analysis["success"] else 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve product insights"
        }), 500

@analytics_bp.route("/inventory-alerts", methods=["GET"])
def get_inventory_alerts():
    """Get ML-powered inventory alerts"""
    try:
        ml_analysis = analytics_controller.get_ml_product_analysis()
        
        if ml_analysis["success"]:
            alerts = ml_analysis["data"].get("inventory_alerts", [])
            critical_alerts = [a for a in alerts if a.get("alert_level") == "critical"]
            warning_alerts = [a for a in alerts if a.get("alert_level") == "warning"]
            
            return jsonify({
                "success": True,
                "alerts": {
                    "critical": critical_alerts,
                    "warning": warning_alerts,
                    "total": len(alerts)
                },
                "summary": {
                    "critical_count": len(critical_alerts),
                    "warning_count": len(warning_alerts),
                    "total_alerts": len(alerts)
                },
                "message": "Inventory alerts retrieved successfully"
            }), 200
        else:
            return jsonify(ml_analysis), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve inventory alerts"
        }), 500
