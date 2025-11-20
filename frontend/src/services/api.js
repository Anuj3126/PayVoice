import axios from 'axios';
import { getToken } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const getAllUsers = async () => {
  try {
    const response = await api.get('/users');
    return response.data.data.users;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};

export const getUserData = async (userId) => {
  try {
    // Add timestamp to prevent caching
    const timestamp = new Date().getTime();
    const response = await api.get(`/user/${userId}?_=${timestamp}`);
    console.log(`[API] Fetched user data for user ${userId}:`, response.data.data);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching user data:', error);
    throw error;
  }
};

export const processVoiceCommand = async (text, userId, language = 'en') => {
  try {
    const response = await api.post('/process_voice', { text, language, user_id: userId });
    return response.data;
  } catch (error) {
    console.error('Error processing voice command:', error);
    throw error;
  }
};

export const makePayment = async (recipient, amount, pin, userId) => {
  try {
    const response = await api.post('/payment', { recipient, amount, pin, user_id: userId });
    return response.data;
  } catch (error) {
    console.error('Error making payment:', error);
    throw error;
  }
};

export const makeInvestment = async (amount, userId, type = 'gold') => {
  try {
    const response = await api.post('/invest', { amount, type, user_id: userId });
    return response.data;
  } catch (error) {
    console.error('Error making investment:', error);
    throw error;
  }
};

export const getBalance = async (userId) => {
  try {
    const response = await api.get(`/balance/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching balance:', error);
    throw error;
  }
};

export const getTransactions = async (userId, limit = 10) => {
  try {
    const response = await api.get(`/transactions/${userId}?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching transactions:', error);
    throw error;
  }
};

export const getInvestmentAnalysis = async (userId) => {
    try {
        const response = await api.get(`/investment-analysis/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching investment analysis:', error);
        throw error;
    }
};

export const savePhoneNumber = async (userId, phoneNumber) => {
    try {
        const response = await api.post(`/user/${userId}/phone`, {
            phone_number: phoneNumber
        });
        return response.data;
    } catch (error) {
        console.error('Error saving phone number:', error);
        throw error;
    }
};

export const getTopPerformer = async () => {
  try {
    const response = await api.get('/top-performer');
    return response.data;
  } catch (error) {
    console.error('Error fetching top performer:', error);
    throw error;
  }
};

export const getPortfolio = async (userId) => {
  try {
    const response = await api.get(`/portfolio/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching portfolio:', error);
    throw error;
  }
};

