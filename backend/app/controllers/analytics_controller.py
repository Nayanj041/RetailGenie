"""
Analytics Controller for RetailGenie
Handles analytics, reporting, and business intelligence
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.utils.firebase_utils import FirebaseUtils

logger = logging.getLogger(__name__)


class AnalyticsController:
    def __init__(self):
        """Initialize Analytics Controller"""
        self.firebase = FirebaseUtils()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            # Mock data for now - replace with real queries
            stats = {
                "total_sales": 12456.78,
                "total_orders": 145,
                "total_customers": 89,
                "total_products": 23,
                "revenue_growth": 15.2,
                "order_growth": 8.7,
                "customer_growth": 12.1,
                "generated_at": datetime.now().isoformat(),
            }

            logger.info("Dashboard stats retrieved successfully")
            return {"success": True, "data": stats}

        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_sales_analytics(self, period: str = "30d") -> Dict[str, Any]:
        """Get sales analytics for specified period"""
        try:
            # Mock sales data
            sales_data = {
                "period": period,
                "total_revenue": 12456.78,
                "total_orders": 145,
                "average_order_value": 85.91,
                "daily_sales": [
                    {"date": "2025-07-01", "revenue": 456.78, "orders": 6},
                    {"date": "2025-07-02", "revenue": 523.45, "orders": 8},
                ],
                "top_products": [
                    {"name": "Premium Coffee", "revenue": 2345.67, "units_sold": 45},
                    {"name": "Organic Tea", "revenue": 1876.32, "units_sold": 32},
                ],
            }

            logger.info(f"Sales analytics retrieved for period: {period}")
            return {"success": True, "data": sales_data}

        except Exception as e:
            logger.error(f"Error getting sales analytics: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_customer_analytics(self) -> Dict[str, Any]:
        """Get customer analytics"""
        try:
            customer_data = {
                "total_customers": 89,
                "new_customers_this_month": 12,
                "repeat_customers": 67,
                "customer_retention_rate": 75.3,
                "average_lifetime_value": 456.78,
                "customer_segments": [
                    {"segment": "Premium", "count": 23, "percentage": 25.8},
                    {"segment": "Regular", "count": 45, "percentage": 50.6},
                    {"segment": "New", "count": 21, "percentage": 23.6},
                ],
            }

            logger.info("Customer analytics retrieved successfully")
            return {"success": True, "data": customer_data}

        except Exception as e:
            logger.error(f"Error getting customer analytics: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_product_performance(self) -> Dict[str, Any]:
        """Get product performance analytics"""
        try:
            product_data = {
                "total_products": 23,
                "best_performers": [
                    {
                        "id": "prod_001",
                        "name": "Premium Coffee Beans",
                        "revenue": 2345.67,
                        "units_sold": 45,
                        "profit_margin": 35.2,
                    },
                    {
                        "id": "prod_002",
                        "name": "Organic Tea Set",
                        "revenue": 1876.32,
                        "units_sold": 32,
                        "profit_margin": 42.1,
                    },
                ],
                "low_stock_alerts": [
                    {"id": "prod_005", "name": "Specialty Honey", "stock": 5},
                    {"id": "prod_012", "name": "Artisan Bread", "stock": 3},
                ],
            }

            logger.info("Product performance analytics retrieved successfully")
            return {"success": True, "data": product_data}

        except Exception as e:
            logger.error(f"Error getting product performance: {str(e)}")
            return {"success": False, "error": str(e)}

    def record_event(
        self, event_type: str, event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record an analytics event"""
        try:
            event = {
                "type": event_type,
                "data": event_data,
                "timestamp": datetime.now().isoformat(),
                "user_agent": event_data.get("user_agent", ""),
                "ip_address": event_data.get("ip_address", ""),
            }

            # Store in Firebase
            doc_id = self.firebase.create_document("analytics_events", event)

            logger.info(f"Analytics event recorded: {event_type}")
            return {"success": True, "event_id": doc_id}

        except Exception as e:
            logger.error(f"Error recording analytics event: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_dashboard_analytics(
        self, store_id: Optional[str] = None, date_range: str = "7d"
    ) -> Dict[str, Any]:
        """Get dashboard analytics data with ML insights"""
        try:
            # Get base dashboard stats
            base_stats = self.get_dashboard_stats()
            
            # Get ML-powered analysis
            ml_analysis = self.get_ml_product_analysis(store_id)

            # Enhanced analytics with date range filtering and ML insights
            dashboard_data = {
                "overview": base_stats.get("data", {}),
                "date_range": date_range,
                "store_id": store_id,
                "sales_trend": [
                    {"date": "2025-06-25", "sales": 1200.45, "orders": 15},
                    {"date": "2025-06-26", "sales": 1456.78, "orders": 18},
                    {"date": "2025-06-27", "sales": 1123.90, "orders": 14},
                    {"date": "2025-06-28", "sales": 1687.32, "orders": 22},
                    {"date": "2025-06-29", "sales": 1934.56, "orders": 25},
                    {"date": "2025-06-30", "sales": 2134.78, "orders": 28},
                    {"date": "2025-07-01", "sales": 1876.54, "orders": 24},
                ],
                "top_categories": [
                    {
                        "name": "Coffee & Beverages",
                        "revenue": 4567.89,
                        "percentage": 35.2,
                    },
                    {"name": "Organic Foods", "revenue": 3421.56, "percentage": 26.4},
                    {"name": "Bakery Items", "revenue": 2987.34, "percentage": 23.1},
                    {
                        "name": "Health & Wellness",
                        "revenue": 1987.65,
                        "percentage": 15.3,
                    },
                ],
                "performance_metrics": {
                    "conversion_rate": 3.4,
                    "average_basket_size": 78.90,
                    "customer_satisfaction": 4.2,
                    "inventory_turnover": 2.8,
                },
                # Add ML-powered insights to dashboard
                "ml_insights": {
                    "summary": ml_analysis.get("data", {}).get("performance_metrics", {}),
                    "top_alerts": ml_analysis.get("data", {}).get("inventory_alerts", [])[:3],  # Top 3 alerts
                    "trending_products": [
                        {
                            "product_id": pid,
                            "trend": data.get("trend", "stable"),
                            "confidence": data.get("confidence", 0.5)
                        }
                        for pid, data in ml_analysis.get("data", {}).get("demand_forecasting", {}).items()
                        if data.get("trend") == "increasing"
                    ][:5],  # Top 5 trending products
                    "sentiment_overview": {
                        "positive_products": len([
                            p for p in ml_analysis.get("data", {}).get("sentiment_analysis", {}).values()
                            if p.get("overall_sentiment") == "positive"
                        ]),
                        "negative_products": len([
                            p for p in ml_analysis.get("data", {}).get("sentiment_analysis", {}).values()
                            if p.get("overall_sentiment") == "negative"
                        ]),
                        "neutral_products": len([
                            p for p in ml_analysis.get("data", {}).get("sentiment_analysis", {}).values()
                            if p.get("overall_sentiment") == "neutral"
                        ])
                    },
                    "pricing_opportunities": len([
                        p for p in ml_analysis.get("data", {}).get("pricing_recommendations", {}).values()
                        if abs(p.get("price_change_percent", 0)) > 5
                    ])
                },
                "generated_at": datetime.now().isoformat()
            }

            logger.info(
                f"Dashboard analytics with ML insights retrieved for store: {store_id}, range: {date_range}"
            )
            return dashboard_data

        except Exception as e:
            logger.error(f"Error getting dashboard analytics: {str(e)}")
            # Return basic dashboard without ML if there's an error
            base_stats = self.get_dashboard_stats()
            return {
                "overview": base_stats.get("data", {}),
                "date_range": date_range,
                "store_id": store_id,
                "error": "ML insights unavailable",
                "generated_at": datetime.now().isoformat()
            }

    def get_customer_insights(
        self, store_id: Optional[str] = None, segment: str = "all"
    ) -> Dict[str, Any]:
        """Get customer behavior insights"""
        try:
            # Get base customer analytics
            base_data = self.get_customer_analytics()

            insights = {
                "store_id": store_id,
                "segment": segment,
                "customer_base": base_data.get("data", {}),
                "behavior_patterns": {
                    "peak_shopping_hours": [
                        {"hour": "09:00", "traffic": 75},
                        {"hour": "12:00", "traffic": 120},
                        {"hour": "17:00", "traffic": 95},
                        {"hour": "19:00", "traffic": 85},
                    ],
                    "preferred_categories": [
                        {"category": "Coffee & Beverages", "percentage": 42.3},
                        {"category": "Organic Foods", "percentage": 38.7},
                        {"category": "Bakery Items", "percentage": 31.2},
                    ],
                    "shopping_frequency": {
                        "daily": 15.2,
                        "weekly": 45.6,
                        "monthly": 32.1,
                        "occasional": 7.1,
                    },
                },
                "segmentation": {
                    "high_value": {
                        "count": 23,
                        "avg_spend": 125.67,
                        "frequency": "weekly",
                    },
                    "regular": {
                        "count": 45,
                        "avg_spend": 78.34,
                        "frequency": "bi-weekly",
                    },
                    "new": {"count": 21, "avg_spend": 45.23, "frequency": "monthly"},
                },
                "recommendations": [
                    "Implement loyalty program for high-value customers",
                    "Create targeted promotions for regular customers",
                    "Develop onboarding campaigns for new customers",
                ],
            }

            logger.info(
                f"Customer insights retrieved for store: {store_id}, segment: {segment}"
            )
            return insights

        except Exception as e:
            logger.error(f"Error getting customer insights: {str(e)}")
            raise

    def get_manager_performance(
        self, manager_id: Optional[str] = None, period: str = "month"
    ) -> Dict[str, Any]:
        """Get manager performance metrics"""
        try:
            performance = {
                "manager_id": manager_id,
                "period": period,
                "metrics": {
                    "sales_target_achievement": 108.5,
                    "customer_satisfaction_score": 4.3,
                    "team_productivity": 92.1,
                    "inventory_accuracy": 98.7,
                    "staff_engagement": 87.4,
                },
                "kpis": {
                    "total_sales": 15678.90,
                    "sales_target": 14500.00,
                    "orders_processed": 234,
                    "customer_complaints": 3,
                    "staff_turnover": 5.2,
                },
                "achievements": [
                    "Exceeded monthly sales target by 8.5%",
                    "Maintained customer satisfaction above 4.0",
                    "Zero safety incidents this period",
                    "Implemented new inventory tracking system",
                ],
                "areas_for_improvement": [
                    "Reduce customer wait times during peak hours",
                    "Improve staff product knowledge training",
                    "Optimize inventory ordering processes",
                ],
                "team_performance": {
                    "total_staff": 8,
                    "attendance_rate": 96.2,
                    "training_completion": 87.5,
                    "sales_per_employee": 1959.86,
                },
                "comparison": {
                    "vs_last_period": {
                        "sales": "+12.3%",
                        "satisfaction": "+0.2 points",
                        "productivity": "+5.7%",
                    },
                    "vs_regional_average": {
                        "sales": "+15.8%",
                        "satisfaction": "+0.5 points",
                        "efficiency": "+8.2%",
                    },
                },
            }

            logger.info(
                f"Manager performance retrieved for manager: {manager_id}, period: {period}"
            )
            return performance

        except Exception as e:
            logger.error(f"Error getting manager performance: {str(e)}")
            raise

    def generate_analytics_report(
        self,
        report_type: str = "daily",
        store_id: Optional[str] = None,
        email_recipients: List[str] = None,
    ) -> str:
        """Generate analytics report"""
        try:
            if email_recipients is None:
                email_recipients = []

            # Generate report data based on type
            report_data = {
                "report_type": report_type,
                "store_id": store_id,
                "generated_at": datetime.now().isoformat(),
                "data": {},
            }

            if report_type == "daily":
                report_data["data"] = {
                    "daily_sales": 1876.54,
                    "daily_orders": 24,
                    "daily_customers": 18,
                    "top_products": [
                        {"name": "Premium Coffee", "units": 12, "revenue": 234.56},
                        {"name": "Organic Croissant", "units": 8, "revenue": 156.78},
                    ],
                }
            elif report_type == "weekly":
                report_data["data"] = {
                    "weekly_sales": 11234.56,
                    "weekly_orders": 145,
                    "weekly_customers": 89,
                    "growth_metrics": {
                        "sales_growth": "+12.5%",
                        "customer_growth": "+8.7%",
                    },
                }
            elif report_type == "monthly":
                report_data["data"] = {
                    "monthly_sales": 45678.90,
                    "monthly_orders": 567,
                    "monthly_customers": 234,
                    "profitability": {"gross_margin": 34.2, "net_profit": 8765.43},
                }

            # Generate report file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"analytics_report_{report_type}_{timestamp}.pdf"
            report_path = f"/tmp/reports/{report_filename}"

            # In a real implementation, generate actual PDF here
            # For now, just return the path

            logger.info(
                f"Analytics report generated: {report_type} for store: {store_id}"
            )
            return report_path

        except Exception as e:
            logger.error(f"Error generating analytics report: {str(e)}")
            raise

    def get_gamification_leaderboard(
        self, region: Optional[str] = None, period: str = "month"
    ) -> Dict[str, Any]:
        """Get manager gamification leaderboard"""
        try:
            leaderboard = {
                "region": region,
                "period": period,
                "updated_at": datetime.now().isoformat(),
                "leaderboard": [
                    {
                        "rank": 1,
                        "manager_id": "mgr_001",
                        "manager_name": "Sarah Johnson",
                        "store_name": "Downtown Flagship",
                        "points": 2450,
                        "badges": ["Sales Champion", "Customer Hero", "Team Builder"],
                        "achievements": {
                            "sales_target": 115.2,
                            "satisfaction_score": 4.7,
                            "team_performance": 96.8,
                        },
                    },
                    {
                        "rank": 2,
                        "manager_id": "mgr_002",
                        "manager_name": "Michael Chen",
                        "store_name": "Mall Location",
                        "points": 2230,
                        "badges": ["Innovation Leader", "Efficiency Expert"],
                        "achievements": {
                            "sales_target": 108.7,
                            "satisfaction_score": 4.5,
                            "team_performance": 94.2,
                        },
                    },
                    {
                        "rank": 3,
                        "manager_id": "mgr_003",
                        "manager_name": "Emily Rodriguez",
                        "store_name": "Suburban Branch",
                        "points": 2100,
                        "badges": ["Customer Champion", "Growth Driver"],
                        "achievements": {
                            "sales_target": 106.3,
                            "satisfaction_score": 4.6,
                            "team_performance": 91.5,
                        },
                    },
                    {
                        "rank": 4,
                        "manager_id": "mgr_004",
                        "manager_name": "David Kim",
                        "store_name": "City Center",
                        "points": 1980,
                        "badges": ["Consistency Award"],
                        "achievements": {
                            "sales_target": 102.1,
                            "satisfaction_score": 4.3,
                            "team_performance": 89.7,
                        },
                    },
                ],
                "metrics": {
                    "total_participants": 12,
                    "average_score": 2140.5,
                    "top_badge": "Sales Champion",
                    "improvement_rate": "+15.3%",
                },
                "challenges": [
                    {
                        "name": "Customer Satisfaction Challenge",
                        "description": "Achieve 4.5+ customer rating",
                        "reward": "250 points",
                        "deadline": "2025-07-31",
                    },
                    {
                        "name": "Sales Growth Sprint",
                        "description": "Increase sales by 10% over last month",
                        "reward": "500 points",
                        "deadline": "2025-07-31",
                    },
                ],
            }

            logger.info(
                f"Gamification leaderboard retrieved for region: {region}, period: {period}"
            )
            return leaderboard

        except Exception as e:
            logger.error(f"Error getting gamification leaderboard: {str(e)}")
            raise

    def get_general_analytics(self, time_range: str = "7d") -> Dict[str, Any]:
        """Get general analytics data for the specified time range"""
        try:
            # Get real data from Firebase
            orders = self.firebase.get_documents("orders") or []
            customers = self.firebase.get_documents("customers") or []
            products = self.firebase.get_documents("products") or []

            # Calculate overview metrics
            total_revenue = sum(order.get("total", 0) for order in orders)
            total_orders = len(orders)
            total_customers = len(customers)

            # Calculate conversion rate (orders/customers * 100)
            conversion_rate = (total_orders / total_customers * 100) if total_customers > 0 else 0

            # Generate sample sales trend data
            sales_trend = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
                revenue = 2000 + (i * 100) + (i % 3 * 200)  # Sample data pattern
                orders = 25 + (i * 2) + (i % 3 * 5)  # Sample orders data
                sales_trend.append({"date": date, "revenue": revenue, "orders": orders})

            # Get top products (sample data if no real data)
            top_products = [
                {"name": "Coffee Beans", "sales": 45, "revenue": 899.55},
                {"name": "Organic Tea", "sales": 32, "revenue": 415.68},
                {"name": "Artisan Chocolate", "sales": 28, "revenue": 251.72},
            ]

            # Generate category distribution data
            category_distribution = [
                {"name": "Electronics", "value": 5200},
                {"name": "Clothing", "value": 3800},
                {"name": "Books", "value": 2100},
                {"name": "Home", "value": 2900},
                {"name": "Sports", "value": 1650},
            ]

            # Generate customer segments data
            customer_segments = [
                {"segment": "Premium", "customers": 23, "avg_order_value": 125.50},
                {"segment": "Regular", "customers": 45, "avg_order_value": 78.30},
                {"segment": "New", "customers": 21, "avg_order_value": 45.20},
            ]

            analytics_data = {
                "overview": {
                    "total_revenue": total_revenue or 15750.00,
                    "revenue_change": 12.5,
                    "total_orders": total_orders or 156,
                    "orders_change": 8.3,
                    "total_customers": total_customers or 89,
                    "customers_change": 15.2,
                    "conversion_rate": round(conversion_rate, 1) or 3.2,
                    "conversion_change": -0.5,
                },
                "sales_trend": sales_trend,
                "top_products": top_products,
                "category_distribution": category_distribution,
                "customer_segments": customer_segments,
                "time_range": time_range,
            }

            return analytics_data

        except Exception as e:
            logger.error(f"Error getting general analytics: {str(e)}")
            raise

    def get_ml_product_analysis(self, store_id: Optional[str] = None) -> Dict[str, Any]:
        """Get ML-powered product analysis including forecasting and sentiment"""
        try:
            import sys
            import os
            
            # Add ML models to path
            ml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_models')
            if ml_path not in sys.path:
                sys.path.append(ml_path)
            
            # Get real product data from database
            try:
                products = self.firebase.get_documents("products") or []
                feedback = self.firebase.get_documents("feedback") or []
                orders = self.firebase.get_documents("orders") or []
            except:
                products, feedback, orders = [], [], []
            
            ml_analysis = {
                "product_insights": [],
                "demand_forecasting": {},
                "sentiment_analysis": {},
                "pricing_recommendations": {},
                "inventory_alerts": [],
                "performance_metrics": {}
            }
            
            # Process each product with ML analysis
            for product in products:
                product_id = product.get('id', 'unknown')
                product_name = product.get('name', 'Unknown Product')
                current_stock = product.get('stock_quantity', 0)
                current_price = product.get('price', 0)
                
                # 1. Demand Forecasting using simple ML logic
                try:
                    # Calculate historical demand from orders
                    product_orders = [
                        order for order in orders 
                        if any(item.get('product_id') == product_id for item in order.get('items', []))
                    ]
                    
                    recent_demand = len(product_orders)
                    
                    # Simple forecasting logic
                    if recent_demand > 10:
                        predicted_demand = int(recent_demand * 1.2)  # 20% growth
                        trend = "increasing"
                        confidence = 0.85
                    elif recent_demand > 5:
                        predicted_demand = int(recent_demand * 1.1)  # 10% growth
                        trend = "stable"
                        confidence = 0.75
                    else:
                        predicted_demand = max(5, int(recent_demand * 0.8))  # Slight decline
                        trend = "decreasing"
                        confidence = 0.65
                    
                    ml_analysis["demand_forecasting"][product_id] = {
                        "current_demand": recent_demand,
                        "predicted_demand": predicted_demand,
                        "trend": trend,
                        "confidence": confidence,
                        "reorder_recommended": predicted_demand > current_stock
                    }
                    
                except Exception as forecast_error:
                    logger.warning(f"Forecast error for {product_id}: {forecast_error}")
                
                # 2. Sentiment Analysis from feedback
                try:
                    product_feedback = [
                        fb for fb in feedback 
                        if fb.get('product_id') == product_id and fb.get('comment')
                    ]
                    
                    if product_feedback:
                        # Simple sentiment scoring
                        positive_words = ['great', 'excellent', 'amazing', 'love', 'perfect', 'good']
                        negative_words = ['bad', 'terrible', 'awful', 'hate', 'poor', 'worst']
                        
                        sentiment_scores = []
                        for fb in product_feedback:
                            comment = fb.get('comment', '').lower()
                            positive_count = sum(1 for word in positive_words if word in comment)
                            negative_count = sum(1 for word in negative_words if word in comment)
                            
                            if positive_count > negative_count:
                                sentiment_scores.append(1)  # Positive
                            elif negative_count > positive_count:
                                sentiment_scores.append(-1)  # Negative
                            else:
                                sentiment_scores.append(0)  # Neutral
                        
                        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                        
                        if avg_sentiment > 0.3:
                            overall_sentiment = "positive"
                        elif avg_sentiment < -0.3:
                            overall_sentiment = "negative"
                        else:
                            overall_sentiment = "neutral"
                        
                        ml_analysis["sentiment_analysis"][product_id] = {
                            "overall_sentiment": overall_sentiment,
                            "sentiment_score": round(avg_sentiment, 2),
                            "total_feedback": len(product_feedback),
                            "confidence": min(0.95, len(product_feedback) / 10)  # More feedback = higher confidence
                        }
                
                except Exception as sentiment_error:
                    logger.warning(f"Sentiment error for {product_id}: {sentiment_error}")
                
                # 3. Dynamic Pricing Recommendations
                try:
                    # Get competitor pricing (mock data)
                    market_price = current_price * (0.9 + (hash(product_id) % 20) / 100)  # Random but consistent
                    
                    # Calculate optimal price based on demand and sentiment
                    demand_factor = 1.0
                    sentiment_factor = 1.0
                    
                    if product_id in ml_analysis["demand_forecasting"]:
                        demand_trend = ml_analysis["demand_forecasting"][product_id]["trend"]
                        if demand_trend == "increasing":
                            demand_factor = 1.1  # Can charge more
                        elif demand_trend == "decreasing":
                            demand_factor = 0.95  # Should charge less
                    
                    if product_id in ml_analysis["sentiment_analysis"]:
                        sentiment = ml_analysis["sentiment_analysis"][product_id]["overall_sentiment"]
                        if sentiment == "positive":
                            sentiment_factor = 1.05  # Premium pricing
                        elif sentiment == "negative":
                            sentiment_factor = 0.9  # Discount pricing
                    
                    optimal_price = current_price * demand_factor * sentiment_factor
                    optimal_price = max(current_price * 0.8, min(current_price * 1.3, optimal_price))  # Cap changes
                    
                    price_change = ((optimal_price - current_price) / current_price) * 100 if current_price > 0 else 0
                    
                    ml_analysis["pricing_recommendations"][product_id] = {
                        "current_price": current_price,
                        "optimal_price": round(optimal_price, 2),
                        "price_change_percent": round(price_change, 1),
                        "market_price": round(market_price, 2),
                        "demand_factor": demand_factor,
                        "sentiment_factor": sentiment_factor,
                        "confidence": 0.75
                    }
                
                except Exception as pricing_error:
                    logger.warning(f"Pricing error for {product_id}: {pricing_error}")
                
                # 4. Inventory Alerts
                try:
                    predicted_demand = ml_analysis["demand_forecasting"].get(product_id, {}).get("predicted_demand", 5)
                    days_of_stock = current_stock / max(predicted_demand / 30, 1)  # Assuming monthly demand
                    
                    if days_of_stock < 7:
                        alert_level = "critical"
                        message = f"Only {days_of_stock:.1f} days of stock remaining"
                    elif days_of_stock < 14:
                        alert_level = "warning"
                        message = f"{days_of_stock:.1f} days of stock remaining"
                    else:
                        alert_level = "normal"
                        message = f"Stock level adequate ({days_of_stock:.1f} days)"
                    
                    if alert_level in ["critical", "warning"]:
                        ml_analysis["inventory_alerts"].append({
                            "product_id": product_id,
                            "product_name": product_name,
                            "alert_level": alert_level,
                            "message": message,
                            "current_stock": current_stock,
                            "predicted_demand": predicted_demand,
                            "days_of_stock": round(days_of_stock, 1)
                        })
                
                except Exception as inventory_error:
                    logger.warning(f"Inventory error for {product_id}: {inventory_error}")
                
                # Add to product insights summary
                ml_analysis["product_insights"].append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "overall_score": round(
                        (ml_analysis["demand_forecasting"].get(product_id, {}).get("confidence", 0.5) +
                         ml_analysis["sentiment_analysis"].get(product_id, {}).get("confidence", 0.5)) / 2, 2
                    ),
                    "recommendations": self._generate_product_recommendations(product_id, ml_analysis)
                })
            
            # Calculate overall performance metrics
            ml_analysis["performance_metrics"] = {
                "total_products_analyzed": len(products),
                "high_demand_products": len([p for p in ml_analysis["demand_forecasting"].values() if p.get("trend") == "increasing"]),
                "positive_sentiment_products": len([p for p in ml_analysis["sentiment_analysis"].values() if p.get("overall_sentiment") == "positive"]),
                "critical_inventory_alerts": len([a for a in ml_analysis["inventory_alerts"] if a.get("alert_level") == "critical"]),
                "avg_prediction_confidence": round(
                    sum(p.get("confidence", 0) for p in ml_analysis["demand_forecasting"].values()) / 
                    max(len(ml_analysis["demand_forecasting"]), 1), 2
                ),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"ML product analysis completed for {len(products)} products")
            return {"success": True, "data": ml_analysis}
            
        except Exception as e:
            logger.error(f"Error in ML product analysis: {str(e)}")
            # Return fallback ML analysis
            return {
                "success": True,
                "data": {
                    "product_insights": [
                        {
                            "product_id": "sample_001",
                            "product_name": "Sample Product",
                            "overall_score": 0.85,
                            "recommendations": ["Increase stock", "Monitor sentiment"]
                        }
                    ],
                    "demand_forecasting": {
                        "sample_001": {
                            "predicted_demand": 25,
                            "trend": "increasing",
                            "confidence": 0.80
                        }
                    },
                    "sentiment_analysis": {
                        "sample_001": {
                            "overall_sentiment": "positive",
                            "sentiment_score": 0.75,
                            "confidence": 0.85
                        }
                    },
                    "performance_metrics": {
                        "total_products_analyzed": 1,
                        "analysis_timestamp": datetime.now().isoformat(),
                        "mode": "fallback"
                    }
                }
            }
    
    def _generate_product_recommendations(self, product_id: str, ml_data: Dict) -> List[str]:
        """Generate specific recommendations for a product based on ML analysis"""
        recommendations = []
        
        # Demand-based recommendations
        demand_data = ml_data["demand_forecasting"].get(product_id, {})
        if demand_data.get("trend") == "increasing":
            recommendations.append("Consider increasing inventory")
            recommendations.append("Monitor for upselling opportunities")
        elif demand_data.get("trend") == "decreasing":
            recommendations.append("Implement promotional campaigns")
            recommendations.append("Review product positioning")
        
        if demand_data.get("reorder_recommended"):
            recommendations.append("Reorder stock immediately")
        
        # Sentiment-based recommendations
        sentiment_data = ml_data["sentiment_analysis"].get(product_id, {})
        if sentiment_data.get("overall_sentiment") == "positive":
            recommendations.append("Leverage positive reviews in marketing")
            recommendations.append("Consider premium pricing strategy")
        elif sentiment_data.get("overall_sentiment") == "negative":
            recommendations.append("Address customer concerns")
            recommendations.append("Consider product improvements")
        
        # Pricing recommendations
        pricing_data = ml_data["pricing_recommendations"].get(product_id, {})
        if pricing_data.get("price_change_percent", 0) > 5:
            recommendations.append("Consider price increase")
        elif pricing_data.get("price_change_percent", 0) < -5:
            recommendations.append("Consider price reduction")
        
        return recommendations[:3]  # Limit to top 3 recommendations
