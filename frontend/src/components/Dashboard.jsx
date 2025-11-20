import React from 'react';
import { Wallet, TrendingUp, ArrowUpRight } from 'lucide-react';

const Dashboard = ({ userData }) => {
  if (!userData) return null;

  // Safe defaults for investments
  const investments = userData.investments || { gold: 0, total: 0 };
  const goldInvestments = investments.gold || 0;
  const totalInvestments = investments.total || 0;

  const recentTransactions = userData.transactions?.slice(0, 3) || [];
  const totalSpent = recentTransactions
    .filter(t => t.type === 'debit')
    .reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="bg-white rounded-3xl shadow-xl p-6 mb-4">
      {/* Balance Card */}
      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm opacity-80 mb-1">Available Balance</p>
            <h2 className="text-4xl font-bold">₹{userData.balance.toLocaleString()}</h2>
          </div>
          <Wallet className="w-12 h-12 opacity-50" />
        </div>
        
        <div className="flex gap-4 pt-4 border-t border-white/20">
          <div className="flex-1">
            <p className="text-xs opacity-80 mb-1">This Month</p>
            <p className="text-lg font-semibold">₹{totalSpent.toLocaleString()}</p>
          </div>
          <div className="flex-1">
            <p className="text-xs opacity-80 mb-1">Investments</p>
            <p className="text-lg font-semibold">₹{totalInvestments.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-100">
          <div className="flex items-center gap-2 mb-2">
            <div className="bg-green-500 p-2 rounded-lg">
              <TrendingUp className="w-4 h-4 text-white" />
            </div>
            <span className="text-xs text-gray-600">Gold Investments</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            ₹{goldInvestments.toLocaleString()}
          </p>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
          <div className="flex items-center gap-2 mb-2">
            <div className="bg-blue-500 p-2 rounded-lg">
              <ArrowUpRight className="w-4 h-4 text-white" />
            </div>
            <span className="text-xs text-gray-600">Transactions</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {userData.transactions?.length || 0}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

