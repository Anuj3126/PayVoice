import React from 'react';
import { Mic, Wallet } from 'lucide-react';

const MainActionCards = ({ onPayClick, onBalanceClick }) => {
  return (
    <div className="flex justify-evenly items-center mb-6 px-4">
      {/* Pay Button with Label */}
      <div className="flex flex-col items-center gap-2">
        <button
          onClick={onPayClick}
          className="group relative bg-white rounded-full w-24 h-24 flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110"
        >
          <Mic className="w-10 h-10 text-blue-600 group-hover:text-blue-700 transition-colors" />
        </button>
        <span className="text-sm font-medium text-gray-700">Pay</span>
      </div>

      {/* Balance Button with Label */}
      <div className="flex flex-col items-center gap-2">
        <button
          onClick={onBalanceClick}
          className="group relative bg-white rounded-full w-24 h-24 flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110"
        >
          <Wallet className="w-10 h-10 text-blue-600 group-hover:text-blue-700 transition-colors" />
        </button>
        <span className="text-sm font-medium text-gray-700">Balance</span>
      </div>
    </div>
  );
};

export default MainActionCards;

