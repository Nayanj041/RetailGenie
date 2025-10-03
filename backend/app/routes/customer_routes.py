from flask import Blueprint, jsonify, request
from datetime import datetime

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handle_customers():
    """Handle customer listing and creation"""
    if request.method == 'OPTIONS':
        response = jsonify({"message": "OK"})
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response

    try:
        from app.utils.firebase_utils import FirebaseUtils
        firebase = FirebaseUtils()

        if request.method == 'GET':
            # Get all customers
            customers = firebase.get_documents("customers") or []
            return jsonify({
                "success": True,
                "customers": customers,
                "count": len(customers)
            }), 200

        elif request.method == 'POST':
            # Create new customer
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400

            required_fields = ["name", "email"]
            if not all(field in data for field in required_fields):
                return jsonify({"success": False, "error": "Missing required fields"}), 400

            customer_data = {
                **data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            customer_id = firebase.create_document("customers", customer_data)
            return jsonify({
                "success": True,
                "customer_id": customer_id,
                "customer": customer_data,
                "message": "Customer created successfully"
            }), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@customer_bp.route('/<customer_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def handle_customer(customer_id):
    """Handle individual customer operations"""
    if request.method == 'OPTIONS':
        response = jsonify({"message": "OK"})
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,DELETE,OPTIONS')
        return response

    try:
        from app.utils.firebase_utils import FirebaseUtils
        firebase = FirebaseUtils()

        if request.method == 'GET':
            # Get customer details
            customer = firebase.get_document("customers", customer_id)
            if not customer:
                return jsonify({"success": False, "error": "Customer not found"}), 404

            return jsonify({
                "success": True,
                "customer": customer
            }), 200

        elif request.method == 'PUT':
            # Update customer
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400

            customer = firebase.get_document("customers", customer_id)
            if not customer:
                return jsonify({"success": False, "error": "Customer not found"}), 404

            updated_data = {
                **customer,
                **data,
                "updated_at": datetime.now().isoformat()
            }

            firebase.update_document("customers", customer_id, updated_data)
            return jsonify({
                "success": True,
                "customer": updated_data,
                "message": "Customer updated successfully"
            }), 200

        elif request.method == 'DELETE':
            # Delete customer
            customer = firebase.get_document("customers", customer_id)
            if not customer:
                return jsonify({"success": False, "error": "Customer not found"}), 404

            firebase.delete_document("customers", customer_id)
            return jsonify({
                "success": True,
                "message": "Customer deleted successfully"
            }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500