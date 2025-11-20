import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import { processVoiceCommand } from '../services/api';

const VoiceInterface = ({ onResponse, userId }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [textInput, setTextInput] = useState('');
  const [showTextInput, setShowTextInput] = useState(false);
  
  // Store both English and Hindi voices
  const selectedVoiceRef = useRef({ en: null, hi: null });

  // Initialize voices on component mount
  useEffect(() => {
    const initVoice = () => {
      const synth = window.speechSynthesis;
      const voices = synth.getVoices();
      
      if (voices.length > 0) {
        // Select a consistent male English voice
        const maleVoice = voices.find(voice => 
          voice.lang.startsWith('en-') && 
          (voice.name.includes('Male') || 
           voice.name.includes('Google UK English Male') ||
           voice.name.includes('Alex') ||
           voice.name.includes('Daniel'))
        ) || voices.find(voice => 
          voice.lang.startsWith('en-') && !voice.name.includes('Female')
        ) || voices[0];
        
        // Select a Hindi voice
        const hindiVoice = voices.find(voice => 
          voice.lang.startsWith('hi-') || 
          voice.lang === 'hi' ||
          voice.name.includes('Hindi') ||
          voice.name.includes('Lekha') // Google's Hindi voice
        ) || voices.find(voice => 
          voice.lang.startsWith('hi')
        );
        
        selectedVoiceRef.current = { en: maleVoice, hi: hindiVoice };
        console.log('🔊 Selected English voice:', maleVoice?.name);
        console.log('🔊 Selected Hindi voice:', hindiVoice?.name || 'None available');
        
        if (!hindiVoice) {
          console.warn('⚠️ No Hindi voice found. Hindi text may not be spoken correctly.');
        }
      }
    };

    // Voices load asynchronously
    if (window.speechSynthesis.getVoices().length > 0) {
      initVoice();
    } else {
      window.speechSynthesis.onvoiceschanged = initVoice;
    }
  }, []);

  const toggleListening = async () => {
    if (isListening) {
      // Stop recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
      setIsListening(false);
    } else {
      // Start recording
      try {
        setTranscript('');
        audioChunksRef.current = [];
        
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          // Stop all tracks
          stream.getTracks().forEach(track => track.stop());
          
          // Create audio blob
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          
          // Send to backend for transcription
          await transcribeAudio(audioBlob);
        };

        mediaRecorder.start();
        setIsListening(true);
        console.log('🎤 Recording started (using Whisper)...');
      } catch (error) {
        console.error('Error accessing microphone:', error);
        setCommandHistory(prev => [...prev, { 
          text: 'Could not access microphone. Please check permissions or use text input.', 
          type: 'error', 
          timestamp: new Date() 
        }]);
        setShowTextInput(true);
      }
    }
  };

  const transcribeAudio = async (audioBlob) => {
    try {
      console.log('📤 Sending audio to Groq Whisper API (FREE!)...');
      setTranscript('Transcribing...');
      
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      const response = await fetch('http://localhost:8000/api/transcribe', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Transcription failed: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Groq Whisper transcribed:', data.text);
      console.log('🌍 Whisper detected language:', data.language);
      
      // Fix common transcription errors for names and numbers
      let correctedText = data.text;
      const nameCorrections = {
        // Names
        'nudj': 'Anuj',
        'anuj': 'Anuj',
        'grazie': 'Rahul',
        'grazi': 'Rahul',
        
        // Common words
        'rúpeas': 'rupees',
        'rupaye': 'rupees',
        'rupay': 'rupees',
        'það': 'to',
        'að': 'to',
        
        // Numbers in Hindi
        'sau': '100',
        'so': '100',
        'pachas': '50',
        'das': '10',
        'bees': '20',
        'pachees': '25',
        'paanch': '5'
      };
      
      // Apply corrections (case-insensitive)
      Object.entries(nameCorrections).forEach(([wrong, correct]) => {
        const regex = new RegExp(`\\b${wrong}\\b`, 'gi');
        correctedText = correctedText.replace(regex, correct);
      });
      
      if (correctedText !== data.text) {
        console.log('🔧 Corrected:', data.text, '→', correctedText);
      }
      
      setTranscript(correctedText);
      
      // Use Whisper's detected language, fallback to frontend detection
      let detectedLanguage = 'en';
      if (data.language && (data.language === 'hi' || data.language.startsWith('hi'))) {
        detectedLanguage = 'hi';
        console.log('✅ Using Hindi from Whisper detection');
      } else {
        // Fallback to frontend detection
        detectedLanguage = detectLanguage(correctedText);
        console.log('🔍 Using frontend language detection:', detectedLanguage);
      }
      
      handleVoiceCommand(correctedText.trim(), detectedLanguage);
      
    } catch (error) {
      console.error('❌ Transcription error:', error);
      setCommandHistory(prev => [...prev, { 
        text: 'Failed to transcribe audio. Please try again or use text input.', 
        type: 'error', 
        timestamp: new Date() 
      }]);
      setTranscript('');
      setShowTextInput(true);
    }
  };

  const detectLanguage = (text) => {
    // Detect language from transcribed text
    const hindiRegex = /[\u0900-\u097F]/; // Devanagari script
    
    // Check for Devanagari characters
    if (hindiRegex.test(text)) {
      return 'hi';
    }
    
    // Check for distinctive Hindi/Hinglish words (not used in English)
    // Exclude ambiguous words like "rupees" which can be used in English too
    const strongHindiWords = ['ko', 'ka', 'ki', 'ke', 'hai', 'hain', 'bhejo', 'bhej', 'kitna', 'kya', 'mera', 'tera', 'uska', 'karo', 'kaise', 'kyun', 'meri', 'aap', 'aapka', 'sakti', 'sakta', 'kya', 'kyun', 'kaise', 'rupaye', 'rupaye', 'sau', 'pachas', 'bees', 'pachees', 'paanch', 'das'];
    const lowerText = text.toLowerCase();
    
    // Count how many Hindi words are present (more flexible matching)
    const hindiWordCount = strongHindiWords.filter(word => {
      // Check for word boundaries or as part of words
      const regex = new RegExp(`\\b${word}\\b`, 'i');
      return regex.test(lowerText);
    }).length;
    
    // Need at least 1 strong Hindi word to classify as Hindi
    // This prevents "Send ten rupees to Neeraj" from being detected as Hindi
    if (hindiWordCount >= 1) {
      console.log(`🔍 Detected ${hindiWordCount} Hindi words, classifying as Hindi`);
      return 'hi'; // Hinglish/Hindi
    }
    
    return 'en'; // Default to English
  };

  const startListening = () => {
    if (!isListening && !showTextInput) {
      toggleListening();
      console.log('🎤 Auto-started voice listening');
    }
  };

  const handleVoiceCommand = async (text, detectedLang = null) => {
    setCommandHistory(prev => [...prev, { text, type: 'user', timestamp: new Date() }]);

    try {
      // Use provided language or detect from text
      const language = detectedLang || detectLanguage(text);
      console.log('🌐 Final language for API:', language);
      
      const response = await processVoiceCommand(text, userId, language);
      
      setCommandHistory(prev => [
        ...prev,
        { text: response.message, type: 'assistant', timestamp: new Date() }
      ]);

      // Speak the response
      await speak(response.message);

      // Auto-enable voice input for phone number prompts
      const message = response.message.toLowerCase();
      const needsVoiceInput = 
        message.includes('phone number') ||
        message.includes('say the') ||
        message.includes('tell me') ||
        message.includes('please tell') ||
        message.includes('10-digit') ||
        message.includes('is this correct') ||
        message.includes('say yes or no') ||
        message.includes('would you like to add') ||
        message.endsWith('?');  // Any question triggers voice input
      
      if (needsVoiceInput) {
        console.log('🎤 Prompt detected, auto-enabling voice input');
        // Wait a bit for TTS to finish, then auto-start listening
        setTimeout(() => {
          startListening();
        }, 500);
      }

      // Notify parent component
      if (onResponse) {
        onResponse(response);
      }
    } catch (error) {
      const errorMsg = 'Sorry, I encountered an error. Please try again.';
      setCommandHistory(prev => [
        ...prev,
        { text: errorMsg, type: 'error', timestamp: new Date() }
      ]);
      await speak(errorMsg);
    }
  };

  const speak = async (text) => {
    return new Promise((resolve) => {
      try {
        setIsSpeaking(true);
        
        // Use browser's built-in Text-to-Speech (Groq doesn't have TTS API)
        const synth = window.speechSynthesis;
        
        // Cancel any ongoing speech first
        synth.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Configure voice settings
        utterance.rate = 1.0;  // Normal speed
        utterance.pitch = 1.0;  // Normal pitch
        utterance.volume = 1.0;  // Full volume
        
        // Detect if text is Hindi (contains Devanagari characters)
        const isHindi = /[\u0900-\u097F]/.test(text);
        
        // Use the appropriate voice based on language
        if (isHindi && selectedVoiceRef.current.hi) {
          utterance.voice = selectedVoiceRef.current.hi;
          utterance.lang = 'hi-IN';
          console.log('🔊 Using Hindi voice:', selectedVoiceRef.current.hi.name);
        } else if (selectedVoiceRef.current.en) {
          utterance.voice = selectedVoiceRef.current.en;
          utterance.lang = 'en-US';
          console.log('🔊 Using English voice:', selectedVoiceRef.current.en.name);
        }
        
        // Handle completion
        utterance.onend = () => {
          setIsSpeaking(false);
          resolve();
        };
        
        utterance.onerror = (error) => {
          console.error('Speech synthesis error:', error);
          setIsSpeaking(false);
          resolve();
        };
        
        // Speak!
        synth.speak(utterance);
        
      } catch (error) {
        console.error('TTS error:', error);
        setIsSpeaking(false);
        resolve();
      }
    });
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (textInput.trim()) {
      handleVoiceCommand(textInput.trim());
      setTextInput('');
    }
  };

  return (
    <div className="bg-white rounded-b-3xl shadow-2xl p-6 mb-4">
      {/* Toggle between voice and text */}
      <div className="flex justify-end mb-2">
        <button
          onClick={() => setShowTextInput(!showTextInput)}
          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
        >
          {showTextInput ? '🎤 Switch to Voice' : '⌨️ Switch to Text'}
        </button>
      </div>

      {/* Text Input (fallback for network issues) */}
      {showTextInput ? (
        <form onSubmit={handleTextSubmit} className="mb-6">
          <div className="flex gap-2">
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Type your command (e.g., 'Pay 200 to 9108012345')"
              className="flex-1 px-4 py-3 border-2 border-indigo-200 rounded-xl focus:outline-none focus:border-indigo-500 transition"
              disabled={isSpeaking}
            />
            <button
              type="submit"
              disabled={!textInput.trim() || isSpeaking}
              className="px-6 py-3 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Send
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            💡 Examples: "Pay 200 to Anuj", "What's my balance", "Pay 200 to 9108012345"
          </p>
        </form>
      ) : (
        <>
          {/* Microphone Button */}
          <div className="flex flex-col items-center mb-6">
        <button
          onClick={toggleListening}
          disabled={isSpeaking}
          className={`relative w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${
            isListening
              ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/50'
              : 'bg-gradient-to-br from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 shadow-lg'
          } ${isSpeaking ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isListening ? (
            <MicOff className="w-10 h-10 text-white" />
          ) : (
            <Mic className="w-10 h-10 text-white" />
          )}
          
          {isListening && (
            <>
              <span className="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-75"></span>
            </>
          )}
        </button>

        <div className="mt-4 text-center">
          <p className="text-sm font-medium text-gray-700">
            {isListening ? 'Recording... (Tap to stop)' : 'Tap to speak'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {isListening ? 'Using Groq Whisper 🎯 (FREE!)' : ''}
          </p>
          {isSpeaking && (
            <div className="flex items-center justify-center gap-2 mt-2 text-purple-600">
              <Volume2 className="w-4 h-4 animate-pulse" />
              <span className="text-xs">Speaking...</span>
            </div>
          )}
        </div>
      </div>
        </>
      )}

      {/* Live Transcript */}
      {transcript && (
        <div className="bg-gray-50 rounded-xl p-4 mb-4">
          <p className="text-sm text-gray-600 mb-1">You said:</p>
          <p className="text-gray-900 font-medium">{transcript}</p>
        </div>
      )}

      {/* Command History */}
      {commandHistory.length > 0 && (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Recent Commands</p>
          {commandHistory.slice(-10).reverse().map((cmd, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg ${
                cmd.type === 'user'
                  ? 'bg-indigo-50 border-l-4 border-indigo-500'
                  : cmd.type === 'error'
                  ? 'bg-red-50 border-l-4 border-red-500'
                  : 'bg-purple-50 border-l-4 border-purple-500'
              }`}
            >
              <p className="text-xs font-semibold text-gray-600 mb-1">
                {cmd.type === 'user' ? 'You' : cmd.type === 'error' ? 'Error' : 'Assistant'}
              </p>
              <p className="text-sm text-gray-800">{cmd.text}</p>
            </div>
          ))}
        </div>
      )}

      {/* Quick Commands */}
      <div className="mt-6 border-t pt-4">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Quick Commands</p>
        <div className="flex flex-wrap gap-2">
          {[
            "What's my balance?",
            "Pay 500 to Rahul",
            "Show transactions"
          ].map((cmd, idx) => (
            <button
              key={idx}
              onClick={() => handleVoiceCommand(cmd)}
              disabled={isSpeaking || isListening}
              className="px-3 py-1.5 text-xs bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 rounded-full hover:from-indigo-200 hover:to-purple-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {cmd}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default VoiceInterface;
