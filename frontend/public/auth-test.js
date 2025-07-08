/**
 * Frontend Authentication Test Script
 * Tests authentication functionality from browser console
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000';

// Test functions that can be run in browser console
window.authTests = {
  
  // Test 1: Backend Health Check
  async testBackendHealth() {
    console.log('🧪 Testing Backend Health...');
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`);
      const data = await response.json();
      
      if (response.ok) {
        console.log('✅ Backend Health: OK');
        console.log('📊 Response:', data);
        return true;
      } else {
        console.log('❌ Backend Health: FAILED');
        console.log('📊 Response:', data);
        return false;
      }
    } catch (error) {
      console.log('❌ Backend Health: ERROR');
      console.error('Error:', error);
      return false;
    }
  },

  // Test 2: User Registration
  async testRegistration(email = null) {
    console.log('🧪 Testing User Registration...');
    
    const testEmail = email || `testuser${Date.now()}@retailgenie.com`;
    const userData = {
      email: testEmail,
      password: 'testpass123',
      name: 'Test User',
      business_name: 'Test Business'
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        console.log('✅ Registration: SUCCESS');
        console.log('📊 User ID:', data.user?.id);
        console.log('🎫 Token:', data.token ? `${data.token.substring(0, 20)}...` : 'Missing');
        
        // Store for login test
        window.testUser = {
          email: testEmail,
          password: 'testpass123',
          token: data.token,
          user: data.user
        };
        
        return data;
      } else {
        console.log('❌ Registration: FAILED');
        console.log('📊 Response:', data);
        return null;
      }
    } catch (error) {
      console.log('❌ Registration: ERROR');
      console.error('Error:', error);
      return null;
    }
  },

  // Test 3: User Login
  async testLogin(email = 'demo@retailgenie.com', password = 'demo123456') {
    console.log('🧪 Testing User Login...');
    
    const loginData = {
      email: email,
      password: password
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        console.log('✅ Login: SUCCESS');
        console.log('📊 User:', data.user?.name);
        console.log('📧 Email:', data.user?.email);
        console.log('🎫 Token:', data.token ? `${data.token.substring(0, 20)}...` : 'Missing');
        
        // Store token for authenticated requests
        localStorage.setItem('authTestToken', data.token);
        window.currentUser = data.user;
        window.currentToken = data.token;
        
        return data;
      } else {
        console.log('❌ Login: FAILED');
        console.log('📊 Response:', data);
        return null;
      }
    } catch (error) {
      console.log('❌ Login: ERROR');
      console.error('Error:', error);
      return null;
    }
  },

  // Test 4: Authenticated Request
  async testAuthenticatedRequest(token = null) {
    console.log('🧪 Testing Authenticated Request...');
    
    const authToken = token || localStorage.getItem('authTestToken') || window.currentToken;
    
    if (!authToken) {
      console.log('❌ No token available. Please login first.');
      return null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/products`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        console.log('✅ Authenticated Request: SUCCESS');
        console.log('📊 Products Count:', data.count || 0);
        console.log('📦 Products:', data.data);
        return data;
      } else {
        console.log('❌ Authenticated Request: FAILED');
        console.log('📊 Response:', data);
        return null;
      }
    } catch (error) {
      console.log('❌ Authenticated Request: ERROR');
      console.error('Error:', error);
      return null;
    }
  },

  // Test 5: Frontend Context Integration
  async testFrontendAuth() {
    console.log('🧪 Testing Frontend Auth Context...');
    
    // Check if AuthContext is available
    if (window.React && window.AuthContext) {
      console.log('✅ AuthContext: Available');
    } else {
      console.log('ℹ️  AuthContext: Not directly accessible from console');
    }

    // Check localStorage for existing token
    const existingToken = localStorage.getItem('token');
    if (existingToken) {
      console.log('✅ Existing Token: Found');
      console.log('🎫 Token:', `${existingToken.substring(0, 20)}...`);
    } else {
      console.log('ℹ️  Existing Token: None found');
    }

    // Check if user is logged in via React state (if accessible)
    const userState = window.currentUser || localStorage.getItem('user');
    if (userState) {
      console.log('✅ User State: Found');
      console.log('👤 User:', userState);
    } else {
      console.log('ℹ️  User State: None found');
    }
  },

  // Complete Test Suite
  async runFullTest() {
    console.log('🚀 Running Complete Frontend Authentication Test Suite');
    console.log('=' * 60);
    
    const results = {};
    
    // Test 1: Health check
    console.log('\n1️⃣ Backend Health Check');
    results.health = await this.testBackendHealth();
    
    if (!results.health) {
      console.log('🛑 Backend not available. Stopping tests.');
      return results;
    }

    // Test 2: Registration  
    console.log('\n2️⃣ User Registration Test');
    results.registration = await this.testRegistration();
    
    // Test 3: Login
    console.log('\n3️⃣ User Login Test');
    if (results.registration) {
      results.login = await this.testLogin(window.testUser.email, window.testUser.password);
    } else {
      results.login = await this.testLogin(); // Try with demo user
    }
    
    // Test 4: Authenticated request
    console.log('\n4️⃣ Authenticated Request Test');
    results.authenticated = await this.testAuthenticatedRequest();
    
    // Test 5: Frontend integration
    console.log('\n5️⃣ Frontend Integration Test');
    await this.testFrontendAuth();
    
    // Summary
    console.log('\n' + '=' * 60);
    console.log('📊 TEST RESULTS SUMMARY:');
    console.log(`Backend Health: ${results.health ? '✅' : '❌'}`);
    console.log(`Registration: ${results.registration ? '✅' : '❌'}`);
    console.log(`Login: ${results.login ? '✅' : '❌'}`);
    console.log(`Authenticated Requests: ${results.authenticated ? '✅' : '❌'}`);
    
    const totalPassed = Object.values(results).filter(Boolean).length;
    const totalTests = Object.keys(results).length;
    
    console.log(`\n🎯 Overall: ${totalPassed}/${totalTests} tests passed`);
    
    if (totalPassed === totalTests) {
      console.log('🎉 ALL TESTS PASSED! Authentication system is working perfectly.');
    } else {
      console.log('⚠️  Some tests failed. Check the output above for details.');
    }
    
    return results;
  },

  // Cleanup function
  cleanup() {
    console.log('🧹 Cleaning up test data...');
    localStorage.removeItem('authTestToken');
    delete window.testUser;
    delete window.currentUser;
    delete window.currentToken;
    console.log('✅ Cleanup complete');
  }
};

// Auto-run tests when script loads
console.log('🔧 Frontend Authentication Test Script Loaded');
console.log('📝 Available commands:');
console.log('  authTests.testBackendHealth()     - Test backend connection');
console.log('  authTests.testRegistration()      - Test user registration');
console.log('  authTests.testLogin()             - Test user login');
console.log('  authTests.testAuthenticatedRequest() - Test authenticated API call');
console.log('  authTests.runFullTest()           - Run complete test suite');
console.log('  authTests.cleanup()               - Clean up test data');
console.log('');
console.log('🚀 To run all tests: authTests.runFullTest()');

// Export for global access
if (typeof module !== 'undefined' && module.exports) {
  module.exports = window.authTests;
}
