from flask import Blueprint, jsonify, request

from app.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)
auth_controller = AuthController()


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        required_fields = ["email", "password", "name"]
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

        result = auth_controller.register_user(data)
        return (
            jsonify(
                {
                    "success": True,
                    "data": result,
                    "message": "User registered successfully",
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": str(e), "message": "Registration failed"}
            ),
            500,
        )


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login"""
    try:
        data = request.get_json()

        required_fields = ["email", "password"]
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

        result = auth_controller.login_user(data["email"], data["password"])
        return (
            jsonify({"success": True, "data": result, "message": "Login successful"}),
            200,
        )
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 401
    except Exception as e:
        return (
            jsonify({"success": False, "error": str(e), "message": "Login failed"}),
            500,
        )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """User logout"""
    try:
        token = request.headers.get("Authorization")
        if not token:
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        auth_controller.logout_user(token)
        return jsonify({"success": True, "message": "Logout successful"}), 200
    except Exception as e:
        return (
            jsonify({"success": False, "error": str(e), "message": "Logout failed"}),
            500,
        )


@auth_bp.route("/profile", methods=["GET"])
def get_profile():
    """Get user profile"""
    try:
        token = request.headers.get("Authorization")
        if not token:
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        profile = auth_controller.get_user_profile(token)
        return (
            jsonify(
                {
                    "success": True,
                    "data": profile,
                    "message": "Profile retrieved successfully",
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 401
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to retrieve profile",
                }
            ),
            500,
        )


@auth_bp.route("/profile", methods=["PUT"])
def update_profile():
    """Update user profile"""
    try:
        token = request.headers.get("Authorization")
        if not token:
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        data = request.get_json()
        updated_profile = auth_controller.update_user_profile(token, data)

        return (
            jsonify(
                {
                    "success": True,
                    "data": updated_profile,
                    "message": "Profile updated successfully",
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 401
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to update profile",
                }
            ),
            500,
        )
