# 🎙️ VoicePay v2

**AI-Powered Voice Payment System** built with Gemini AI, FastAPI, React, and ElevenLabs TTS

VoicePay is a voice-first payment demo application that lets you make payments, check balances, and manage investments using natural voice commands.

![Tech Stack](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Gemini AI](https://img.shields.io/badge/Gemini-2.0--flash-orange)
![Python](https://img.shields.io/badge/Python-3.8+-blue)

## ✨ Features

- 🎤 **Voice Commands** - Natural speech recognition with browser STT
- 🤖 **Gemini AI** - Intelligent intent detection with function calling
- 🎙️ **Premium TTS** - Professional voice responses via ElevenLabs (with browser fallback)
- 💰 **UPI-like Payments** - Voice-driven instant transfers
- 🔐 **PIN Security** - 4-digit PIN authentication for payments
- 📊 **Real-time Dashboard** - Live balance and transaction tracking
- 💎 **Smart Investments** - AI-powered investment nudges with real market data
- 📈 **yfinance Integration** - Real-time market prices for investments
- 💾 **SQLite Database** - Persistent data storage
- 🎯 **Investment Analysis** - Monthly spending insights and recommendations

## 🎤 Voice Commands Examples

Try these commands:

- "What's my balance?"
- "Pay 500 rupees to Rahul"
- "Send 1000 to Priya"
- "Show my transactions"
- "Check my investments"
- "Show my spending"

## 🏗️ Architecture

```
Voice Input (Browser STT)
    ↓
Gemini AI (Agent-based Intent Detection)
    ↓
FastAPI Backend (Business Logic)
    ↓  
SQLite Database (Persistent Storage)
    ↓
ElevenLabs TTS (Voice Output)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Gemini API key (Required)
- ElevenLabs API key (Optional - will fallback to browser TTS)

### Installation

**1. Clone and setup backend:**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env
```

**2. Setup frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_ELEVENLABS_API_KEY=your_key_here" > .env
echo "VITE_API_BASE_URL=http://localhost:8000" >> .env
```

### Running the Application

**Terminal 1 - Backend:**

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

The backend will start on `http://localhost:8000`

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

**3. Open your browser:**

Navigate to `http://localhost:3000`

## 🔑 Get API Keys

### Gemini API (Required)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to `backend/.env`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### ElevenLabs API (Optional)

1. Go to [ElevenLabs](https://elevenlabs.io/app/settings/api-keys)
2. Sign up for a free account (10,000 characters/month)
3. Generate an API key
4. Add it to `frontend/.env`:

```
VITE_ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

**Note:** If you don't provide an ElevenLabs API key, the app will automatically fallback to your browser's built-in text-to-speech.

## 📁 Project Structure

```
payvoice-v2/
├── backend/
│   ├── main.py                    # FastAPI app with Gemini AI agent
│   ├── database.py                # SQLite database operations
│   ├── investment_analyzer.py     # yfinance market data & analysis
│   ├── investment_portfolio.py    # Portfolio tracking with real prices
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables (create this)
│   └── voicepay.db               # SQLite database (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── VoiceInterface.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TransactionList.jsx
│   │   │   ├── PinModal.jsx
│   │   │   ├── InvestmentNudge.jsx
│   │   │   ├── PaymentSuccessModal.jsx
│   │   │   ├── MonthlyInvestmentAnalysis.jsx
│   │   │   └── Toast.jsx
│   │   ├── services/
│   │   │   ├── api.js            # API client
│   │   │   └── elevenlabs.js     # TTS service
│   │   ├── App.jsx               # Main app component
│   │   ├── main.jsx              # Entry point
│   │   └── index.css             # Global styles
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env                      # Environment variables (create this)
│
└── README.md
```

## 🎯 How It Works

### Agent-Based Architecture

The application uses an agent-based pattern with Gemini AI:

1. **Voice Input**: User speaks into microphone
2. **Speech-to-Text**: Browser's Web Speech API converts to text
3. **AI Agent**: Gemini AI analyzes intent and calls appropriate function:
   - `get_transaction_history` - For spending queries
   - `process_payment_intent` - For money transfers
   - `check_balance` - For balance queries
   - `query_investments` - For investment portfolio
4. **Backend Processing**: FastAPI executes the requested operation
5. **Text-to-Speech**: ElevenLabs converts response to speech
6. **User Hears**: Natural voice response

### Key Technologies

**Backend:**
- FastAPI - High-performance async web framework
- Gemini AI 2.0 Flash - Function calling for intent detection
- SQLite - Lightweight database
- yfinance - Real-time market data
- Pydantic - Data validation

**Frontend:**
- React 18 - Modern UI library
- Vite - Ultra-fast build tool
- TailwindCSS - Utility-first styling
- Web Speech API - Browser STT
- ElevenLabs - Premium TTS
- Axios - HTTP client

## 💾 Database Schema

### Users Table
```sql
id, name, balance, pin, created_at
```

### Transactions Table
```sql
id, user_id, type, amount, description, recipient, timestamp
```

### Investments Table
```sql
id, user_id, type, amount
```

### Portfolio Table
```sql
id, user_id, investment_type, amount, units, purchase_price, purchase_date
```

## 🎭 Demo Data

The app comes with pre-loaded demo users:

- **Niraj** - Balance: ₹10,000 (Default user)
- **Rahul** - Balance: ₹15,000
- **Priya** - Balance: ₹20,000
- **Amit** - Balance: ₹12,000

**Default PIN for all users:** `1234`

You can switch between users using the dropdown in the app header.

## 🔐 Security Note

⚠️ This is a **demo application** for educational purposes. It does not process real payments or connect to actual payment gateways.

## 📊 Investment Features

- **Real Market Data**: Uses yfinance to fetch live prices for Gold ETF, Nifty 50 ETF, and other instruments
- **Portfolio Tracking**: Tracks your investments with real market prices
- **Investment Analysis**: Analyzes your spending and suggests potential returns
- **Smart Nudges**: AI-powered investment recommendations after payments

## 🐛 Troubleshooting

### Backend Issues

**Error: GEMINI_API_KEY is required**
- Make sure you've created `backend/.env` file
- Add your Gemini API key: `GEMINI_API_KEY=your_key_here`

**Database errors**
- Delete `voicepay.db` and restart the backend
- The database will be recreated automatically

**yfinance errors**
- Market data may be unavailable outside trading hours
- The app will gracefully handle this and show appropriate messages

### Frontend Issues

**Voice not working**
- Check microphone permissions in your browser
- Use Chrome or Edge for best Web Speech API support
- Firefox has limited speech recognition support

**No audio output**
- If you haven't set `VITE_ELEVENLABS_API_KEY`, the app uses browser TTS
- Check your browser's audio settings
- Some browsers may block audio autoplay

**CORS errors**
- Make sure backend is running on port 8000
- Check `VITE_API_BASE_URL` in `frontend/.env`

## 🚀 Deployment

### Backend Deployment (Heroku/Railway/Render)

1. Add `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Set environment variables:
```
GEMINI_API_KEY=your_key
```

### Frontend Deployment (Vercel/Netlify)

1. Build command: `npm run build`
2. Output directory: `dist`
3. Set environment variables:
```
VITE_ELEVENLABS_API_KEY=your_key
VITE_API_BASE_URL=https://your-backend-url
```

## 🤝 Contributing

This is a demo project built for educational purposes. Feel free to fork and modify for your own learning!

## 📝 License

MIT License - feel free to use for your projects!

## 🙏 Credits

- **Gemini AI** by Google
- **ElevenLabs** for premium TTS
- **FastAPI** framework
- **React** team
- **yfinance** for market data

---

**Built with ❤️ for the future of voice-first payments**

Made by Niraj | November 2024

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the error messages in browser console
3. Ensure all API keys are correctly set

---

## 🎬 Demo Ready Features

✅ **Voice Commands** - Fully functional  
✅ **Payment Flow** - Complete with PIN security  
✅ **Investment Nudges** - AI-powered with real data  
✅ **Transaction History** - Real-time updates  
✅ **Balance Tracking** - Live updates  
✅ **Beautiful UI** - Modern gradient design  
✅ **Error Handling** - Graceful fallbacks  
✅ **Real Market Data** - yfinance integration  
✅ **Portfolio Tracking** - Live investment values  
✅ **Multi-user Support** - Switch between users  

**Total Features:** 50+  
**Demo Readiness:** 100%  
**Production Ready:** No (Demo purposes only)

