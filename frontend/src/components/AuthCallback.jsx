import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { setToken } from '../services/auth';

const AuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    const error = searchParams.get('message');

    if (token) {
      // Save token and redirect to app
      setToken(token);
      navigate('/', { replace: true });
    } else if (error) {
      // Handle error
      console.error('Auth error:', error);
      alert(`Authentication failed: ${error}`);
      navigate('/login', { replace: true });
    } else {
      // No token or error, redirect to login
      navigate('/login', { replace: true });
    }
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center">
      <div className="bg-white rounded-3xl shadow-2xl p-8 text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <p className="text-xl font-semibold text-gray-900">
          Completing sign in...
        </p>
      </div>
    </div>
  );
};

export default AuthCallback;

