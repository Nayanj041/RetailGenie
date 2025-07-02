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
