import React from 'react';
import { Mic, MicOff } from 'lucide-react';

const VoiceOrb = ({ isListening, isProcessing }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12">
      {/* Orb Container */}
      <div className="relative">
        {/* Outer glow rings */}
        {isListening && (
          <>
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-3xl opacity-30 animate-pulse"></div>
            <div className="absolute -inset-4 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full blur-2xl opacity-20 animate-ping"></div>
          </>
        )}
        
        {/* Main Orb */}
        <div className={`relative w-48 h-48 rounded-full flex items-center justify-center transition-all duration-300 ${
          isListening 
            ? 'bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 shadow-2xl scale-110' 
            : 'bg-gradient-to-br from-gray-300 to-gray-400 shadow-lg'
        }`}>
          {/* Inner glow */}
          <div className={`absolute inset-2 rounded-full ${
            isListening 
              ? 'bg-gradient-to-br from-blue-400/50 to-purple-400/50 blur-xl animate-pulse' 
              : ''
          }`}></div>
          
          {/* Icon */}
          <div className="relative z-10">
            {isListening ? (
              <Mic className="w-20 h-20 text-white animate-pulse" />
            ) : (
              <MicOff className="w-20 h-20 text-white/80" />
            )}
          </div>
          
          {/* Ripple effect when listening */}
          {isListening && (
            <>
              <div className="absolute inset-0 rounded-full border-4 border-white/30 animate-ping"></div>
              <div className="absolute inset-0 rounded-full border-2 border-white/20 animate-pulse"></div>
            </>
          )}
        </div>
        
        {/* Floating particles */}
        {isListening && (
          <div className="absolute inset-0">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="absolute w-2 h-2 bg-white rounded-full animate-float"
                style={{
                  left: `${50 + 40 * Math.cos((i * 60 * Math.PI) / 180)}%`,
                  top: `${50 + 40 * Math.sin((i * 60 * Math.PI) / 180)}%`,
                  animationDelay: `${i * 0.2}s`,
                }}
              ></div>
            ))}
          </div>
        )}
      </div>
      
      {/* Status Text */}
      <div className="mt-8 text-center">
        <p className="text-2xl font-bold text-gray-800 mb-2">
          {isListening ? 'Listening...' : isProcessing ? 'Processing...' : 'Tap to Speak'}
        </p>
        <p className="text-gray-500">
          {isListening ? 'Say your command' : isProcessing ? 'Please wait' : 'Voice payment assistant'}
        </p>
      </div>
    </div>
  );
};

export default VoiceOrb;




