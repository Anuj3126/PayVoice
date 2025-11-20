import React from 'react';
import { TrendingUp, Award, PiggyBank, ArrowUp, ArrowDown } from 'lucide-react';

const InvestmentAnalyticsCards = ({ userData }) => {
  const potentialEarnings = userData?.investments?.total ? (userData.investments.total * 0.12).toFixed(0) : '0';
  const topPerformer = userData?.investments?.gold > 0 ? 'Gold' : 'None';
  const invested = userData?.investments?.total?.toFixed(0) || '0';
  const goldReturn = userData?.investments?.gold ? ((userData.investments.gold - (userData.investments.gold / 1.08)) / (userData.investments.gold / 1.08) * 100).toFixed(1) : '0';

  return (
    <div className="mb-6 md:mb-8">
      <div className="flex items-center justify-between mb-4 md:mb-6">
        <h2 className="text-xl md:text-2xl font-bold text-gray-800">Investment Analytics</h2>
        <span className="text-xs md:text-sm text-gray-500">Updated now</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        {/* Potential Earnings */}
        <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-2xl p-6 border-2 border-emerald-200 hover:border-emerald-300 transition-all hover:shadow-lg">
          <div className="flex items-start justify-between mb-4">
            <div className="bg-emerald-100 p-3 rounded-xl">
              <TrendingUp className="w-6 h-6 text-emerald-600" />
            </div>
            <div className="flex items-center gap-1 text-emerald-600 text-sm font-semibold">
              <ArrowUp className="w-4 h-4" />
              <span>12% Est.</span>
            </div>
          </div>
          
          <h3 className="text-gray-600 text-sm font-medium mb-2">Potential Earnings</h3>
          <p className="text-3xl font-bold text-gray-900 mb-1">₹{parseInt(potentialEarnings).toLocaleString('en-IN')}</p>
          <p className="text-xs text-gray-500">Projected annual returns</p>
        </div>

        {/* Top Performer */}
        <div className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-2xl p-6 border-2 border-amber-200 hover:border-amber-300 transition-all hover:shadow-lg">
          <div className="flex items-start justify-between mb-4">
            <div className="bg-amber-100 p-3 rounded-xl">
              <Award className="w-6 h-6 text-amber-600" />
            </div>
            <div className="flex items-center gap-1 text-amber-600 text-sm font-semibold">
              <ArrowUp className="w-4 h-4" />
              <span>+{goldReturn}%</span>
            </div>
          </div>
          
          <h3 className="text-gray-600 text-sm font-medium mb-2">Top Performer</h3>
          <p className="text-3xl font-bold text-gray-900 mb-1">{topPerformer}</p>
          <p className="text-xs text-gray-500">Best investment this month</p>
        </div>

        {/* Total Invested */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border-2 border-blue-200 hover:border-blue-300 transition-all hover:shadow-lg">
          <div className="flex items-start justify-between mb-4">
            <div className="bg-blue-100 p-3 rounded-xl">
              <PiggyBank className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex items-center gap-1 text-blue-600 text-sm font-semibold">
              <span>Active</span>
            </div>
          </div>
          
          <h3 className="text-gray-600 text-sm font-medium mb-2">Total Invested</h3>
          <p className="text-3xl font-bold text-gray-900 mb-1">₹{parseInt(invested).toLocaleString('en-IN')}</p>
          <p className="text-xs text-gray-500">Across all investments</p>
        </div>
      </div>
    </div>
  );
};

export default InvestmentAnalyticsCards;

