import React from 'react';
import { CheckCircle, XCircle, Info, AlertCircle } from 'lucide-react';

const Toast = ({ message, type = 'info' }) => {
  const icons = {
    success: <CheckCircle className="w-5 h-5" />,
    error: <XCircle className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
    info: <Info className="w-5 h-5" />
  };

  const colors = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-blue-500 text-white'
  };

  return (
    <div className="fixed top-4 right-4 z-50 animate-slide-in-up">
      <div className={`${colors[type]} rounded-xl shadow-lg p-4 flex items-center gap-3 min-w-[300px]`}>
        {icons[type]}
        <p className="font-medium">{message}</p>
      </div>
    </div>
  );
};

export default Toast;

