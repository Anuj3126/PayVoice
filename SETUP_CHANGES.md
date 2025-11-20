# Setup Changes Summary

## ✅ Completed Changes

### 1. Moved Virtual Environment
- **Before**: `backend/venv/`
- **After**: `venv/` (in parent directory)
- **Reason**: Better organization for monorepo-style projects

### 2. Consolidated Environment Variables
- **Before**: 
  - `backend/.env` (backend variables)
  - `frontend/.env` (frontend variables)
- **After**: 
  - `.env` (single file in parent directory)
  - `frontend/.env` → symlink to `../.env`

### 3. Updated Backend Code
All backend files now load `.env` from parent directory:
- `backend/main.py`
- `backend/auth.py`
- `backend/investment_analyzer.py`
- `backend/investment_portfolio.py`
- `backend/serpapi_market_data.py`

**Code change pattern:**
```python
# Before
load_dotenv()

# After
import os
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)
```

### 4. Updated Frontend Configuration
- Updated `frontend/vite.config.js` to load env from parent directory
- Created symlink: `frontend/.env` → `../.env`
- Vite will automatically read `VITE_*` variables from the symlinked file

## 📁 New Project Structure

```
payvoice v2/
├── .env                    # ✅ Consolidated environment variables
├── venv/                   # ✅ Moved from backend/venv/
├── backend/
│   ├── .env               # ❌ Removed (now using parent .env)
│   └── main.py            # ✅ Updated to load parent .env
└── frontend/
    ├── .env               # ✅ Symlink to ../.env
    └── vite.config.js     # ✅ Updated to load from parent
```

## 🚀 How to Run

### Backend
```bash
cd "/Users/anujtewari/Documents/payvoice v2"
source venv/bin/activate
cd backend
python3 main.py
```

### Frontend
```bash
cd "/Users/anujtewari/Documents/payvoice v2/frontend"
npm run dev
```

## ✨ Benefits

1. **Single Source of Truth**: All environment variables in one place
2. **Easier Management**: Update API keys in one file
3. **Better Organization**: venv at project root is standard practice
4. **No Duplication**: Frontend and backend share Google Client ID from same file

## ⚠️ Important Notes

1. **SSL Certificate Paths**: Updated in `.env` to point to new venv location:
   ```
   SSL_CERT_FILE=/Users/anujtewari/Documents/payvoice v2/venv/lib/python3.13/site-packages/certifi/cacert.pem
   ```

2. **Environment Variables**: 
   - Backend variables: `GROQ_API_KEY`, `GOOGLE_CLIENT_ID`, `JWT_SECRET_KEY`, etc.
   - Frontend variables: Must be prefixed with `VITE_` (e.g., `VITE_GOOGLE_CLIENT_ID`)

3. **Symlink**: The `frontend/.env` is a symlink. If you need to edit it, edit the parent `.env` file.

## 🔍 Verification

To verify everything works:

```bash
# Test backend can load .env
cd backend
source ../venv/bin/activate
python3 -c "from dotenv import load_dotenv; import os; env_path = os.path.join('..', '.env'); load_dotenv(dotenv_path=env_path); print('GROQ_API_KEY:', bool(os.getenv('GROQ_API_KEY')))"

# Test frontend can read .env
cd frontend
cat .env | grep VITE_GOOGLE_CLIENT_ID
```

