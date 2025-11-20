import React from 'react';
import { ArrowLeft, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, Calendar } from 'lucide-react';

const TransactionHistoryPage = ({ userData, onBack }) => {
  const transactions = userData?.transactions || [];
  
  // Calculate totals
  const totalSent = transactions
    .filter(t => t.type === 'debit' || t.type === 'payment')
    .reduce((sum, t) => sum + t.amount, 0);
  
  const totalReceived = transactions
    .filter(t => t.type === 'credit' || t.type === 'received')
    .reduce((sum, t) => sum + t.amount, 0);
  
  const totalInvested = transactions
    .filter(t => t.type === 'investment')
    .reduce((sum, t) => sum + t.amount, 0);

  const getTransactionIcon = (type) => {
    switch(type) {
      case 'debit':
      case 'payment':
        return <ArrowUpRight className="w-5 h-5" />;
      case 'credit':
      case 'received':
        return <ArrowDownRight className="w-5 h-5" />;
      case 'investment':
        return <TrendingUp className="w-5 h-5" />;
      default:
        return <Calendar className="w-5 h-5" />;
    }
  };

  const getTransactionColor = (type) => {
    switch(type) {
      case 'debit':
      case 'payment':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'credit':
      case 'received':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'investment':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 mb-6 hover:bg-white/10 px-4 py-2 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back</span>
        </button>
        
        <h1 className="text-3xl font-bold mb-2">Transaction History</h1>
        <p className="text-blue-100">Complete overview of your transactions</p>
      </div>

      {/* Summary Cards */}
      <div className="max-w-6xl mx-auto px-8 -mt-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-red-100 p-2 rounded-lg">
                <ArrowUpRight className="w-5 h-5 text-red-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Total Sent</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">₹{totalSent.toLocaleString('en-IN')}</p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-green-100 p-2 rounded-lg">
                <ArrowDownRight className="w-5 h-5 text-green-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Total Received</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">₹{totalReceived.toLocaleString('en-IN')}</p>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-lg">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-blue-100 p-2 rounded-lg">
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <span className="text-sm font-medium text-gray-600">Total Invested</span>
            </div>
            <p className="text-3xl font-bold text-gray-900">₹{totalInvested.toLocaleString('en-IN')}</p>
          </div>
        </div>

        {/* Transactions List */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">All Transactions</h2>
          
          {transactions.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No transactions yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {transactions.map((transaction, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 rounded-xl border-2 hover:shadow-md transition"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl border-2 ${getTransactionColor(transaction.type)}`}>
                      {getTransactionIcon(transaction.type)}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{transaction.description}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(transaction.timestamp).toLocaleString('en-IN', {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <p className={`text-lg font-bold ${
                      (transaction.type === 'credit' || transaction.type === 'received') ? 'text-green-600' : 'text-gray-900'
                    }`}>
                      {(transaction.type === 'credit' || transaction.type === 'received') ? '+' : '-'}₹{transaction.amount.toLocaleString('en-IN')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TransactionHistoryPage;

