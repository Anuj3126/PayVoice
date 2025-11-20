// ElevenLabs TTS Service
const ELEVENLABS_API_KEY = import.meta.env.VITE_ELEVENLABS_API_KEY;
const ELEVENLABS_API_URL = 'https://api.elevenlabs.io/v1';

// Voice IDs (you can change these)
const VOICE_IDS = {
  en: 'EXAVITQu4vr4xnSDxMaL', // Sarah - English
  hi: 'jsCqWAovK2LkecY7zXl4', // Monika Sogam - Hindi Modulated
};

/**
 * Convert text to speech using ElevenLabs API
 * @param {string} text - Text to convert
 * @param {string} language - Language code ('en' or 'hi')
 * @returns {Promise<void>}
 */
export async function speakWithElevenLabs(text, language = 'en') {
  if (!ELEVENLABS_API_KEY) {
    console.warn('ElevenLabs API key not configured. Falling back to browser TTS.');
    // Fallback to browser's speech synthesis
    return speakWithBrowserTTS(text, language);
  }

  try {
    const voiceId = VOICE_IDS[language] || VOICE_IDS.en;
    
    const response = await fetch(
      `${ELEVENLABS_API_URL}/text-to-speech/${voiceId}`,
      {
        method: 'POST',
        headers: {
          'Accept': 'audio/mpeg',
          'Content-Type': 'application/json',
          'xi-api-key': ELEVENLABS_API_KEY,
        },
        body: JSON.stringify({
          text: text,
          model_id: 'eleven_multilingual_v2',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75,
            style: 0.5,
            use_speaker_boost: true,
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`ElevenLabs API error: ${response.status}`);
    }

    // Get audio blob
    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    
    // Play audio
    const audio = new Audio(audioUrl);
    
    return new Promise((resolve, reject) => {
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        resolve();
      };
      audio.onerror = (error) => {
        URL.revokeObjectURL(audioUrl);
        reject(error);
      };
      audio.play();
    });
  } catch (error) {
    console.error('ElevenLabs TTS error, falling back to browser TTS:', error);
    // Fallback to browser's speech synthesis
    return speakWithBrowserTTS(text, language);
  }
}

/**
 * Fallback to browser's built-in speech synthesis
 * @param {string} text - Text to speak
 * @param {string} language - Language code
 */
function speakWithBrowserTTS(text, language = 'en') {
  return new Promise((resolve, reject) => {
    if (!('speechSynthesis' in window)) {
      reject(new Error('Speech synthesis not supported'));
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'hi' ? 'hi-IN' : 'en-US';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onend = () => resolve();
    utterance.onerror = (error) => reject(error);

    window.speechSynthesis.speak(utterance);
  });
}

/**
 * Stop any currently playing speech
 */
export function stopSpeaking() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

/**
 * Get available voices from ElevenLabs
 * @returns {Promise<Array>}
 */
export async function getAvailableVoices() {
  if (!ELEVENLABS_API_KEY) {
    return [];
  }

  try {
    const response = await fetch(`${ELEVENLABS_API_URL}/voices`, {
      headers: {
        'xi-api-key': ELEVENLABS_API_KEY,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch voices');
    }

    const data = await response.json();
    return data.voices;
  } catch (error) {
    console.error('Error fetching voices:', error);
    return [];
  }
}

