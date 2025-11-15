import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      getCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const getCurrentUser = async () => {
    try {
      const response = await axios.get('/api/auth/me');
      setUser(response.data.user);
    } catch (error) {
      console.error('Error getting current user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/login', {
        email,
        password
      });

      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('access_token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setUser(userData);
      toast.success('Login successful!');
      
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const signup = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/signup', {
        email,
        password
      });

      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('access_token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setUser(userData);
      toast.success('Account created successfully!');
      
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Signup failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      delete axios.defaults.headers.common['Authorization'];
      setUser(null);
      toast.success('Logged out successfully');
    }
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
