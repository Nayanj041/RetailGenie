import React, { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import {
  Package,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Search,
  Plus,
  Edit2,
  Trash2,
} from "lucide-react";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../utils/AuthContext";
import { api } from "../utils/api";

const Inventory = () => {
  const { token } = useAuth();
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [predictions, setPredictions] = useState({});

  const [newItem, setNewItem] = useState({
    name: "",
    sku: "",
    category: "",
    quantity: 0,
    price: 0,
    supplier: "",
    reorder_level: 0,
  });

  useEffect(() => {
    fetchInventory();
    fetchPredictions();
  }, []);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const response = await api.get("/api/v1/inventory");
      setInventory(response.data?.items || response.items || []);
    } catch (error) {
      console.error("Error fetching inventory:", error);
      setInventory([]);
      toast.error("Failed to load inventory");
    } finally {
      setLoading(false);
    }
  };

  const fetchPredictions = async () => {
    try {
      const response = await api.get("/api/v1/inventory/forecast");
      setPredictions(response.data?.predictions || response.predictions || {});
    } catch (error) {
      console.error("Error fetching predictions:", error);
      setPredictions({});
      // Don't show error toast for predictions as it's not critical
    }
  };

  const addItem = async () => {
    try {
      await api.post("/api/v1/inventory", newItem);
      fetchInventory();
      setShowAddModal(false);
      setNewItem({
        name: "",
        sku: "",
        category: "",
        quantity: 0,
        price: 0,
        supplier: "",
        reorder_level: 0,
      });
    } catch (error) {
      console.error("Error adding item:", error);
    }
  };

  const updateItem = async (id, updates) => {
    try {
      await api.put(`/inventory/${id}`, updates, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchInventory();
      setEditingItem(null);
    } catch (error) {
      console.error("Error updating item:", error);
    }
  };

  const deleteItem = async (id) => {
    if (window.confirm("Are you sure you want to delete this item?")) {
      try {
        await api.delete(`/inventory/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        fetchInventory();
      } catch (error) {
        console.error("Error deleting item:", error);
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "in_stock":
        return "text-green-600 bg-green-100";
      case "low_stock":
        return "text-yellow-600 bg-yellow-100";
      case "out_of_stock":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case "down":
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4 bg-blue-500 rounded-full"></div>;
    }
  };

  const filteredInventory = inventory.filter(
    (item) =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.category.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Inventory Management
            </h1>
            <p className="text-gray-600">
              Track and manage your product inventory with AI insights
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add Item
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Items</p>
                <p className="text-2xl font-bold text-gray-900">
                  {inventory.length}
                </p>
              </div>
              <Package className="h-8 w-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">In Stock</p>
                <p className="text-2xl font-bold text-green-600">
                  {
                    inventory.filter((item) => item.status === "in_stock")
                      .length
                  }
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Low Stock</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {
                    inventory.filter((item) => item.status === "low_stock")
                      .length
                  }
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-yellow-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Out of Stock
                </p>
                <p className="text-2xl font-bold text-red-600">
                  {
                    inventory.filter((item) => item.status === "out_of_stock")
                      .length
                  }
                </p>
              </div>
              <TrendingDown className="h-8 w-8 text-red-500" />
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search inventory by name, SKU, or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Inventory Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    SKU
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    AI Forecast
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredInventory.map((item) => {
                  const prediction = predictions[item.id] || {};
                  return (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {item.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {item.supplier}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.sku}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.category}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {item.quantity}
                        </div>
                        <div className="text-xs text-gray-500">
                          Reorder at: {item.reorder_level}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${item.price}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}
                        >
                          {item.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {getTrendIcon(prediction.trend)}
                          <div>
                            <div className="text-sm text-gray-900">
                              {prediction.predicted_demand || "N/A"}
                            </div>
                            <div className="text-xs text-gray-500">
                              {prediction.confidence
                                ? `${Math.round(prediction.confidence * 100)}% confidence`
                                : ""}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => setEditingItem(item)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Edit2 className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => deleteItem(item.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Add Item Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <h3 className="text-lg font-bold text-gray-900 mb-4">
                Add New Item
              </h3>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Product Name"
                  value={newItem.name}
                  onChange={(e) =>
                    setNewItem((prev) => ({ ...prev, name: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="SKU"
                  value={newItem.sku}
                  onChange={(e) =>
                    setNewItem((prev) => ({ ...prev, sku: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="Category"
                  value={newItem.category}
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      category: e.target.value,
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  placeholder="Quantity"
                  value={newItem.quantity}
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      quantity: Number(e.target.value),
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  step="0.01"
                  placeholder="Price"
                  value={newItem.price}
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      price: Number(e.target.value),
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="Supplier"
                  value={newItem.supplier}
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      supplier: e.target.value,
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  placeholder="Reorder Level"
                  value={newItem.reorder_level}
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      reorder_level: Number(e.target.value),
                    }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={addItem}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add Item
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Inventory;
