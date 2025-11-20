# 🚀 Quick Start Guide - VoicePay v2

Get up and running in 5 minutes!

## ⚡ Prerequisites Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
- [ ] ElevenLabs API key (Optional - [Get it here](https://elevenlabs.io))

## 📦 Step-by-Step Setup

### 1️⃣ Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Gemini API key
echo "GEMINI_API_KEY=your_actual_gemini_key_here" > .env

# Start the backend
python main.py
```

✅ Backend should be running on `http://localhost:8000`

### 2️⃣ Frontend Setup (2 minutes)

Open a **NEW terminal window**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file (optional - for ElevenLabs TTS)
echo "VITE_ELEVENLABS_API_KEY=your_elevenlabs_key_here" > .env

# Start the frontend
npm run dev
```

✅ Frontend should be running on `http://localhost:3000`

### 3️⃣ Test It Out (1 minute)

1. Open your browser to `http://localhost:3000`
2. Allow microphone permissions when prompted
3. Click the microphone button
4. Say: **"What's my balance?"**
5. 🎉 You should hear a voice response!

## 🎤 Try These Commands

- "Pay 500 rupees to Rahul"
- "Show my transactions"
- "Check my investments"
- "Send 1000 to Priya"

## 💡 Tips

- **Default PIN**: `1234` for all demo users
- **Switch Users**: Use the dropdown in the top-right
- **No ElevenLabs Key?**: App will use browser's built-in TTS
- **Stuck?**: Check the [Troubleshooting](README.md#-troubleshooting) section

## ⚠️ Common Issues

### "GEMINI_API_KEY is required"
```bash
# Make sure your .env file exists in backend/
cat backend/.env
# Should show: GEMINI_API_KEY=your_key...
```

### "Voice not working"
- Try Chrome or Edge (best support)
- Check microphone permissions
- Click the mic button and speak clearly

### "Backend connection failed"
- Make sure backend is running on port 8000
- Check terminal for error messages
- Try restarting the backend

## 📞 Still Need Help?

1. Check the full [README.md](README.md)
2. Look at error messages in browser console (F12)
3. Ensure both terminals are running (backend + frontend)

---

**Happy Voice Paying! 🎙️💰**

