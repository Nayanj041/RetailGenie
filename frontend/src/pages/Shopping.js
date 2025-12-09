import React, { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import {
  ShoppingCart,
  Search,
  Filter,
  Star,
  Heart,
  Plus,
  Minus,
  Package,
  BarChart3,
} from "lucide-react";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../utils/AuthContext";
import { api } from "../utils/api";
import { productCatalog } from "../data/productCatalog";

const Shopping = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [priceRange, setPriceRange] = useState({ min: 0, max: 1000 });
  const [cart, setCart] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: "",
    description: "",
    price: "",
    category: "electronics",
    stock_quantity: "",
    image: ""
  });

  // Show different interface based on user type
  const isRetailer = user?.userType === "retailer";

  const categories = [
    "all",
    "electronics",
    "clothing",
    "books",
    "home",
    "sports",
    "beauty",
  ];

  useEffect(() => {
    fetchProducts();
    fetchCart();
    fetchWishlist();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await api.get("/api/v1/products");
      const fetchedProducts = response.data || response.products;
      // Use fetched products if available, otherwise use the product catalog
      setProducts(fetchedProducts && fetchedProducts.length > 0 ? fetchedProducts : productCatalog);
    } catch (error) {
      console.error("Error fetching products:", error);
      // Use product catalog as fallback when API fails
      setProducts(productCatalog);
    } finally {
      setLoading(false);
    }
  };

  const fetchCart = async () => {
    try {
      const response = await api.get("/api/v1/cart");
      setCart(response.data?.items || response.items || []);
    } catch (error) {
      console.error("Error fetching cart:", error);
      setCart([]);
    }
  };

  const fetchWishlist = async () => {
    try {
      const response = await api.get("/api/v1/wishlist");
      setWishlist(response.data?.items || response.items || []);
    } catch (error) {
      console.error("Error fetching wishlist:", error);
      setWishlist([]);
    }
  };

  const addToCart = async (productId, quantity = 1) => {
    try {
      const response = await api.post("/api/v1/cart/add", {
        product_id: productId,
        quantity,
      });
      
      if (response.data?.success || response.success) {
        toast.success("Product added to cart!");
        fetchCart(); // Refresh cart
      } else {
        toast.error("Failed to add product to cart");
      }
    } catch (error) {
      console.error("Error adding to cart:", error);
      toast.error("Error adding product to cart");
    }
  };

  const addToWishlist = async (productId) => {
    try {
      const response = await api.post("/api/v1/wishlist/add", {
        product_id: productId,
      });
      
      if (response.data?.success || response.success) {
        toast.success("Product added to wishlist!");
        fetchWishlist(); // Refresh wishlist
      } else {
        toast.error("Failed to add product to wishlist");
      }
    } catch (error) {
      console.error("Error adding to wishlist:", error);
      toast.error("Error adding product to wishlist");
    }
  };

  const addNewProduct = async (e) => {
    if (e) e.preventDefault();
    
    try {
      // Validate required fields
      if (!newProduct.name || !newProduct.price || !newProduct.description) {
        toast.error("Please fill in all required fields");
        return;
      }

      if (parseFloat(newProduct.price) <= 0) {
        toast.error("Price must be greater than 0");
        return;
      }

      const productData = {
        name: newProduct.name.trim(),
        description: newProduct.description.trim(),
        price: parseFloat(newProduct.price),
        category: newProduct.category,
        stock_quantity: parseInt(newProduct.stock_quantity) || 0,
        image: newProduct.image || `https://via.placeholder.com/300x200?text=${encodeURIComponent(newProduct.name)}`
      };

      const response = await api.post("/api/v1/products", productData);
      
      if (response.data?.success || response.success) {
        toast.success("Product added successfully!");
        setShowAddProductModal(false);
        setNewProduct({
          name: "",
          description: "",
          price: "",
          category: "electronics",
          stock_quantity: "",
          image: ""
        });
        fetchProducts(); // Refresh products list
      } else {
        toast.error("Failed to add product");
      }
    } catch (error) {
      console.error("Error adding product:", error);
      toast.error(error.response?.data?.message || "Error adding product");
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewProduct(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const filteredProducts = products.filter((product) => {
    const matchesSearch =
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      selectedCategory === "all" || product.category === selectedCategory;
    const matchesPrice =
      product.price >= priceRange.min && product.price <= priceRange.max;
    return matchesSearch && matchesCategory && matchesPrice;
  });

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                {isRetailer ? "Product Catalog" : "Smart Shopping"}
              </h1>
              <p className="text-gray-600">
                {isRetailer
                  ? "Manage and view your product inventory"
                  : "Discover products tailored to your preferences"}
              </p>
            </div>
            
            {/* Add Product Button (Retailers Only) */}
            {isRetailer && (
              <button
                onClick={() => setShowAddProductModal(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 shadow-lg"
              >
                <Plus className="h-5 w-5" />
                <span>Add New Product</span>
              </button>
            )}
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Price Range */}
            <div className="flex space-x-2">
              <input
                type="number"
                placeholder="Min Price"
                value={priceRange.min}
                onChange={(e) =>
                  setPriceRange((prev) => ({
                    ...prev,
                    min: Number(e.target.value),
                  }))
                }
                className="w-1/2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="number"
                placeholder="Max Price"
                value={priceRange.max}
                onChange={(e) =>
                  setPriceRange((prev) => ({
                    ...prev,
                    max: Number(e.target.value),
                  }))
                }
                className="w-1/2 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
            >
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-48 object-cover"
              />
              <div className="p-4">
                <h3 className="font-semibold text-lg text-gray-900 mb-2">
                  {product.name}
                </h3>
                <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                  {product.description}
                </p>

                {/* Rating */}
                <div className="flex items-center mb-2">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`h-4 w-4 ${
                          i < Math.floor(product.rating)
                            ? "text-yellow-400 fill-current"
                            : "text-gray-300"
                        }`}
                      />
                    ))}
                  </div>
                  <span className="ml-2 text-sm text-gray-600">
                    ({product.rating})
                  </span>
                </div>

                {/* Price */}
                <div className="flex items-center justify-between mb-4">
                  <span className="text-2xl font-bold text-blue-600">
                    ${product.price}
                  </span>
                  <span className="text-sm text-gray-500 capitalize">
                    {product.category}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex space-x-2">
                  {isRetailer ? (
                    // Retailer view - show inventory management actions
                    <>
                      <button
                        onClick={() =>
                          window.open(`/inventory/edit/${product.id}`, "_blank")
                        }
                        className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
                      >
                        <Package className="h-4 w-4 mr-2" />
                        Manage Stock
                      </button>
                      <button
                        onClick={() =>
                          window.open(
                            `/analytics/product/${product.id}`,
                            "_blank",
                          )
                        }
                        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <BarChart3 className="h-4 w-4 text-green-600" />
                      </button>
                    </>
                  ) : (
                    // Customer view - show shopping actions
                    <>
                      <button
                        onClick={() => addToCart(product.id)}
                        className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
                      >
                        <ShoppingCart className="h-4 w-4 mr-2" />
                        Add to Cart
                      </button>
                      <button
                        onClick={() => addToWishlist(product.id)}
                        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <Heart className="h-4 w-4 text-red-500" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredProducts.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Search className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No products found
            </h3>
            <p className="text-gray-600">
              Try adjusting your search or filters
            </p>
          </div>
        )}

        {/* Add Product Modal (Retailer only) */}
        {isRetailer && (
          <>
            {showAddProductModal && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                <div className="bg-white rounded-lg shadow-md p-6 max-w-lg w-full">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    Add New Product
                  </h2>

                  {/* New Product Form */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Product Name
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={newProduct.name}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter product name"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        name="description"
                        value={newProduct.description}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter product description"
                        rows="3"
                      ></textarea>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Price
                        </label>
                        <input
                          type="number"
                          name="price"
                          value={newProduct.price}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Enter product price"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Category
                        </label>
                        <select
                          name="category"
                          value={newProduct.category}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          {categories.filter(cat => cat !== "all").map((category) => (
                            <option key={category} value={category}>
                              {category.charAt(0).toUpperCase() + category.slice(1)}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Stock Quantity
                      </label>
                      <input
                        type="number"
                        name="stock_quantity"
                        value={newProduct.stock_quantity}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter stock quantity"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Image URL
                      </label>
                      <input
                        type="text"
                        name="image"
                        value={newProduct.image}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter image URL"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end mt-4">
                    <button
                      type="button"
                      onClick={() => setShowAddProductModal(false)}
                      className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors mr-2"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      onClick={addNewProduct}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Add Product
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="mb-4">
              <button
                onClick={() => setShowAddProductModal(true)}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <Plus className="h-5 w-5 mr-2" />
                Add New Product
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Shopping;
