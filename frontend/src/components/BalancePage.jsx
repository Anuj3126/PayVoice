import React from 'react';
import { ArrowLeft, Wallet, TrendingUp, PieChart, Activity } from 'lucide-react';

const BalancePage = ({ userData, onBack }) => {
  const balance = userData?.balance || 0;
  const invested = userData?.investments?.total || 0;
  const gold = userData?.investments?.gold || 0;
  const totalWealth = balance + invested;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 mb-6 hover:bg-white/10 px-4 py-2 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back</span>
        </button>
        
        <h1 className="text-3xl font-bold mb-2">Balance & Investments</h1>
        <p className="text-indigo-100">Your complete financial overview</p>
      </div>

      {/* Main Balance Card */}
      <div className="max-w-6xl mx-auto px-8 -mt-8">
        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl p-8 shadow-2xl mb-8 text-white">
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-blue-100 text-sm mb-2">Total Wealth</p>
              <p className="text-5xl font-bold mb-2">₹{totalWealth.toLocaleString('en-IN')}</p>
              <p className="text-blue-100 text-sm">Updated just now</p>
            </div>
            <div className="bg-white/20 backdrop-blur p-4 rounded-2xl">
              <Wallet className="w-10 h-10" />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white/10 backdrop-blur rounded-xl p-4">
              <p className="text-blue-100 text-xs mb-1">Available</p>
              <p className="text-2xl font-bold">₹{balance.toLocaleString('en-IN')}</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-xl p-4">
              <p className="text-blue-100 text-xs mb-1">Invested</p>
              <p className="text-2xl font-bold">₹{invested.toLocaleString('en-IN')}</p>
            </div>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Available Balance Details */}
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-green-100 p-3 rounded-xl">
                <Wallet className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Available Balance</h3>
                <p className="text-sm text-gray-500">Ready to use</p>
              </div>
            </div>
            
            <p className="text-4xl font-bold text-gray-900 mb-4">₹{balance.toLocaleString('en-IN')}</p>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Status</span>
                <span className="font-semibold text-green-600">Active</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Account Type</span>
                <span className="font-semibold text-gray-900">Premium</span>
              </div>
            </div>
          </div>

          {/* Investment Summary */}
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-blue-100 p-3 rounded-xl">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Total Invested</h3>
                <p className="text-sm text-gray-500">Active investments</p>
              </div>
            </div>
            
            <p className="text-4xl font-bold text-gray-900 mb-4">₹{invested.toLocaleString('en-IN')}</p>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Gold</span>
                <span className="font-semibold text-gray-900">₹{gold.toLocaleString('en-IN')}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Est. Returns</span>
                <span className="font-semibold text-green-600">+12% p.a.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Wealth Distribution */}
        <div className="bg-white rounded-2xl p-6 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-purple-100 p-3 rounded-xl">
              <PieChart className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">Wealth Distribution</h3>
              <p className="text-sm text-gray-500">How your money is allocated</p>
            </div>
          </div>

          <div className="space-y-4">
            {/* Balance Bar */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Available Cash</span>
                <span className="text-sm font-bold text-gray-900">
                  {totalWealth > 0 ? ((balance / totalWealth) * 100).toFixed(1) : 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${totalWealth > 0 ? (balance / totalWealth) * 100 : 0}%` }}
                ></div>
              </div>
            </div>

            {/* Investment Bar */}
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Investments</span>
                <span className="text-sm font-bold text-gray-900">
                  {totalWealth > 0 ? ((invested / totalWealth) * 100).toFixed(1) : 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${totalWealth > 0 ? (invested / totalWealth) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BalancePage;




