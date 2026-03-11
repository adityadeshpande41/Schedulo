# Schedulo - Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Start the Backend (Python FastAPI)

```bash
cd python_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --port 8000
```

Backend running at: **http://localhost:8000**  
API docs at: **http://localhost:8000/docs**

### 2. Start the Frontend (React + Vite)

```bash
# In a new terminal, from project root
npm install
npm run dev:frontend
```

Frontend running at: **http://localhost:5000**

### 3. Open Your Browser

Navigate to **http://localhost:5000** and start scheduling!

---

## 📁 Project Structure

```
AI-Scheduler-Frontend/
├── python_backend/          # FastAPI backend
│   ├── agents/             # AI agent system
│   ├── api/                # REST API endpoints
│   ├── services/           # Business logic
│   └── main.py             # FastAPI app
│
├── client/                 # React frontend
│   ├── src/
│   │   ├── pages/          # Dashboard, Agent Flow, Decision
│   │   ├── hooks/          # React Query hooks
│   │   ├── lib/api.ts      # API client
│   │   └── components/     # UI components
│   └── .env                # Frontend config
│
└── INTEGRATION.md          # Detailed integration docs
```

---

## 🔧 Configuration

### Frontend (`.env`)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_DEFAULT_USER_ID=u1
```

### Backend (`python_backend/.env`)
```bash
API_V1_STR=/api
PROJECT_NAME=Schedulo
CORS_ORIGINS=http://localhost:5000,http://localhost:5173
```

---

## 🧪 Test the Integration

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Create Schedule Request
```bash
curl -X POST http://localhost:8000/api/schedule/request \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Sync",
    "attendee_ids": ["u1", "u2"],
    "duration": 60,
    "priority": "high",
    "meeting_type": "team_sync"
  }'
```

---

## 📚 Key Features

✅ **Multi-Agent AI System** - 4 specialized agents working together  
✅ **Real-time Updates** - WebSocket support for live agent status  
✅ **Smart Caching** - React Query for efficient data fetching  
✅ **Type-Safe** - Full TypeScript + Python type hints  
✅ **Explainable AI** - Every recommendation comes with reasoning  

---

## 🎯 What's Working

- ✅ Frontend connected to backend via REST API
- ✅ All pages using real API calls (Dashboard, Agent Flow, Decision)
- ✅ React Query hooks for data fetching
- ✅ WebSocket support for real-time updates
- ✅ AI agent orchestration system
- ✅ CORS configured properly

---

## 🔜 Next Steps

1. **Database Integration** - Connect to PostgreSQL
2. **Authentication** - Add JWT tokens
3. **Calendar APIs** - Google Calendar, Outlook
4. **ML Models** - Behavior prediction
5. **Production Deploy** - Docker, CI/CD

---

## 📖 Documentation

- **INTEGRATION.md** - Detailed integration guide
- **python_backend/README.md** - Backend documentation
- **API Docs** - http://localhost:8000/docs (when running)

---

## 🐛 Troubleshooting

**Backend won't start?**
- Check Python version: `python3 --version` (need 3.8+)
- Activate venv: `source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`

**Frontend can't connect?**
- Ensure backend is running on port 8000
- Check `.env` file has correct API_URL
- Verify CORS settings in backend

**CORS errors?**
- Check `python_backend/core/config.py` CORS_ORIGINS
- Ensure frontend URL is in the list
- Restart backend after config changes

---

## 💡 Tips

- Use **React Query DevTools** to debug API calls
- Check **FastAPI docs** at `/docs` for API testing
- Monitor **browser console** for errors
- Check **terminal logs** for backend errors

---

Happy Scheduling! 🎉
