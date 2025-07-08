import React, { createContext, useContext, useState, useEffect } from 'react';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Backend API base URL - Use Codespace URL in production or localhost in development
  const getApiBaseUrl = () => {
    if (process.env.REACT_APP_API_URL) {
      return process.env.REACT_APP_API_URL;
    }
    
    // Check if we're in a GitHub Codespace
    const codespace = process.env.CODESPACE_NAME || window.location.hostname.includes('app.github.dev');
    if (codespace) {
      const codespaceBase = window.location.hostname.replace('-3001', '-5000').replace('-3000', '-5000');
      return `https://${codespaceBase}`;
    }
    
    return 'http://127.0.0.1:5000';
  };
  
  const API_BASE_URL = getApiBaseUrl();

  useEffect(() => {
    // Check for existing token on app start
    const token = localStorage.getItem('token');
    if (token) {
      // Validate token with backend
      validateToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const validateToken = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData.data);
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Token validation error:', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setLoading(true);
      
      console.log('🔄 Starting login request...', { email, API_BASE_URL });
      
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      console.log('📡 Login response received:', { status: response.status, ok: response.ok });

      const data = await response.json();
      console.log('📝 Login response data:', data);

      if (response.ok && data.success) {
        localStorage.setItem('token', data.token);
        setUser(data.user);
        toast.success('Login successful!');
        return { success: true };
      } else {
        toast.error(data.message || 'Login failed');
        return { success: false, error: data.message };
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      toast.error('Unable to connect to server. Please try again later.');
      return { success: false, error: 'Network error' };
    } finally {
      setLoading(false);
    }
  };

  const register = async (formData) => {
    try {
      setLoading(true);
      
      console.log('🔄 Starting registration request...', { email: formData.email, API_BASE_URL });
      
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: `${formData.firstName} ${formData.lastName}`,
          email: formData.email,
          password: formData.password,
          phone: formData.phone,
          userType: formData.userType,
          business_name: formData.businessName,  // Fix: use business_name instead of businessName
          businessType: formData.businessType
        }),
      });

      console.log('📡 Registration response received:', { status: response.status, ok: response.ok });

      const data = await response.json();
      console.log('📝 Registration response data:', data);

      if (response.ok && data.success) {
        localStorage.setItem('token', data.token);
        setUser(data.user);
        toast.success('Registration successful!');
        return { success: true };
      } else {
        const errorMessage = data.error || data.message || 'Registration failed';
        toast.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('❌ Registration error:', error);
      toast.error('Unable to connect to server. Please try again later.');
      return { success: false, error: 'Network error' };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    toast.success('Logged out successfully');
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    API_BASE_URL,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
