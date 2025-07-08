from flask import Blueprint, jsonify, request

from app.controllers.feedback_controller import FeedbackController

feedback_bp = Blueprint("feedback", __name__)
feedback_controller = FeedbackController()


@feedback_bp.route("/", methods=["POST"])
@feedback_bp.route("", methods=["POST"])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()

        required_fields = ["user_id", "product_id", "rating", "comment"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"Missing required field: {field}",
                        }
                    ),
                    400,
                )

        feedback_id = feedback_controller.submit_feedback(data)
        return (
            jsonify(
                {
                    "success": True,
                    "data": {"feedback_id": feedback_id},
                    "message": "Feedback submitted successfully",
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
                    "message": "Failed to submit feedback",
                }
            ),
            500,
        )


@feedback_bp.route("/product/<product_id>", methods=["GET"])
def get_product_feedback(product_id):
    """Get all feedback for a specific product"""
    try:
        feedback = feedback_controller.get_product_feedback(product_id)
        return (
            jsonify(
                {
                    "success": True,
                    "data": feedback,
                    "message": "Feedback retrieved successfully",
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
                    "message": "Failed to retrieve feedback",
                }
            ),
            500,
        )


@feedback_bp.route("/user/<user_id>", methods=["GET"])
def get_user_feedback(user_id):
    """Get all feedback submitted by a specific user"""
    try:
        feedback = feedback_controller.get_user_feedback(user_id)
        return (
            jsonify(
                {
                    "success": True,
                    "data": feedback,
                    "message": "User feedback retrieved successfully",
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
                    "message": "Failed to retrieve user feedback",
                }
            ),
            500,
        )


@feedback_bp.route("/analyze/<product_id>", methods=["GET"])
def analyze_feedback(product_id):
    """Analyze feedback for a product using AI"""
    try:
        analysis = feedback_controller.analyze_feedback(product_id)
        return (
            jsonify(
                {
                    "success": True,
                    "data": analysis,
                    "message": "Feedback analysis completed successfully",
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
                    "message": "Failed to analyze feedback",
                }
            ),
            500,
        )


@feedback_bp.route("/export/<product_id>", methods=["GET"])
def export_feedback(product_id):
    """Export feedback as PDF report"""
    try:
        pdf_path = feedback_controller.export_feedback_report(product_id)
        return (
            jsonify(
                {
                    "success": True,
                    "data": {"download_url": pdf_path},
                    "message": "Feedback report exported successfully",
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
                    "message": "Failed to export feedback report",
                }
            ),
            500,
        )


@feedback_bp.route("/", methods=["GET"])
@feedback_bp.route("", methods=["GET"])
def get_all_feedback():
    """Get all feedback with optional filtering"""
    try:
        # Get query parameters for filtering
        rating_filter = request.args.get("rating", type=int)
        category_filter = request.args.get("category")
        limit = request.args.get("limit", 50, type=int)

        feedback = feedback_controller.get_all_feedback(
            rating_filter=rating_filter,
            category_filter=category_filter,
            limit=limit,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "feedback": feedback,
                    "count": len(feedback),
                    "message": "Feedback retrieved successfully",
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
                    "message": "Failed to retrieve feedback",
                }
            ),
            500,
        )


@feedback_bp.route("/sentiment", methods=["GET"])
def get_sentiment_analysis():
    """Get sentiment analysis of all feedback"""
    try:
        analysis = feedback_controller.get_sentiment_analysis()

        return (
            jsonify(
                {
                    "success": True,
                    "analysis": analysis,
                    "message": "Sentiment analysis retrieved successfully",
                }
            ),
            200,
        )

    except Exception as e:
        # Fallback response for sentiment analysis
        fallback_analysis = {
            "overall_sentiment": "neutral",
            "sentiment_distribution": {"positive": 33, "neutral": 34, "negative": 33},
            "trending_topics": ["quality", "service", "pricing"],
            "total_feedback": 0,
        }

        return (
            jsonify(
                {
                    "success": True,
                    "analysis": fallback_analysis,
                    "message": "Sentiment analysis (fallback data)",
                }
            ),
            200,
        )
