import React, { useEffect } from 'react';
import { CheckCircle } from 'lucide-react';

const PaymentSuccessModal = ({ payment, onClose }) => {
  useEffect(() => {
    // Auto-close after 2 seconds
    const timer = setTimeout(() => {
      onClose();
    }, 2000);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-sm w-full p-6 animate-slide-in-up">
        {/* Success Icon */}
        <div className="flex flex-col items-center mb-6">
          <div className="bg-green-100 p-4 rounded-full mb-4 animate-pulse">
            <CheckCircle className="w-16 h-16 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            Payment Successful!
          </h3>
          <p className="text-gray-600 text-center">
            Your payment has been processed
          </p>
        </div>

        {/* Payment Details */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-100">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm text-gray-600">Amount Paid</span>
            <span className="text-2xl font-bold text-green-600">
              ₹{payment?.amount?.toLocaleString()}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Paid to</span>
            <span className="text-lg font-semibold text-gray-900 capitalize">
              {payment?.recipient}
            </span>
          </div>
        </div>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="w-full mt-6 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold py-3 rounded-xl hover:from-green-700 hover:to-emerald-700 transition"
        >
          Done
        </button>
      </div>
    </div>
  );
};

export default PaymentSuccessModal;

