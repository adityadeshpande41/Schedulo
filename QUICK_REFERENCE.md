# Schedulo - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# Setup (one time)
cd python_backend && pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
python cli.py init && python cli.py seed

# Run
uvicorn main:app --reload --port 8000  # Backend
npm run dev:frontend                    # Frontend (new terminal)

# Test
python test_system.py                   # Run test suite
```

## 🔑 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost:5432/schedulo
OPENAI_API_KEY=sk-your-key-here

# Optional (defaults shown)
OPENAI_MODEL=gpt-4
CONFIDENCE_THRESHOLD=0.6
LOOKBACK_DAYS=90
```

## 📡 API Endpoints

### Schedule
```bash
POST   /api/schedule/request              # Schedule meeting
GET    /api/schedule/slots/recommendations # Get recommendations
POST   /api/schedule/slots/{id}/confirm   # Confirm slot
```

### Meetings
```bash
GET    /api/meetings/upcoming              # Upcoming meetings
GET    /api/meetings/{id}                  # Get meeting
POST   /api/meetings                       # Create meeting
PUT    /api/meetings/{id}                  # Update meeting
DELETE /api/meetings/{id}                  # Delete meeting
```

### Preferences
```bash
GET    /api/preferences/{user_id}          # Get preferences
PUT    /api/preferences/{user_id}          # Update preferences
```

### Agents
```bash
GET    /api/agents/activity                # Agent activity
WS     /api/agents/ws/activity             # WebSocket updates
```

## 🗄️ Database Commands

```bash
python cli.py init          # Create tables
python cli.py seed          # Add sample data
python cli.py drop          # Drop all tables
python cli.py reset         # Drop and recreate

# With options
python cli.py seed --users 10 --meetings 50
```

## 🧪 Testing

```bash
# Full test suite
python test_system.py

# Individual component tests
python -c "from agents.personal_agent import PersonalAgent; print('OK')"
python -c "from agents.ml_behavior_model import BehaviorLearningModel; print('OK')"
python -c "from agents.openai_integration import OpenAIAssistant; print('OK')"

# API test
curl -X POST http://localhost:8000/api/schedule/request \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","attendee_ids":["u1","u2"],"duration":30}'
```

## 📁 Key Files

### AI Agents
- `agents/langgraph_orchestrator.py` - Main workflow
- `agents/personal_agent.py` - Per-user agent
- `agents/ml_behavior_model.py` - ML learning
- `agents/openai_integration.py` - GPT-4 integration
- `agents/multi_agent_coordinator.py` - Negotiation
- `agents/edge_case_handler.py` - Edge cases

### Backend
- `main.py` - FastAPI app
- `api/routes/schedule.py` - Schedule endpoints
- `services/user_data_service.py` - Data access
- `database/models.py` - Database models

### Frontend
- `client/src/pages/dashboard.tsx` - Main UI
- `client/src/lib/api.ts` - API client
- `client/src/hooks/use-schedule.ts` - Schedule hooks

### Config
- `python_backend/.env` - Environment variables
- `python_backend/requirements.txt` - Dependencies
- `alembic.ini` - Database migrations

## 🔍 Debugging

### View Logs
```bash
# Backend logs (terminal running uvicorn)
# Shows: API requests, agent execution, DB queries, OpenAI calls

# Frontend logs (browser console)
# Shows: API calls, React Query cache, WebSocket messages
```

### Database Inspection
```bash
psql schedulo

# View tables
\dt

# View users
SELECT * FROM users;

# View meetings
SELECT * FROM meetings;

# View preferences
SELECT * FROM user_preferences;
```

### Check API
```bash
# API documentation
open http://localhost:8000/docs

# Health check
curl http://localhost:8000/

# Get upcoming meetings
curl http://localhost:8000/api/meetings/upcoming
```

## 🏗️ Architecture Overview

```
User → Frontend → API → LangGraph → Personal Agents → Database
                                  ↓
                            OpenAI + ML
```

### Workflow
1. **Parse** - OpenAI parses natural language
2. **Agents** - Personal agents check availability (parallel)
3. **Coordinate** - Find consensus across agents
4. **Edge Cases** - Validate timezone, hours, conflicts
5. **Rank** - Sort by confidence, generate explanations
6. **Decision** - Complete or escalate

## 🔒 Privacy Model

### Agents Share
✅ Status: "available" | "busy" | "flexible"
✅ Confidence: 0.0 - 1.0
✅ Flexibility: 0.0 - 1.0

### Agents Never Share
❌ Calendar event titles
❌ Meeting descriptions
❌ Full calendar view

## 📊 Sample Data

### Users (after seed)
- u1: Alex Chen (alex@example.com)
- u2: Sarah Johnson (sarah@example.com)
- u3: Marcus Williams (marcus@example.com)
- u4: Emily Davis (emily@example.com)
- u5: James Wilson (james@example.com)

### Test Request
```json
{
  "title": "Team Sync",
  "attendee_ids": ["u1", "u2"],
  "duration": 30,
  "meeting_type": "team_sync",
  "priority": "medium"
}
```

## 🐛 Common Issues

### Database Connection Error
```bash
# Check PostgreSQL is running
brew services start postgresql  # macOS
sudo systemctl start postgresql # Linux

# Test connection
psql -U postgres -c "SELECT version();"
```

### OpenAI API Error
```bash
# Set API key
export OPENAI_API_KEY=sk-your-key-here

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Port Already in Use
```bash
# Use different port
uvicorn main:app --reload --port 8001
npm run dev:frontend -- --port 5001
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Documentation

- **README.md** - Project overview
- **GETTING_STARTED.md** - Setup guide
- **SYSTEM_FLOW.md** - How it works
- **FINAL_ARCHITECTURE.md** - Complete system
- **IMPLEMENTATION_STATUS.md** - Current status
- **PROJECT_SUMMARY.md** - Key achievements

## 🎯 URLs

- Frontend: http://localhost:5000
- API Docs: http://localhost:8000/docs
- API Base: http://localhost:8000/api

## 💡 Tips

### Development
- Backend auto-reloads on `.py` file changes
- Frontend auto-reloads on `.tsx` file changes
- Use API docs at `/docs` for interactive testing

### Performance
- Agents run in parallel (3 agents = ~1.5s total)
- ML predictions are cached
- Database uses connection pooling

### Debugging
- Enable debug mode: `DEBUG=True` in `.env`
- Check logs in terminal running uvicorn
- Use browser console for frontend issues

## 🚀 Next Steps

1. **Test** - Run `python test_system.py`
2. **Explore** - Try the API at `/docs`
3. **Customize** - Modify agents or add features
4. **Deploy** - See `DEPLOYMENT.md`

---

**Quick reference for the Schedulo AI scheduling system** 📋
