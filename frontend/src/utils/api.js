const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getAuthHeaders() {
    const token = localStorage.getItem("token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getAuthHeaders(),
      ...options,
      credentials: 'include', 
    };

    try {
      const response = await fetch(url, config);
      
      // Check if response is OK
      if (!response.ok) {
        // Try to get error message from response
        let errorMessage;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorData.error || `HTTP error! status: ${response.status}`;
          } catch {
            errorMessage = `HTTP error! status: ${response.status}`;
          }
        } else {
          // Server returned HTML (like 404/405 error page)
          const text = await response.text();
          errorMessage = `Server error: ${response.status} - ${text.substring(0, 100)}...`;
        }
        
        throw new Error(errorMessage);
      }

      // Parse JSON response
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        // Non-JSON response
        const text = await response.text();
        throw new Error(`Expected JSON response but got: ${text.substring(0, 100)}...`);
      }
      
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  // HTTP convenience methods
  async get(endpoint) {
    return this.request(endpoint, {
      method: "GET",
    });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, {
      method: "DELETE",
    });
  }

  // Auth endpoints
  async login(credentials) {
    return this.request("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  }

  async register(userData) {
    return this.request("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  }

  async getProfile() {
    return this.request("/api/v1/auth/profile");
  }

  // Product endpoints
  async getProducts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(
      `/api/v1/products${queryString ? `?${queryString}` : ""}`,
    );
  }

  async createProduct(productData) {
    return this.request("/api/v1/products", {
      method: "POST",
      body: JSON.stringify(productData),
    });
  }

  async getProduct(productId) {
    return this.request(`/api/v1/products/${productId}`);
  }

  // AI Chat endpoints
  async chatWithAI(message, context = {}) {
    return this.request("/api/v1/ai/chat", {
      method: "POST",
      body: JSON.stringify({ message, context }),
    });
  }

  async getAIRecommendations(preferences = {}) {
    return this.request("/api/v1/ai/recommendations", {
      method: "POST",
      body: JSON.stringify(preferences),
    });
  }

  // Analytics endpoints
  async getDashboardData() {
    return this.request("/api/v1/analytics/dashboard");
  }

  async getSalesAnalytics(period = "7d") {
    return this.request(`/api/v1/analytics/sales?period=${period}`);
  }

  // Inventory endpoints
  async getInventoryStatus() {
    return this.request("/api/v1/inventory/status");
  }

  async getLowStockItems() {
    return this.request("/api/v1/inventory/low-stock");
  }

  // Feedback endpoints
  async getFeedback() {
    return this.request("/api/v1/feedback");
  }

  async submitFeedback(feedbackData) {
    return this.request("/api/v1/feedback", {
      method: "POST",
      body: JSON.stringify(feedbackData),
    });
  }

  // Health check
  async getHealth() {
    return this.request("/api/v1/health");
  }

  // Database operations
  async getDatabaseStatus() {
    return this.request("/api/v1/database/status");
  }

  async initializeDatabase() {
    return this.request("/api/v1/database/init", {
      method: "POST",
    });
  }
  
  // Customer API Methods
  async getCustomers() {
    return this.request('/api/v1/customers', {
      method: 'GET'
    });
  }

  async addCustomer(customerData) {
    return this.request('/api/v1/customers', {
      method: 'POST',
      body: JSON.stringify(customerData)
    });
  }

  async updateCustomer(customerId, customerData) {
    return this.request(`/api/v1/customers/${customerId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(customerData)
    });
  }

  async deleteCustomer(customerId) {
    return this.request(`/api/v1/customers/${customerId}`, {
      method: 'DELETE'
    });
  }

  async getCustomerDetails(customerId) {
    return this.request(`/api/v1/customers/${customerId}`, {
      method: 'GET'
    });
  }
}

const api = new ApiService();
export { api };
export default api;
