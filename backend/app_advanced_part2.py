"""
RetailGenie Advanced Backend - Part 2
All remaining advanced endpoints and features
"""

def add_advanced_endpoints(app, firebase, controllers, require_auth, get_json_data, logger):
    """Add all advanced endpoints to the Flask app"""
    
    # ===== PRODUCTS ENDPOINTS =====
    
    @app.route("/api/v1/products", methods=["GET"])
    def get_all_products():
        """Get all products with advanced filtering"""
        try:
            # Get query parameters
            category = request.args.get('category')
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            in_stock = request.args.get('in_stock', type=bool)
            limit = request.args.get('limit', 50, type=int)
            
            if "product" in controllers:
                result = controllers["product"].get_products({
                    'category': category,
                    'min_price': min_price,
                    'max_price': max_price,
                    'in_stock': in_stock,
                    'limit': limit
                })
                return jsonify(result)
            else:
                # Fallback implementation with filtering
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
                
                # Limit results
                products = products[:limit]
                
                return jsonify({
                    "success": True,
                    "data": products,
                    "count": len(products),
                    "filters_applied": {
                        "category": category,
                        "price_range": [min_price, max_price],
                        "in_stock_only": in_stock
                    }
                })
                
        except Exception as e:
            logger.error(f"Get products error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products", methods=["POST"])
    @require_auth
    def create_product():
        """Create new product (requires authentication)"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            if "product" in controllers:
                result = controllers["product"].create_product(data)
                return jsonify(result), 201 if result.get("success") else 400
            else:
                # Fallback implementation
                required_fields = ['name', 'price', 'category']
                if not all(field in data for field in required_fields):
                    return jsonify({"success": False, "error": "Missing required fields"}), 400
                
                product_data = {
                    "id": str(uuid.uuid4()),
                    "name": data.get("name"),
                    "description": data.get("description", ""),
                    "price": float(data.get("price")),
                    "category": data.get("category"),
                    "stock": int(data.get("stock", 0)),
                    "sku": data.get("sku", f"SKU-{uuid.uuid4().hex[:8].upper()}"),
                    "created_at": datetime.now().isoformat(),
                    "created_by": request.user.get("user_id"),
                    "status": "active"
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
        """Get specific product by ID"""
        try:
            if "product" in controllers:
                result = controllers["product"].get_product_by_id(product_id)
                return jsonify(result)
            else:
                product = firebase.get_document("products", product_id)
                if product:
                    return jsonify({"success": True, "data": product})
                else:
                    return jsonify({"success": False, "error": "Product not found"}), 404
                    
        except Exception as e:
            logger.error(f"Get product error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products/<product_id>", methods=["PUT"])
    @require_auth
    def update_product(product_id):
        """Update product (requires authentication)"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            if "product" in controllers:
                result = controllers["product"].update_product(product_id, data)
                return jsonify(result)
            else:
                # Add update timestamp
                data["updated_at"] = datetime.now().isoformat()
                data["updated_by"] = request.user.get("user_id")
                
                success = firebase.update_document("products", product_id, data)
                if success:
                    updated_product = firebase.get_document("products", product_id)
                    return jsonify({
                        "success": True,
                        "product": updated_product,
                        "message": "Product updated successfully"
                    })
                else:
                    return jsonify({"success": False, "error": "Product not found"}), 404
                    
        except Exception as e:
            logger.error(f"Update product error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products/search", methods=["GET"])
    def search_products():
        """Advanced product search"""
        try:
            query = request.args.get('q', '').lower()
            if not query:
                return jsonify({"success": False, "error": "Search query required"}), 400
            
            if "product" in controllers:
                result = controllers["product"].search_products(query)
                return jsonify(result)
            else:
                products = firebase.get_documents("products") or []
                
                # Simple text search
                matching_products = []
                for product in products:
                    if (query in product.get('name', '').lower() or 
                        query in product.get('description', '').lower() or
                        query in product.get('category', '').lower()):
                        matching_products.append(product)
                
                return jsonify({
                    "success": True,
                    "data": matching_products,
                    "count": len(matching_products),
                    "query": query
                })
                
        except Exception as e:
            logger.error(f"Search products error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/products/categories", methods=["GET"])
    def get_product_categories():
        """Get all product categories"""
        try:
            products = firebase.get_documents("products") or []
            categories = list(set(p.get('category') for p in products if p.get('category')))
            
            category_stats = []
            for category in categories:
                count = len([p for p in products if p.get('category') == category])
                category_stats.append({
                    "name": category,
                    "product_count": count
                })
            
            return jsonify({
                "success": True,
                "categories": category_stats,
                "total_categories": len(categories)
            })
            
        except Exception as e:
            logger.error(f"Get categories error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # ===== INVENTORY ENDPOINTS =====
    
    @app.route("/api/v1/inventory", methods=["GET"])
    def get_inventory_status():
        """Get complete inventory status"""
        try:
            if "inventory" in controllers:
                result = controllers["inventory"].get_inventory_overview()
                return jsonify(result)
            else:
                products = firebase.get_documents("products") or []
                
                inventory_data = []
                low_stock_count = 0
                total_value = 0
                
                for product in products:
                    stock = product.get('stock', 0)
                    price = product.get('price', 0)
                    
                    status = "out_of_stock" if stock == 0 else "low_stock" if stock < 10 else "in_stock"
                    if status == "low_stock":
                        low_stock_count += 1
                    
                    total_value += stock * price
                    
                    inventory_data.append({
                        "product_id": product.get('id'),
                        "name": product.get('name'),
                        "sku": product.get('sku'),
                        "current_stock": stock,
                        "unit_price": price,
                        "total_value": stock * price,
                        "status": status,
                        "category": product.get('category')
                    })
                
                return jsonify({
                    "success": True,
                    "data": inventory_data,
                    "summary": {
                        "total_products": len(products),
                        "low_stock_count": low_stock_count,
                        "total_inventory_value": round(total_value, 2),
                        "out_of_stock_count": len([p for p in products if p.get('stock', 0) == 0])
                    }
                })
                
        except Exception as e:
            logger.error(f"Get inventory error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/inventory/low-stock", methods=["GET"])
    def get_low_stock_items():
        """Get products with low stock"""
        try:
            threshold = request.args.get('threshold', 10, type=int)
            
            if "inventory" in controllers:
                result = controllers["inventory"].get_low_stock_alerts(threshold)
                return jsonify(result)
            else:
                products = firebase.get_documents("products") or []
                low_stock_products = [
                    p for p in products if p.get('stock', 0) <= threshold and p.get('stock', 0) > 0
                ]
                
                return jsonify({
                    "success": True,
                    "data": low_stock_products,
                    "count": len(low_stock_products),
                    "threshold": threshold
                })
                
        except Exception as e:
            logger.error(f"Get low stock error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/inventory/update", methods=["POST"])
    @require_auth
    def update_inventory():
        """Update inventory levels (requires authentication)"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            if "inventory" in controllers:
                result = controllers["inventory"].update_stock_levels(data)
                return jsonify(result)
            else:
                updates = data.get('updates', [])
                if not updates:
                    return jsonify({"success": False, "error": "No updates provided"}), 400
                
                results = []
                for update in updates:
                    product_id = update.get('product_id')
                    new_stock = update.get('stock')
                    
                    if product_id and new_stock is not None:
                        success = firebase.update_document("products", product_id, {
                            "stock": int(new_stock),
                            "updated_at": datetime.now().isoformat(),
                            "updated_by": request.user.get("user_id")
                        })
                        results.append({
                            "product_id": product_id,
                            "success": success,
                            "new_stock": new_stock
                        })
                
                return jsonify({
                    "success": True,
                    "updates": results,
                    "message": f"Updated {len(results)} products"
                })
                
        except Exception as e:
            logger.error(f"Update inventory error: {str(e)}")
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
            
            # Limit results
            orders = orders[:limit]
            
            # Calculate summary
            total_revenue = sum(o.get('total', 0) for o in orders)
            
            return jsonify({
                "success": True,
                "data": orders,
                "count": len(orders),
                "summary": {
                    "total_revenue": round(total_revenue, 2),
                    "average_order_value": round(total_revenue / len(orders), 2) if orders else 0
                },
                "filters": {"status": status, "customer_id": customer_id}
            })
            
        except Exception as e:
            logger.error(f"Get orders error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/v1/orders", methods=["POST"])
    @require_auth
    def create_order():
        """Create new order (requires authentication)"""
        try:
            data, error_response, status_code = get_json_data()
            if error_response:
                return error_response, status_code
            
            # Validate required fields
            required_fields = ['customer_id', 'items']
            if not all(field in data for field in required_fields):
                return jsonify({"success": False, "error": "Missing required fields"}), 400
            
            items = data.get('items', [])
            if not items:
                return jsonify({"success": False, "error": "Order must have at least one item"}), 400
            
            # Calculate total and validate items
            total = 0
            for item in items:
                if not all(k in item for k in ['product_id', 'quantity']):
                    return jsonify({"success": False, "error": "Invalid item format"}), 400
                
                # Get product price
                product = firebase.get_document("products", item['product_id'])
                if not product:
                    return jsonify({"success": False, "error": f"Product {item['product_id']} not found"}), 400
                
                item['price'] = product.get('price', 0)
                item['subtotal'] = item['price'] * item['quantity']
                total += item['subtotal']
            
            order_data = {
                "id": str(uuid.uuid4()),
                "customer_id": data.get('customer_id'),
                "items": items,
                "total": round(total, 2),
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

    # Continue with more endpoints...
    return app
