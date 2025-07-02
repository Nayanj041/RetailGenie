"""
RetailGenie Complete Advanced Backend - Part 2
All remaining advanced endpoints (Products, Inventory, Orders, Customers, Analytics, AI, Pricing, Feedback)
"""

import uuid
import bcrypt
from datetime import datetime, timedelta
from flask import request, jsonify

def add_all_advanced_endpoints(app, firebase, controllers, require_auth, get_json_data, logger, generate_jwt_token):
    """Add ALL advanced endpoints to the Flask app"""
    
    # ===== PRODUCTS ENDPOINTS =====
    
    @app.route("/api/v1/products", methods=["GET"])
    def get_all_products():
        """Get all products with advanced filtering and pagination"""
        try:
            # Get query parameters
            category = request.args.get('category')
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            in_stock = request.args.get('in_stock', type=bool)
            sort_by = request.args.get('sort_by', 'name')
            order = request.args.get('order', 'asc')
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            if "product" in controllers:
                result = controllers["product"].get_products({
                    'category': category,
                    'min_price': min_price,
                    'max_price': max_price,
                    'in_stock': in_stock,
                    'sort_by': sort_by,
                    'order': order,
                    'limit': limit,
                    'offset': offset
                })
                return jsonify(result)
            else:
                # Enhanced fallback implementation
                products = firebase.get_documents("products") or []
                
                # Apply filters
                if category:
                    products = [p for p in products if p.get('category', '').lower() == category.lower()]
                if min_price is not None:
                    products = [p for p in products if p.get('price', 0) >= min_price]
                if max_price is not None:
                    products = [p for p in products if p.get('price', 0) <= max_price]
                if in_stock:
                    products = [p for p in products if p.get('stock', 0) > 0]
                
                # Sort products
                if sort_by in ['name', 'price', 'stock', 'created_at']:
                    reverse = order.lower() == 'desc'
                    products.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)
                
                # Apply pagination
                total = len(products)
                products = products[offset:offset + limit]
                
                return jsonify({
                    "success": True,
                    "data": products,
                    "pagination": {
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                        "has_more": offset + limit < total
                    },
                    "filters_applied": {
                        "category": category,
                        "min_price": min_price,
                        "max_price": max_price,
                        "in_stock": in_stock
                    }
                })
                
        except Exception as e:
            logger.error(f"Get products error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products", methods=["POST"])
    @require_auth
    def create_product():
        """Create new product with validation"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            if "product" in controllers:
                result = controllers["product"].create_product(data)
                return jsonify(result), 201 if result.get("success") else 400
            else:
                # Enhanced fallback implementation
                required_fields = ['name', 'price', 'category']
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({"success": False, "error": f"{field} is required"}), 400
                
                product_data = {
                    "id": str(uuid.uuid4()),
                    "name": data.get("name"),
                    "description": data.get("description", ""),
                    "price": float(data.get("price")),
                    "category": data.get("category"),
                    "stock": int(data.get("stock", 0)),
                    "sku": data.get("sku", f"SKU-{uuid.uuid4().hex[:8].upper()}"),
                    "status": data.get("status", "active"),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "created_by": request.user.get("user_id")
                }
                
                product_id = firebase.create_document("products", product_data)
                
                return jsonify({
                    "success": True,
                    "product_id": product_id,
                    "product": product_data,
                    "message": "Product created successfully"
                }), 201
                
        except Exception as e:
            logger.error(f"Create product error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products/<product_id>", methods=["GET"])
    def get_product_by_id(product_id):
        """Get product by ID with detailed information"""
        try:
            if "product" in controllers:
                result = controllers["product"].get_product_by_id(product_id)
                return jsonify(result)
            else:
                product = firebase.get_document("products", product_id)
                if product:
                    # Add additional computed fields
                    product["value"] = product.get("price", 0) * product.get("stock", 0)
                    product["status_display"] = product.get("status", "active").title()
                    
                    return jsonify({
                        "success": True,
                        "product": product
                    })
                else:
                    return jsonify({"success": False, "error": "Product not found"}), 404
                    
        except Exception as e:
            logger.error(f"Get product error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products/<product_id>", methods=["PUT"])
    @require_auth
    def update_product(product_id):
        """Update product with validation"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            if "product" in controllers:
                result = controllers["product"].update_product(product_id, data)
                return jsonify(result)
            else:
                # Check if product exists
                existing_product = firebase.get_document("products", product_id)
                if not existing_product:
                    return jsonify({"success": False, "error": "Product not found"}), 404
                
                # Update fields
                update_data = {
                    "updated_at": datetime.now().isoformat(),
                    "updated_by": request.user.get("user_id")
                }
                
                # Only update provided fields
                for field in ['name', 'description', 'price', 'category', 'stock', 'status']:
                    if field in data:
                        if field == 'price':
                            update_data[field] = float(data[field])
                        elif field == 'stock':
                            update_data[field] = int(data[field])
                        else:
                            update_data[field] = data[field]
                
                firebase.update_document("products", product_id, update_data)
                
                # Get updated product
                updated_product = firebase.get_document("products", product_id)
                
                return jsonify({
                    "success": True,
                    "product": updated_product,
                    "message": "Product updated successfully"
                })
                
        except Exception as e:
            logger.error(f"Update product error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products/<product_id>", methods=["DELETE"])
    @require_auth
    def delete_product(product_id):
        """Delete product (soft delete)"""
        try:
            if "product" in controllers:
                result = controllers["product"].delete_product(product_id)
                return jsonify(result)
            else:
                # Check if product exists
                product = firebase.get_document("products", product_id)
                if not product:
                    return jsonify({"success": False, "error": "Product not found"}), 404
                
                # Soft delete by updating status
                firebase.update_document("products", product_id, {
                    "status": "deleted",
                    "deleted_at": datetime.now().isoformat(),
                    "deleted_by": request.user.get("user_id")
                })
                
                return jsonify({
                    "success": True,
                    "message": "Product deleted successfully"
                })
                
        except Exception as e:
            logger.error(f"Delete product error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products/search", methods=["GET"])
    def search_products():
        """Advanced product search"""
        try:
            query = request.args.get('q', '')
            category = request.args.get('category')
            limit = request.args.get('limit', 20, type=int)
            
            if "product" in controllers:
                result = controllers["product"].search_products({
                    'query': query,
                    'category': category,
                    'limit': limit
                })
                return jsonify(result)
            else:
                products = firebase.get_documents("products") or []
                
                # Filter by search query
                if query:
                    query_lower = query.lower()
                    products = [p for p in products 
                              if query_lower in p.get('name', '').lower() 
                              or query_lower in p.get('description', '').lower()
                              or query_lower in p.get('category', '').lower()]
                
                # Filter by category
                if category:
                    products = [p for p in products if p.get('category', '').lower() == category.lower()]
                
                # Only active products
                products = [p for p in products if p.get('status') != 'deleted']
                
                # Limit results
                products = products[:limit]
                
                return jsonify({
                    "success": True,
                    "query": query,
                    "category": category,
                    "results": products,
                    "count": len(products)
                })
                
        except Exception as e:
            logger.error(f"Search products error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products/categories", methods=["GET"])
    def get_product_categories():
        """Get all product categories"""
        try:
            if "product" in controllers:
                result = controllers["product"].get_categories()
                return jsonify(result)
            else:
                products = firebase.get_documents("products") or []
                categories = list(set(p.get('category') for p in products if p.get('category')))
                categories.sort()
                
                # Count products per category
                category_counts = {}
                for category in categories:
                    count = len([p for p in products if p.get('category') == category and p.get('status') != 'deleted'])
                    category_counts[category] = count
                
                return jsonify({
                    "success": True,
                    "categories": categories,
                    "category_counts": category_counts,
                    "total_categories": len(categories)
                })
                
        except Exception as e:
            logger.error(f"Get categories error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ===== INVENTORY ENDPOINTS =====
    
    @app.route("/api/v1/inventory", methods=["GET"])
    def get_inventory_status():
        """Get comprehensive inventory status"""
        try:
            if "inventory" in controllers:
                result = controllers["inventory"].get_inventory_status()
                return jsonify(result)
            else:
                products = firebase.get_documents("products") or []
                active_products = [p for p in products if p.get('status') != 'deleted']
                
                total_products = len(active_products)
                total_stock = sum(p.get('stock', 0) for p in active_products)
                total_value = sum(p.get('price', 0) * p.get('stock', 0) for p in active_products)
                
                low_stock_threshold = 10
                low_stock_items = [p for p in active_products if p.get('stock', 0) < low_stock_threshold]
                out_of_stock_items = [p for p in active_products if p.get('stock', 0) == 0]
                
                return jsonify({
                    "success": True,
                    "inventory_summary": {
                        "total_products": total_products,
                        "total_stock": total_stock,
                        "total_value": total_value,
                        "low_stock_count": len(low_stock_items),
                        "out_of_stock_count": len(out_of_stock_items)
                    },
                    "alerts": {
                        "low_stock": len(low_stock_items),
                        "out_of_stock": len(out_of_stock_items)
                    },
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Get inventory status error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/inventory/low-stock", methods=["GET"])
    def get_low_stock_items():
        """Get items with low stock levels"""
        try:
            threshold = request.args.get('threshold', 10, type=int)
            
            if "inventory" in controllers:
                result = controllers["inventory"].get_low_stock_items(threshold)
                return jsonify(result)
            else:
                products = firebase.get_documents("products") or []
                low_stock_items = [
                    p for p in products 
                    if p.get('status') != 'deleted' and p.get('stock', 0) < threshold
                ]
                
                # Sort by stock level (lowest first)
                low_stock_items.sort(key=lambda x: x.get('stock', 0))
                
                return jsonify({
                    "success": True,
                    "threshold": threshold,
                    "low_stock_items": low_stock_items,
                    "count": len(low_stock_items),
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Get low stock items error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/inventory/update", methods=["POST"])
    @require_auth
    def update_inventory():
        """Update inventory levels for multiple products"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            updates = data.get('updates', [])
            if not updates:
                return jsonify({"success": False, "error": "No updates provided"}), 400
            
            if "inventory" in controllers:
                result = controllers["inventory"].update_inventory(updates)
                return jsonify(result)
            else:
                results = []
                for update in updates:
                    product_id = update.get('product_id')
                    new_stock = update.get('stock')
                    
                    if not product_id or new_stock is None:
                        results.append({
                            "product_id": product_id,
                            "success": False,
                            "error": "product_id and stock required"
                        })
                        continue
                    
                    try:
                        # Check if product exists
                        product = firebase.get_document("products", product_id)
                        if not product:
                            results.append({
                                "product_id": product_id,
                                "success": False,
                                "error": "Product not found"
                            })
                            continue
                        
                        # Update stock
                        firebase.update_document("products", product_id, {
                            "stock": int(new_stock),
                            "updated_at": datetime.now().isoformat(),
                            "updated_by": request.user.get("user_id")
                        })
                        
                        results.append({
                            "product_id": product_id,
                            "success": True,
                            "old_stock": product.get("stock", 0),
                            "new_stock": int(new_stock)
                        })
                        
                    except Exception as e:
                        results.append({
                            "product_id": product_id,
                            "success": False,
                            "error": str(e)
                        })
                
                successful_updates = len([r for r in results if r.get("success")])
                
                return jsonify({
                    "success": True,
                    "message": f"Updated {successful_updates}/{len(updates)} products",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Update inventory error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ===== AI ASSISTANT ENDPOINTS =====
    
    @app.route("/api/v1/ai/chat", methods=["POST"])
    def ai_chat():
        """Chat with AI assistant"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            message = data.get('message')
            if not message:
                return jsonify({"success": False, "error": "Message is required"}), 400
            
            if "ai" in controllers:
                result = controllers["ai"].chat(message, data.get('context', {}))
                return jsonify(result)
            else:
                # Simple fallback AI response
                responses = [
                    "I'm here to help with your retail management needs!",
                    "Based on your data, I recommend focusing on inventory optimization.",
                    "Your sales trends show growth potential in the electronics category.",
                    "Consider implementing dynamic pricing for seasonal items.",
                    "Customer feedback suggests improving product descriptions."
                ]
                
                import random
                response = random.choice(responses)
                
                return jsonify({
                    "success": True,
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                    "context": "retail_assistant"
                })
                
        except Exception as e:
            logger.error(f"AI chat error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/ai/recommendations", methods=["GET"])
    def ai_recommendations():
        """Get AI-powered business recommendations"""
        try:
            category = request.args.get('category', 'general')
            
            if "ai" in controllers:
                result = controllers["ai"].get_recommendations(category)
                return jsonify(result)
            else:
                # Generate sample recommendations based on category
                recommendations = {
                    "general": [
                        "Focus on top-selling product categories",
                        "Implement customer loyalty programs",
                        "Optimize inventory turnover rates",
                        "Analyze seasonal sales patterns"
                    ],
                    "inventory": [
                        "Set up automated reorder points",
                        "Monitor slow-moving inventory",
                        "Implement just-in-time ordering",
                        "Use demand forecasting models"
                    ],
                    "pricing": [
                        "Implement dynamic pricing strategies",
                        "Monitor competitor pricing",
                        "Use psychological pricing tactics",
                        "Optimize discount strategies"
                    ],
                    "marketing": [
                        "Target high-value customers",
                        "Implement personalized recommendations",
                        "Use email marketing automation",
                        "Leverage social media analytics"
                    ]
                }
                
                category_recommendations = recommendations.get(category, recommendations["general"])
                
                return jsonify({
                    "success": True,
                    "category": category,
                    "recommendations": category_recommendations,
                    "generated_at": datetime.now().isoformat(),
                    "confidence": 0.85
                })
                
        except Exception as e:
            logger.error(f"AI recommendations error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/ai/insights", methods=["GET"])
    def ai_insights():
        """Get AI business insights"""
        try:
            if "ai" in controllers:
                result = controllers["ai"].get_insights()
                return jsonify(result)
            else:
                # Generate sample insights
                products = firebase.get_documents("products") or []
                active_products = [p for p in products if p.get('status') != 'deleted']
                
                insights = []
                
                if active_products:
                    # Calculate some basic insights
                    avg_price = sum(p.get('price', 0) for p in active_products) / len(active_products)
                    total_value = sum(p.get('price', 0) * p.get('stock', 0) for p in active_products)
                    
                    insights.extend([
                        f"Average product price: ${avg_price:.2f}",
                        f"Total inventory value: ${total_value:.2f}",
                        f"Product catalog contains {len(active_products)} active items",
                        "Consider diversifying product categories for better market coverage"
                    ])
                else:
                    insights.append("No products found. Start by adding some products to your catalog.")
                
                return jsonify({
                    "success": True,
                    "insights": insights,
                    "analysis_date": datetime.now().isoformat(),
                    "data_points_analyzed": len(active_products)
                })
                
        except Exception as e:
            logger.error(f"AI insights error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ===== ANALYTICS ENDPOINTS =====
    
    @app.route("/api/v1/analytics/dashboard", methods=["GET"])
    def analytics_dashboard():
        """Get comprehensive dashboard analytics"""
        try:
            if "analytics" in controllers:
                result = controllers["analytics"].get_dashboard_data()
                return jsonify(result)
            else:
                # Generate dashboard analytics from available data
                products = firebase.get_documents("products") or []
                orders = firebase.get_documents("orders") or []
                customers = firebase.get_documents("customers") or []
                
                active_products = [p for p in products if p.get('status') != 'deleted']
                
                dashboard_data = {
                    "overview": {
                        "total_products": len(active_products),
                        "total_orders": len(orders),
                        "total_customers": len(customers),
                        "total_revenue": sum(o.get('total', 0) for o in orders),
                        "average_order_value": sum(o.get('total', 0) for o in orders) / len(orders) if orders else 0
                    },
                    "inventory": {
                        "total_stock": sum(p.get('stock', 0) for p in active_products),
                        "inventory_value": sum(p.get('price', 0) * p.get('stock', 0) for p in active_products),
                        "low_stock_count": len([p for p in active_products if p.get('stock', 0) < 10])
                    },
                    "recent_activity": {
                        "recent_orders": len([o for o in orders if o.get('created_at', '') > (datetime.now() - timedelta(days=7)).isoformat()]),
                        "new_customers": len([c for c in customers if c.get('created_at', '') > (datetime.now() - timedelta(days=30)).isoformat()])
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                return jsonify({
                    "success": True,
                    "dashboard": dashboard_data
                })
                
        except Exception as e:
            logger.error(f"Analytics dashboard error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ===== PRICING ENDPOINTS =====
    
    @app.route("/api/v1/pricing/products/<product_id>", methods=["GET"])
    def get_product_pricing(product_id):
        """Get detailed pricing information for a product"""
        try:
            if "pricing" in controllers:
                result = controllers["pricing"].get_product_pricing(product_id)
                return jsonify(result)
            else:
                product = firebase.get_document("products", product_id)
                if not product:
                    return jsonify({"success": False, "error": "Product not found"}), 404
                
                pricing_data = {
                    "product_id": product_id,
                    "current_price": product.get('price', 0),
                    "cost": product.get('cost', product.get('price', 0) * 0.7),  # Estimated cost
                    "margin": product.get('price', 0) * 0.3,  # Estimated margin
                    "margin_percentage": 30.0,
                    "recommended_price": product.get('price', 0) * 1.05,  # 5% increase suggestion
                    "competitor_average": product.get('price', 0) * 0.95,  # Estimated competitor price
                    "last_updated": datetime.now().isoformat()
                }
                
                return jsonify({
                    "success": True,
                    "pricing": pricing_data
                })
                
        except Exception as e:
            logger.error(f"Get product pricing error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ===== FEEDBACK ENDPOINTS =====
    
    @app.route("/api/v1/feedback", methods=["GET"])
    def get_all_feedback():
        """Get all customer feedback"""
        try:
            if "feedback" in controllers:
                result = controllers["feedback"].get_all_feedback()
                return jsonify(result)
            else:
                feedback_list = firebase.get_documents("feedback") or []
                
                # Sort by created_at (newest first)
                feedback_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                
                return jsonify({
                    "success": True,
                    "feedback": feedback_list,
                    "count": len(feedback_list),
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Get feedback error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/feedback", methods=["POST"])
    def submit_feedback():
        """Submit new customer feedback"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            if "feedback" in controllers:
                result = controllers["feedback"].submit_feedback(data)
                return jsonify(result), 201 if result.get("success") else 400
            else:
                required_fields = ['message', 'rating']
                for field in required_fields:
                    if not data.get(field):
                        return jsonify({"success": False, "error": f"{field} is required"}), 400
                
                feedback_data = {
                    "id": str(uuid.uuid4()),
                    "message": data.get("message"),
                    "rating": int(data.get("rating")),
                    "customer_name": data.get("customer_name", "Anonymous"),
                    "customer_email": data.get("customer_email"),
                    "product_id": data.get("product_id"),
                    "category": data.get("category", "general"),
                    "status": "new",
                    "created_at": datetime.now().isoformat()
                }
                
                feedback_id = firebase.create_document("feedback", feedback_data)
                
                return jsonify({
                    "success": True,
                    "feedback_id": feedback_id,
                    "message": "Feedback submitted successfully"
                }), 201
                
        except Exception as e:
            logger.error(f"Submit feedback error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ===== ORDERS ENDPOINTS =====
    
    @app.route("/api/v1/orders", methods=["GET"])
    def get_all_orders():
        """Get all orders with filtering"""
        try:
            status = request.args.get('status')
            customer_id = request.args.get('customer_id')
            limit = request.args.get('limit', 50, type=int)
            
            orders = firebase.get_documents("orders") or []
            
            # Apply filters
            if status:
                orders = [o for o in orders if o.get('status') == status]
            if customer_id:
                orders = [o for o in orders if o.get('customer_id') == customer_id]
            
            # Sort by created_at (newest first)
            orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Limit results
            orders = orders[:limit]
            
            return jsonify({
                "success": True,
                "orders": orders,
                "count": len(orders),
                "filters": {"status": status, "customer_id": customer_id}
            })
            
        except Exception as e:
            logger.error(f"Get orders error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/orders", methods=["POST"])
    @require_auth
    def create_order():
        """Create new order"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            required_fields = ['customer_id', 'items']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"success": False, "error": f"{field} is required"}), 400
            
            items = data.get('items', [])
            if not items:
                return jsonify({"success": False, "error": "Order must contain at least one item"}), 400
            
            # Calculate order total
            total = 0
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                
                # Get product price
                product = firebase.get_document("products", product_id)
                if product:
                    price = product.get('price', 0)
                    item['price'] = price
                    item['subtotal'] = price * quantity
                    total += item['subtotal']
            
            order_data = {
                "id": str(uuid.uuid4()),
                "customer_id": data.get("customer_id"),
                "items": items,
                "total": total,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "created_by": request.user.get("user_id")
            }
            
            order_id = firebase.create_document("orders", order_data)
            
            return jsonify({
                "success": True,
                "order_id": order_id,
                "order": order_data,
                "message": "Order created successfully"
            }), 201
            
        except Exception as e:
            logger.error(f"Create order error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ===== CUSTOMERS ENDPOINTS =====
    
    @app.route("/api/v1/customers", methods=["GET"])
    def get_all_customers():
        """Get all customers"""
        try:
            customers = firebase.get_documents("customers") or []
            
            # Sort by created_at (newest first)
            customers.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return jsonify({
                "success": True,
                "customers": customers,
                "count": len(customers)
            })
            
        except Exception as e:
            logger.error(f"Get customers error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/customers", methods=["POST"])
    @require_auth
    def create_customer():
        """Create new customer"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            required_fields = ['name', 'email']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"success": False, "error": f"{field} is required"}), 400
            
            customer_data = {
                "id": str(uuid.uuid4()),
                "name": data.get("name"),
                "email": data.get("email"),
                "phone": data.get("phone"),
                "address": data.get("address"),
                "created_at": datetime.now().isoformat(),
                "created_by": request.user.get("user_id")
            }
            
            customer_id = firebase.create_document("customers", customer_data)
            
            return jsonify({
                "success": True,
                "customer_id": customer_id,
                "customer": customer_data,
                "message": "Customer created successfully"
            }), 201
            
        except Exception as e:
            logger.error(f"Create customer error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    return app


# This file contains endpoint definitions to be imported by the main app
