import React, { useState } from 'react';
import { TrendingUp, X, Sparkles } from 'lucide-react';
import { makeInvestment } from '../services/api';

const InvestmentNudge = ({ nudge, onInvest, onClose, userId }) => {
  const [loading, setLoading] = useState(false);

  const handleInvest = async () => {
    setLoading(true);
    try {
      const response = await makeInvestment(nudge.amount, userId, nudge.type);
      if (response.success) {
        onInvest();
      }
    } catch (error) {
      console.error('Investment failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full p-6 animate-slide-in-up">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-yellow-400 to-orange-500 p-3 rounded-full">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Smart Invest</h3>
              <p className="text-sm text-gray-500">Build your wealth</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Nudge Message */}
        <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-4 mb-6 border border-yellow-200">
          <div className="flex items-start gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-yellow-600 mt-0.5" />
            <p className="text-gray-800 font-medium">{nudge.message}</p>
          </div>
          
          <div className="bg-white rounded-xl p-3 border border-yellow-200">
            <p className="text-sm text-gray-600 mb-1">Investment Amount</p>
            <p className="text-3xl font-bold text-orange-600">
              ₹{nudge.amount}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              in {nudge.type.toUpperCase()}
            </p>
          </div>
        </div>

        {/* Benefits */}
        <div className="bg-gray-50 rounded-xl p-4 mb-6">
          <p className="text-sm font-medium text-gray-700 mb-2">Why invest?</p>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Grow your wealth with small amounts</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Gold is a stable investment</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">✓</span>
              <span>Round-off savings add up fast</span>
            </li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-gray-100 text-gray-700 font-semibold py-3 rounded-xl hover:bg-gray-200 transition"
          >
            Maybe Later
          </button>
          <button
            onClick={handleInvest}
            disabled={loading}
            className="flex-1 bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-semibold py-3 rounded-xl hover:from-yellow-600 hover:to-orange-600 disabled:opacity-50 transition"
          >
            {loading ? 'Investing...' : `Invest ₹${nudge.amount}`}
          </button>
        </div>
      </div>
    </div>
  );
};

export default InvestmentNudge;

