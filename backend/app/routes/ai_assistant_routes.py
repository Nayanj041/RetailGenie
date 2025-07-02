from flask import Blueprint, jsonify, request

from app.controllers.ai_assistant_controller import AIAssistantController

ai_assistant_bp = Blueprint("ai_assistant", __name__)
ai_assistant = AIAssistantController()


@ai_assistant_bp.route("/chat", methods=["POST"])
def chat_with_assistant():
    """Chat with AI shopping assistant"""
    try:
        data = request.get_json()
        message = data.get("message")
        user_id = data.get("user_id")
        context = data.get("context", {})

        if not message:
            return jsonify({"success": False, "message": "Message is required"}), 400

        response = ai_assistant.process_chat_message(message, user_id, context)

        return (
            jsonify(
                {
                    "success": True,
                    "data": response,
                    "message": "Chat response generated successfully",
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
                    "message": "Failed to process chat message",
                }
            ),
            500,
        )


@ai_assistant_bp.route("/voice", methods=["POST"])
def process_voice_command():
    """Process voice command from user"""
    try:
        # Handle voice file upload and processing
        if "audio" not in request.files:
            return jsonify({"success": False, "message": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        user_id = request.form.get("user_id")
        language = request.form.get("language", "en")

        response = ai_assistant.process_voice_command(audio_file, user_id, language)

        return (
            jsonify(
                {
                    "success": True,
                    "data": response,
                    "message": "Voice command processed successfully",
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
                    "message": "Failed to process voice command",
                }
            ),
            500,
        )


@ai_assistant_bp.route("/substitute", methods=["POST"])
def find_substitutes():
    """Find product substitutes"""
    try:
        data = request.get_json()
        product_id = data.get("product_id")
        preferences = data.get("preferences", {})

        if not product_id:
            return jsonify({"success": False, "message": "Product ID is required"}), 400

        substitutes = ai_assistant.find_product_substitutes(product_id, preferences)

        return (
            jsonify(
                {
                    "success": True,
                    "data": substitutes,
                    "message": "Product substitutes found successfully",
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
                    "message": "Failed to find substitutes",
                }
            ),
            500,
        )


@ai_assistant_bp.route("/coupons/optimize", methods=["POST"])
def optimize_coupons():
    """Get optimized coupon recommendations"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        cart_items = data.get("cart_items", [])

        if not user_id:
            return jsonify({"success": False, "message": "User ID is required"}), 400

        coupons = ai_assistant.optimize_coupons(user_id, cart_items)

        return (
            jsonify(
                {
                    "success": True,
                    "data": coupons,
                    "message": "Optimized coupons retrieved successfully",
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
                    "message": "Failed to optimize coupons",
                }
            ),
            500,
        )


@ai_assistant_bp.route("/sustainability/score", methods=["POST"])
def calculate_sustainability_score():
    """Calculate sustainability score for cart"""
    try:
        data = request.get_json()
        cart_items = data.get("cart_items", [])

        if not cart_items:
            return (
                jsonify({"success": False, "message": "Cart items are required"}),
                400,
            )

        score_data = ai_assistant.calculate_sustainability_score(cart_items)

        return (
            jsonify(
                {
                    "success": True,
                    "data": score_data,
                    "message": "Sustainability score calculated successfully",
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
                    "message": "Failed to calculate sustainability score",
                }
            ),
            500,
        )
