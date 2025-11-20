import React from 'react';
import { ArrowUpRight, ArrowDownLeft, TrendingUp, Clock } from 'lucide-react';

const TransactionList = ({ transactions }) => {
  if (!transactions || transactions.length === 0) {
    return (
      <div className="bg-white rounded-3xl shadow-xl p-6 text-center">
        <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">No transactions yet</p>
      </div>
    );
  }

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'credit':
        return <ArrowDownLeft className="w-5 h-5" />;
      case 'debit':
        return <ArrowUpRight className="w-5 h-5" />;
      case 'investment':
        return <TrendingUp className="w-5 h-5" />;
      default:
        return <Clock className="w-5 h-5" />;
    }
  };

  const getTransactionColor = (type) => {
    switch (type) {
      case 'credit':
        return 'bg-green-100 text-green-600';
      case 'debit':
        return 'bg-red-100 text-red-600';
      case 'investment':
        return 'bg-purple-100 text-purple-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-3xl shadow-xl p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Transactions</h3>
      
      <div className="space-y-3">
        {transactions.slice(0, 10).map((transaction) => (
          <div
            key={transaction.id}
            className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition"
          >
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-full ${getTransactionColor(transaction.type)}`}>
                {getTransactionIcon(transaction.type)}
              </div>
              <div>
                <p className="font-medium text-gray-900">{transaction.description}</p>
                <p className="text-xs text-gray-500">{transaction.date}</p>
              </div>
            </div>
            
            <div className="text-right">
              <p
                className={`font-bold ${
                  transaction.type === 'credit'
                    ? 'text-green-600'
                    : transaction.type === 'debit'
                    ? 'text-red-600'
                    : 'text-purple-600'
                }`}
              >
                {transaction.type === 'credit' ? '+' : '-'}₹{transaction.amount.toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TransactionList;

