import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  TrendingUp,
  Users,
  ShoppingCart,
  Package,
  Bot,
  Star,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import api from "../utils/api";
import { useAuth } from "../utils/AuthContext";

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  const isRetailer = user?.userType === "retailer";

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.getDashboardData();

      // Transform backend data to match our dashboard structure
      const backendData = response.data;
      const transformedData = {
        overview: {
          total_sales: backendData.overview.total_sales || 0,
          total_orders: backendData.overview.total_orders || 0,
          total_customers: backendData.overview.total_customers || 0,
          total_products: backendData.overview.total_products || 0,
          revenue_growth: backendData.overview.revenue_growth || 0,
          order_growth: backendData.overview.order_growth || 0,
          customer_growth: backendData.overview.customer_growth || 0,
          conversion_rate: backendData.performance_metrics.conversion_rate || 0,
        },
        performance_metrics: {
          conversion_rate: backendData.performance_metrics.conversion_rate || 0,
          average_basket_size:
            backendData.performance_metrics.average_basket_size || 0,
          customer_satisfaction:
            backendData.performance_metrics.customer_satisfaction || 0,
          inventory_turnover:
            backendData.performance_metrics.inventory_turnover || 0,
        },
        sales_data: backendData.sales_trend || [],
        top_categories: backendData.top_categories || [],
        generated_at: backendData.overview.generated_at,
      };

      setDashboardData(transformedData);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      // Show error state instead of mock data
      setDashboardData(null);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, change, icon: Icon, trend }) => (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {value}
          </p>
          {change && (
            <div
              className={`flex items-center mt-1 text-sm ${
                trend === "up" ? "text-green-600" : "text-red-600"
              }`}
            >
              {trend === "up" ? (
                <ArrowUpRight className="h-4 w-4 mr-1" />
              ) : (
                <ArrowDownRight className="h-4 w-4 mr-1" />
              )}
              {change}% from last month
            </div>
          )}
        </div>
        <div className="p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
          <Icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <Package className="h-12 w-12" />
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            Unable to load dashboard
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Please check your connection and try refreshing the page.
          </p>
          <div className="mt-6">
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              Refresh Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  const overview = dashboardData?.overview || {};
  const metrics = dashboardData?.performance_metrics || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Welcome back! Here's what's happening with your store.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-primary-600" />
          <span className="text-sm text-primary-600 font-medium">
            AI Insights Active
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Revenue"
          value={`$${overview.total_sales?.toLocaleString() || "0"}`}
          change={overview.revenue_growth}
          trend="up"
          icon={TrendingUp}
        />
        <StatCard
          title="Total Orders"
          value={overview.total_orders?.toLocaleString() || "0"}
          change={overview.order_growth}
          trend="up"
          icon={ShoppingCart}
        />
        <StatCard
          title="Customers"
          value={overview.total_customers?.toLocaleString() || "0"}
          change={overview.customer_growth}
          trend="up"
          icon={Users}
        />
        <StatCard
          title="Products"
          value={overview.total_products?.toLocaleString() || "0"}
          icon={Package}
        />
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Performance Metrics
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">
                Conversion Rate
              </span>
              <span className="font-semibold">{metrics.conversion_rate}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">
                Avg. Basket Size
              </span>
              <span className="font-semibold">
                ${metrics.average_basket_size}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">
                Customer Satisfaction
              </span>
              <div className="flex items-center">
                <Star className="h-4 w-4 text-yellow-400 mr-1" />
                <span className="font-semibold">
                  {metrics.customer_satisfaction}
                </span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">
                Inventory Turnover
              </span>
              <span className="font-semibold">
                {metrics.inventory_turnover}x
              </span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h3>
          <div className="space-y-3">
            <button
              onClick={() => navigate("/analytics")}
              className="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">View Analytics</span>
                <ArrowUpRight className="h-4 w-4 text-gray-400" />
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Check detailed sales reports
              </p>
            </button>
            <button
              onClick={() => navigate("/ai-assistant")}
              className="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">AI Assistant</span>
                <Bot className="h-4 w-4 text-primary-600" />
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Get smart recommendations
              </p>
            </button>
            {isRetailer ? (
              <button
                onClick={() => navigate("/inventory")}
                className="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">Inventory Check</span>
                  <Package className="h-4 w-4 text-gray-400" />
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Monitor stock levels
                </p>
              </button>
            ) : (
              <button
                onClick={() => navigate("/shopping")}
                className="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">Start Shopping</span>
                  <ShoppingCart className="h-4 w-4 text-gray-400" />
                </div>
                <p className="text-sm text-gray-500 mt-1">Browse products</p>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* AI Insights */}
      <div className="card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Bot className="h-5 w-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            AI Insights
          </h3>
        </div>
        <div className="bg-gradient-to-r from-primary-50 to-retail-50 dark:from-primary-900/20 dark:to-retail-900/20 rounded-lg p-4">
          <p className="text-gray-700 dark:text-gray-300">
            📈 <strong>Sales are trending up!</strong> Your revenue increased by{" "}
            <strong>{overview.revenue_growth}%</strong> this month. Consider
            stocking more of your top-selling items.
          </p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">
            Based on AI analysis of your sales patterns and customer behavior.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
