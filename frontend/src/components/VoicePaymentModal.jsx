import React, { useState } from 'react';
import { X } from 'lucide-react';
import VoiceOrb from './VoiceOrb';
import VoiceInterface from './VoiceInterface';

const VoicePaymentModal = ({ onClose, onVoiceResponse }) => {
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Voice Payment</h2>
            <p className="text-sm text-gray-500">Speak naturally to make payments</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Voice Interface */}
        <div className="p-6">
          <VoiceInterface onResponse={onVoiceResponse} />
        </div>
      </div>
    </div>
  );
};

export default VoicePaymentModal;




