import React from 'react';
import { Search, Bell, Heart, Menu } from 'lucide-react';

const PaytmHeader = ({ user, onMenuClick }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left: User Avatar (Clickable to toggle sidebar) */}
          <button
            onClick={onMenuClick}
            className="flex items-center gap-3 hover:bg-gray-50 rounded-2xl p-2 -ml-2 transition group"
          >
            {/* User Avatar */}
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-md group-hover:shadow-lg group-hover:scale-105 transition">
              {getInitials(user?.name)}
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm text-gray-500">Welcome back</p>
              <p className="font-semibold text-gray-900">{user?.name || 'User'}</p>
            </div>
          </button>

          {/* Center: Logo */}
          <div className="flex items-center gap-2">
            <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Paytm
            </span>
            <Heart className="w-5 h-5 text-red-500 fill-red-500" />
            <span className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI
            </span>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            <button className="p-2 hover:bg-gray-100 rounded-full transition">
              <Search className="w-6 h-6 text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-full transition relative">
              <Bell className="w-6 h-6 text-gray-600" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaytmHeader;

