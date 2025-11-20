/**
 * Authentication service for VoicePay
 * Handles Google OAuth and JWT tokens
 */

const API_BASE = 'http://localhost:8000';

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  const token = localStorage.getItem('access_token');
  const user = localStorage.getItem('user');
  return !!(token && user);
};

/**
 * Get current user from localStorage
 */
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr);
  } catch (e) {
    console.error('Error parsing user data:', e);
    return null;
  }
};

/**
 * Get auth token
 */
export const getAuthToken = () => {
  return localStorage.getItem('access_token');
};

/**
 * Get auth token (alias for backward compatibility)
 */
export const getToken = getAuthToken;

/**
 * Authenticate with Google OAuth token
 */
export const loginWithGoogle = async (googleToken) => {
  try {
    const response = await fetch(`${API_BASE}/api/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: googleToken,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Authentication failed');
    }

    const data = await response.json();
    
    // Store JWT token and user info
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data.user;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

/**
 * Fetch current user info from API (with JWT)
 */
export const fetchCurrentUser = async () => {
  try {
    const token = getAuthToken();
    if (!token) throw new Error('No auth token');

    const response = await fetch(`${API_BASE}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }

    const user = await response.json();
    
    // Update localStorage
    localStorage.setItem('user', JSON.stringify(user));
    
    return user;
  } catch (error) {
    console.error('Error fetching user:', error);
    // If fetch fails, try to return cached user
    return getCurrentUser();
  }
};

/**
 * Logout user
 */
export const logout = async () => {
  try {
    const token = getAuthToken();
    
    if (token) {
      // Call backend logout endpoint
      await fetch(`${API_BASE}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    }
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Clear local storage regardless
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }
};

/**
 * Make authenticated API request
 */
export const authenticatedFetch = async (url, options = {}) => {
  const token = getAuthToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // Add auth token if available
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  // If unauthorized, redirect to login
  if (response.status === 401) {
    logout();
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  
  return response;
};
