import React from 'react';
import { History, LogOut, QrCode, X } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';

const Sidebar = ({ user, onNavigate, onLogout, isOpen, onClose }) => {
  const upiId = user?.phone_number ? `${user.phone_number}@payvoice` : 'user@payvoice';

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        ></div>
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed lg:sticky top-0 left-0 h-screen z-50
        w-80 bg-gradient-to-b from-blue-600 to-indigo-700 text-white flex flex-col
        transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
      {/* Close button for mobile */}
      <button
        onClick={onClose}
        className="lg:hidden absolute top-4 right-4 p-2 hover:bg-white/10 rounded-full transition"
      >
        <X className="w-6 h-6" />
      </button>

      {/* QR Code Section */}
      <div className="p-6 flex flex-col items-center">
        <div className="bg-white p-4 rounded-2xl shadow-lg mb-4">
          <QRCodeSVG 
            value={upiId}
            size={180}
            level="H"
            includeMargin={true}
          />
        </div>
        
        {/* User Info */}
        <div className="text-center mb-2">
          <h3 className="text-xl font-bold mb-1">{user?.name || 'User'}</h3>
          <p className="text-blue-100 text-sm mb-1">{user?.email || 'email@example.com'}</p>
          <div className="inline-flex items-center gap-1 bg-white/20 backdrop-blur px-3 py-1 rounded-full text-xs">
            <QrCode className="w-3 h-3" />
            <span className="font-mono">{upiId}</span>
          </div>
        </div>

        {/* Balance Badge */}
        <div className="mt-4 bg-white/10 backdrop-blur-sm px-6 py-3 rounded-xl border border-white/20">
          <p className="text-xs text-blue-100 mb-1">Available Balance</p>
          <p className="text-2xl font-bold">₹{user?.balance?.toLocaleString('en-IN') || '0'}</p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 px-4">
        <button
          onClick={() => onNavigate('history')}
          className="w-full flex items-center gap-3 px-4 py-3 mb-2 rounded-xl hover:bg-white/10 transition group"
        >
          <div className="bg-white/20 p-2 rounded-lg group-hover:bg-white/30 transition">
            <History className="w-5 h-5" />
          </div>
          <span className="font-medium">Transaction History</span>
        </button>
      </div>

      {/* Logout Button */}
      <div className="p-4">
        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-500 hover:bg-red-600 rounded-xl transition shadow-lg"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-semibold">Logout</span>
        </button>
      </div>
      </div>
    </>
  );
};

export default Sidebar;

