import React from 'react';
import { TrendingUp, X, Sparkles, BarChart3, DollarSign } from 'lucide-react';

const MonthlyInvestmentAnalysis = ({ analysis, onClose, onViewDetails }) => {
  const { message, analysis: data, recommendation } = analysis;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-lg w-full p-6 animate-slide-in-up max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-green-400 to-emerald-500 p-3 rounded-full">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Monthly Investment Insight</h3>
              <p className="text-sm text-gray-500">Based on your spending</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-4 border border-blue-100">
            <p className="text-sm text-blue-600 mb-1">Transactions</p>
            <p className="text-3xl font-bold text-blue-700">{data.transaction_count}</p>
            <p className="text-xs text-blue-500 mt-1">this month</p>
          </div>
          
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-4 border border-purple-100">
            <p className="text-sm text-purple-600 mb-1">Round-off Total</p>
            <p className="text-3xl font-bold text-purple-700">₹{data.total_roundoff}</p>
            <p className="text-xs text-purple-500 mt-1">could invest</p>
          </div>
        </div>

        {/* Main Message */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-5 mb-6 border border-green-200">
          <div className="flex items-start gap-3 mb-4">
            <Sparkles className="w-6 h-6 text-green-600 mt-1 flex-shrink-0" />
            <div>
              <h4 className="font-bold text-gray-900 mb-2">What if you invested?</h4>
              <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-line">
                {message}
              </p>
            </div>
          </div>

          {/* Potential Earnings Highlight */}
          <div className="bg-white rounded-xl p-4 border border-green-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Potential Earnings</span>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-green-600">
                ₹{data.potential_earnings}
              </span>
              <span className="text-lg text-gray-500">
                (+{data.return_percentage}%)
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Estimated returns for {data.current_month}
            </p>
          </div>
        </div>

        {/* Investment Recommendation */}
        <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl p-5 mb-6 border border-yellow-200">
          <div className="flex items-center gap-2 mb-3">
            <DollarSign className="w-5 h-5 text-orange-600" />
            <h4 className="font-bold text-gray-900">Top Performer This Week</h4>
          </div>
          <div className="bg-white rounded-xl p-4 border border-orange-200">
            <p className="text-lg font-bold text-gray-900 mb-1">
              {recommendation.name}
            </p>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-green-600">
                +{data.weekly_return}%
              </span>
              <span className="text-sm text-gray-500">this week</span>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-gray-50 rounded-xl p-4 mb-6">
          <p className="text-sm font-medium text-gray-700 mb-3">💡 How Auto-Invest Works:</p>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">1.</span>
              <span>Round up every payment to the nearest ₹10</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">2.</span>
              <span>Automatically invest the difference</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-500 mt-0.5">3.</span>
              <span>Watch your savings grow over time</span>
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
            onClick={onViewDetails}
            className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold py-3 rounded-xl hover:from-green-600 hover:to-emerald-600 transition"
          >
            Enable Auto-Invest
          </button>
        </div>

        <p className="text-xs text-gray-400 text-center mt-4">
          * Returns are estimated based on historical data
        </p>
      </div>
    </div>
  );
};

export default MonthlyInvestmentAnalysis;

