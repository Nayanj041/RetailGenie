// Test connectivity from the frontend to backend
const testBackendConnection = async () => {
  console.log("🔍 Testing backend connectivity...");

  const endpoints = [
    "http://localhost:5000/api/v1/health",
    "http://127.0.0.1:5000/api/v1/health",
  ];

  for (const endpoint of endpoints) {
    try {
      console.log(`Testing: ${endpoint}`);
      const response = await fetch(endpoint, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      console.log(`✅ ${endpoint} - Status: ${response.status}`);
      const data = await response.json();
      console.log(`   Response:`, data);
    } catch (error) {
      console.error(`❌ ${endpoint} - Error:`, error.message);
    }
  }

  // Test login endpoint
  try {
    console.log("Testing login endpoint...");
    const response = await fetch("http://127.0.0.1:5000/api/v1/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: "demo@retailgenie.com",
        password: "demo123456",
      }),
    });

    console.log(`✅ Login - Status: ${response.status}`);
    const data = await response.json();
    console.log(`   Login Response:`, data);
  } catch (error) {
    console.error(`❌ Login - Error:`, error.message);
  }
};

testBackendConnection();
