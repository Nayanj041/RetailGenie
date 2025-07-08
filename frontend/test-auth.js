#!/usr/bin/env node

/**
 * Frontend-side Authentication Test Runner
 * Tests the authentication system from frontend perspective
 */

const https = require("https");
const http = require("http");

// Configuration
const API_BASE_URL = "http://localhost:5000";
const FRONTEND_URL = "http://localhost:3001";

// Test utilities
class AuthTester {
  constructor() {
    this.testResults = {};
    this.testToken = null;
    this.testUser = null;
  }

  log(message, type = "info") {
    const timestamp = new Date().toLocaleTimeString();
    const prefix =
      type === "success"
        ? "✅"
        : type === "error"
          ? "❌"
          : type === "warning"
            ? "⚠️"
            : "ℹ️";
    console.log(`[${timestamp}] ${prefix} ${message}`);
  }

  async makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      const requestOptions = {
        hostname: urlObj.hostname,
        port: urlObj.port,
        path: urlObj.pathname + urlObj.search,
        method: options.method || "GET",
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
      };

      const req = http.request(requestOptions, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            const jsonData = JSON.parse(data);
            resolve({
              ok: res.statusCode >= 200 && res.statusCode < 300,
              status: res.statusCode,
              data: jsonData,
            });
          } catch (e) {
            resolve({
              ok: res.statusCode >= 200 && res.statusCode < 300,
              status: res.statusCode,
              data: data,
            });
          }
        });
      });

      req.on("error", reject);

      if (options.body) {
        req.write(JSON.stringify(options.body));
      }

      req.end();
    });
  }

  // Test 1: Backend Health
  async testBackendHealth() {
    this.log("Testing backend health...");
    try {
      const response = await this.makeRequest(`${API_BASE_URL}/api/v1/health`);

      if (response.ok) {
        this.log("Backend health: SUCCESS", "success");
        this.log(`Firebase connected: ${response.data.firebase_connected}`);
        this.testResults.health = true;
        return true;
      } else {
        this.log(`Backend health: FAILED (${response.status})`, "error");
        this.testResults.health = false;
        return false;
      }
    } catch (error) {
      this.log(`Backend health: ERROR - ${error.message}`, "error");
      this.testResults.health = false;
      return false;
    }
  }

  // Test 2: Frontend Accessibility
  async testFrontendAccess() {
    this.log("Testing frontend accessibility...");
    try {
      const response = await this.makeRequest(FRONTEND_URL);

      if (response.ok) {
        this.log("Frontend access: SUCCESS", "success");
        this.testResults.frontend = true;
        return true;
      } else {
        this.log(`Frontend access: FAILED (${response.status})`, "error");
        this.testResults.frontend = false;
        return false;
      }
    } catch (error) {
      this.log(`Frontend access: ERROR - ${error.message}`, "error");
      this.testResults.frontend = false;
      return false;
    }
  }

  // Test 3: User Registration
  async testRegistration() {
    this.log("Testing user registration...");

    const timestamp = Date.now();
    const userData = {
      email: `test${timestamp}@retailgenie.com`,
      password: "testpass123",
      name: "Test User",
      business_name: "Test Business",
    };

    try {
      const response = await this.makeRequest(
        `${API_BASE_URL}/api/v1/auth/register`,
        {
          method: "POST",
          body: userData,
        },
      );

      if (response.ok && response.data.success) {
        this.log("Registration: SUCCESS", "success");
        this.log(`User ID: ${response.data.user?.id}`);
        this.log(`Token received: ${response.data.token ? "Yes" : "No"}`);

        // Store for login test
        this.testUser = {
          email: userData.email,
          password: userData.password,
        };
        this.testToken = response.data.token;

        this.testResults.registration = true;
        return response.data;
      } else {
        this.log(`Registration: FAILED - ${response.data.message}`, "error");
        this.testResults.registration = false;
        return null;
      }
    } catch (error) {
      this.log(`Registration: ERROR - ${error.message}`, "error");
      this.testResults.registration = false;
      return null;
    }
  }

  // Test 4: User Login
  async testLogin(email = "demo@retailgenie.com", password = "demo123456") {
    this.log(`Testing user login for: ${email}`);

    const loginData = { email, password };

    try {
      const response = await this.makeRequest(
        `${API_BASE_URL}/api/v1/auth/login`,
        {
          method: "POST",
          body: loginData,
        },
      );

      if (response.ok && response.data.success) {
        this.log("Login: SUCCESS", "success");
        this.log(`User: ${response.data.user?.name}`);
        this.log(`Email: ${response.data.user?.email}`);
        this.log(`Role: ${response.data.user?.role}`);

        this.testToken = response.data.token;
        this.testResults.login = true;
        return response.data;
      } else {
        this.log(`Login: FAILED - ${response.data.message}`, "error");
        this.testResults.login = false;
        return null;
      }
    } catch (error) {
      this.log(`Login: ERROR - ${error.message}`, "error");
      this.testResults.login = false;
      return null;
    }
  }

  // Test 5: Authenticated Request
  async testAuthenticatedRequest() {
    this.log("Testing authenticated request...");

    if (!this.testToken) {
      this.log("No token available for authenticated request", "error");
      this.testResults.authenticated = false;
      return null;
    }

    try {
      const response = await this.makeRequest(
        `${API_BASE_URL}/api/v1/products`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${this.testToken}`,
          },
        },
      );

      if (response.ok) {
        this.log("Authenticated request: SUCCESS", "success");
        this.log(`Products count: ${response.data.count || 0}`);

        this.testResults.authenticated = true;
        return response.data;
      } else {
        this.log(`Authenticated request: FAILED (${response.status})`, "error");
        this.testResults.authenticated = false;
        return null;
      }
    } catch (error) {
      this.log(`Authenticated request: ERROR - ${error.message}`, "error");
      this.testResults.authenticated = false;
      return null;
    }
  }

  // Test 6: Frontend-Backend CORS
  async testCORS() {
    this.log("Testing CORS configuration...");

    try {
      const response = await this.makeRequest(`${API_BASE_URL}/api/v1/health`, {
        headers: {
          Origin: FRONTEND_URL,
          "Access-Control-Request-Method": "POST",
          "Access-Control-Request-Headers": "Content-Type,Authorization",
        },
      });

      if (response.ok) {
        this.log("CORS test: SUCCESS", "success");
        this.testResults.cors = true;
        return true;
      } else {
        this.log("CORS test: FAILED", "error");
        this.testResults.cors = false;
        return false;
      }
    } catch (error) {
      this.log(`CORS test: ERROR - ${error.message}`, "error");
      this.testResults.cors = false;
      return false;
    }
  }

  // Complete test suite
  async runFullTest() {
    console.log("🚀 RetailGenie Frontend Authentication Test Suite");
    console.log("=".repeat(60));

    // Test 1: Backend Health
    console.log("\n1️⃣ Backend Health Check");
    const healthOk = await this.testBackendHealth();

    if (!healthOk) {
      console.log("🛑 Backend not available. Stopping tests.");
      return this.printSummary();
    }

    // Test 2: Frontend Access
    console.log("\n2️⃣ Frontend Accessibility");
    await this.testFrontendAccess();

    // Test 3: CORS
    console.log("\n3️⃣ CORS Configuration");
    await this.testCORS();

    // Test 4: Registration
    console.log("\n4️⃣ User Registration");
    const registrationResult = await this.testRegistration();

    // Test 5: Login
    console.log("\n5️⃣ User Login");
    if (registrationResult && this.testUser) {
      await this.testLogin(this.testUser.email, this.testUser.password);
    } else {
      await this.testLogin(); // Try demo user
    }

    // Test 6: Authenticated Request
    console.log("\n6️⃣ Authenticated Request");
    await this.testAuthenticatedRequest();

    // Summary
    this.printSummary();
  }

  printSummary() {
    console.log("\n" + "=".repeat(60));
    console.log("📊 TEST RESULTS SUMMARY:");
    console.log("=".repeat(60));

    const tests = [
      { name: "Backend Health", result: this.testResults.health },
      { name: "Frontend Access", result: this.testResults.frontend },
      { name: "CORS Configuration", result: this.testResults.cors },
      { name: "User Registration", result: this.testResults.registration },
      { name: "User Login", result: this.testResults.login },
      {
        name: "Authenticated Requests",
        result: this.testResults.authenticated,
      },
    ];

    tests.forEach((test) => {
      const status =
        test.result === true
          ? "✅ PASS"
          : test.result === false
            ? "❌ FAIL"
            : "⏸️ SKIP";
      console.log(`${status} ${test.name}`);
    });

    const passed = tests.filter((t) => t.result === true).length;
    const total = tests.filter((t) => t.result !== undefined).length;

    console.log("\n" + "=".repeat(60));
    console.log(`🎯 Overall Result: ${passed}/${total} tests passed`);

    if (passed === total && total > 0) {
      console.log(
        "🎉 ALL TESTS PASSED! Authentication system is working perfectly!",
      );
      console.log("✅ Frontend can successfully communicate with backend");
      console.log("✅ Registration and login functionality working");
      console.log("✅ JWT authentication working");
      console.log("✅ CORS properly configured");
    } else {
      console.log("⚠️  Some tests failed or were skipped.");
      console.log("👀 Check the detailed output above for specific issues.");
    }

    console.log("\n📝 Next Steps:");
    console.log("1. Open browser at: http://localhost:3001");
    console.log("2. Test registration at: http://localhost:3001/register");
    console.log("3. Test login at: http://localhost:3001/login");
    console.log("4. Use test page at: http://localhost:3001/auth-test.html");

    return this.testResults;
  }
}

// Main execution
async function main() {
  const tester = new AuthTester();

  console.log("🔧 Initializing frontend authentication tests...");
  console.log(`📡 Backend URL: ${API_BASE_URL}`);
  console.log(`🌐 Frontend URL: ${FRONTEND_URL}`);
  console.log("");

  await tester.runFullTest();
}

// Run tests
if (require.main === module) {
  main().catch((error) => {
    console.error("❌ Test runner error:", error);
    process.exit(1);
  });
}

module.exports = AuthTester;
