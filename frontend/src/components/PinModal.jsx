import React, { useState, useRef, useEffect } from 'react';
import { Lock, X } from 'lucide-react';
import { makePayment } from '../services/api';

const PinModal = ({ pendingPayment, onSuccess, onClose, userId }) => {
  const [pin, setPin] = useState(['', '', '', '']);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const inputRefs = useRef([]);

  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const handleChange = (index, value) => {
    if (value.length > 1) return;
    if (value && !/^\d+$/.test(value)) return;

    const newPin = [...pin];
    newPin[index] = value;
    setPin(newPin);
    setError('');

    // Move to next input
    if (value && index < 3) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all digits entered
    if (index === 3 && value) {
      handleSubmit(newPin.join(''));
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !pin[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = async (pinValue = pin.join('')) => {
    if (pinValue.length !== 4) {
      setError('Please enter 4-digit PIN');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await makePayment(
        pendingPayment.recipient,
        pendingPayment.amount,
        pinValue,
        userId
      );

      console.log('Payment response:', response);
      
      if (response.success) {
        console.log('Payment successful, calling onSuccess');
        onSuccess(response.data);
      } else {
        console.error('Payment failed:', response.message);
        setError(response.message || 'Payment failed');
        setPin(['', '', '', '']);
        inputRefs.current[0]?.focus();
      }
    } catch (error) {
      setError('Payment failed. Please try again.');
      setPin(['', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full p-6 animate-slide-in-up">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-100 p-3 rounded-full">
              <Lock className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Enter PIN</h3>
              <p className="text-sm text-gray-500">Confirm your payment</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Payment Details */}
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-4 mb-6 border border-indigo-100">
          <p className="text-sm text-gray-600 mb-1">Paying to</p>
          <p className="text-lg font-bold text-gray-900 capitalize mb-2">
            {pendingPayment?.recipient}
          </p>
          <p className="text-3xl font-bold text-indigo-600">
            ₹{pendingPayment?.amount.toLocaleString()}
          </p>
        </div>

        {/* PIN Input */}
        <div className="flex gap-3 justify-center mb-4">
          {pin.map((digit, index) => (
            <input
              key={index}
              ref={(el) => (inputRefs.current[index] = el)}
              type="password"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              className="w-14 h-14 text-center text-2xl font-bold border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition"
              disabled={loading}
            />
          ))}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-xl mb-4">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={() => handleSubmit()}
          disabled={loading || pin.join('').length !== 4}
          className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-4 rounded-xl hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? 'Processing...' : 'Confirm Payment'}
        </button>

        <p className="text-xs text-gray-500 text-center mt-4">
          Default PIN: 1234 (Demo)
        </p>
      </div>
    </div>
  );
};

export default PinModal;

