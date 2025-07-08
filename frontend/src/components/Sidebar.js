import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  BarChart3,
  MessageSquare,
  User,
  X,
  Bot,
  Store,
  TrendingUp,
  Zap,
} from "lucide-react";

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();

  const menuItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
      description: "Overview & Analytics",
    },
    {
      name: "AI Assistant",
      href: "/ai-assistant",
      icon: Bot,
      description: "Chat with AI",
    },
    {
      name: "Smart Shopping",
      href: "/shopping",
      icon: ShoppingCart,
      description: "Browse Products",
    },
    {
      name: "Inventory",
      href: "/inventory",
      icon: Package,
      description: "Stock Management",
    },
    {
      name: "Analytics",
      href: "/analytics",
      icon: BarChart3,
      description: "Sales & Performance",
    },
    {
      name: "Feedback",
      href: "/feedback",
      icon: MessageSquare,
      description: "Customer Reviews",
    },
    {
      name: "Profile",
      href: "/profile",
      icon: User,
      description: "Account Settings",
    },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 lg:static lg:inset-0`}
      >
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Store className="h-8 w-8 text-primary-600" />
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              Menu
            </span>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          <div className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => window.innerWidth < 1024 && onClose()}
                  className={`group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${
                    active
                      ? "bg-primary-50 dark:bg-primary-900/50 text-primary-600 dark:text-primary-400 border-l-4 border-primary-600"
                      : "text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white"
                  }`}
                >
                  <Icon
                    className={`mr-3 h-5 w-5 transition-colors ${
                      active
                        ? "text-primary-600 dark:text-primary-400"
                        : "text-gray-400 group-hover:text-gray-500"
                    }`}
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium">{item.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                  {active && (
                    <div className="ml-3">
                      <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Quick Stats */}
        <div className="mt-8 mx-3">
          <div className="bg-gradient-to-r from-primary-500 to-retail-500 rounded-lg p-4 text-white">
            <div className="flex items-center justify-between mb-2">
              <Zap className="h-5 w-5" />
              <span className="text-xs font-medium">AI POWERED</span>
            </div>
            <h3 className="text-sm font-semibold mb-1">RetailGenie Pro</h3>
            <p className="text-xs opacity-90">
              Smart recommendations & analytics at your fingertips
            </p>
            <div className="mt-3 flex items-center text-xs">
              <TrendingUp className="h-3 w-3 mr-1" />
              <span>+24% this week</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              RetailGenie v1.0
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500">
              AI Shopping Assistant
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
