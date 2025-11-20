import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Wallet } from 'lucide-react';
import { loginWithGoogle, isAuthenticated } from '../services/auth';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const googleButtonRef = useRef(null);

  useEffect(() => {
    // Redirect if already logged in
    if (isAuthenticated()) {
      navigate('/');
    }

    // Load Google Identity Services script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      initializeGoogleSignIn();
    };
    
    document.body.appendChild(script);

    return () => {
      // Cleanup script on unmount
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, [navigate]);

  const initializeGoogleSignIn = () => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    
    if (!clientId || clientId === 'your_google_client_id.apps.googleusercontent.com') {
      console.log('Google Client ID not configured');
      return;
    }

    if (window.google && googleButtonRef.current) {
      console.log('Rendering Google Sign-In button');
      
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredentialResponse,
      });

      // Render the button
      window.google.accounts.id.renderButton(
        googleButtonRef.current,
        {
          theme: 'outline',
          size: 'large',
          width: googleButtonRef.current.offsetWidth,
          text: 'signin_with',
          shape: 'rectangular',
        }
      );
    }
  };


  const handleCredentialResponse = async (response) => {
    console.log('Google credential received');
    setLoading(true);
    setError('');
    
    try {
      // Send Google token to our backend and get JWT
      console.log('Sending token to backend...');
      await loginWithGoogle(response.credential);
      
      console.log('Login successful! Redirecting...');
      // Redirect to main app
      navigate('/');
    } catch (err) {
      console.error('Auth error:', err);
      setError(err.message || 'Authentication failed. Please try Demo Mode.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Wallet className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to VoicePay</h1>
          <p className="text-gray-600">AI-powered voice payments made simple</p>
        </div>

        {/* Features List */}
        <div className="bg-gray-50 rounded-xl p-4 mb-6">
          <p className="text-sm font-semibold text-gray-700 mb-3">What you can do:</p>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Make payments with voice commands</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Check balance and transactions</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Smart investment suggestions</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Get ₹12,000 starting bonus</span>
            </li>
          </ul>
        </div>

        {/* Google Sign-In Button Container */}
        <div 
          ref={googleButtonRef}
          className="w-full mb-4"
          style={{ minHeight: '44px' }}
        >
          {/* Google button will be rendered here by Google Identity Services */}
          {loading && (
            <div className="flex items-center justify-center py-3">
              <div className="w-6 h-6 border-2 border-gray-300 border-t-indigo-600 rounded-full animate-spin"></div>
              <span className="ml-3 text-gray-600">Signing in...</span>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-xl mb-4">
            <p className="font-semibold mb-1">⚠️ Google Sign-In Issue</p>
            <p>{error}</p>
          </div>
        )}
        
        {/* Info Message */}
        {!import.meta.env.VITE_GOOGLE_CLIENT_ID && (
          <div className="bg-blue-50 border border-blue-200 text-blue-600 text-xs p-3 rounded-xl mb-4">
            <p className="font-semibold mb-1">💡 Quick Tip:</p>
            <p>Google OAuth not set up yet. Use <strong>Demo Mode</strong> below to try the app instantly!</p>
          </div>
        )}

        {/* Demo Mode Button */}
        <div className="text-center mt-4">
          <p className="text-sm text-gray-500 mb-2">or</p>
          <button
            onClick={() => {
              // Demo user - no Google OAuth needed
              const demoUser = {
                id: 1,
                name: 'Demo User',
                email: 'demo@voicepay.com',
                balance: 12000
              };
              localStorage.setItem('access_token', 'demo-token');
              localStorage.setItem('user', JSON.stringify(demoUser));
              navigate('/');
            }}
            className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
          >
            Continue as Demo User
          </button>
        </div>

        {/* Footer */}
        <p className="text-xs text-gray-400 text-center mt-6">
          By signing in, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
};

export default Login;
