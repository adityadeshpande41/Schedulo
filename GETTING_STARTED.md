# Getting Started with Schedulo

This guide will get you up and running with the Schedulo AI scheduling system in under 10 minutes.

## Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.11 or higher
- ✅ PostgreSQL installed and running
- ✅ Node.js 18 or higher
- ✅ OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
cd python_backend
pip install -r requirements.txt

# Install Node dependencies
cd ..
npm install
```

### 2. Set Up Database

```bash
# Create PostgreSQL database
createdb schedulo

# Or using psql:
psql -U postgres
CREATE DATABASE schedulo;
\q
```

### 3. Configure Environment

```bash
cd python_backend

# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required settings in `.env`:**

```bash
# Database (update with your credentials)
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/schedulo

# OpenAI (required for AI features)
OPENAI_API_KEY=sk-your-api-key-here

# Optional (defaults are fine)
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1000
CONFIDENCE_THRESHOLD=0.6
```

### 4. Initialize Database

```bash
# Create tables
python cli.py init

# Seed with sample data (5 users, preferences, meetings)
python cli.py seed
```

You should see:
```
✅ Database initialized successfully
✅ Seeded 5 users
✅ Seeded 5 user preferences
✅ Seeded 10 sample meetings
```

### 5. Test the System

```bash
# Run comprehensive test suite
python test_system.py
```

This will test:
- ✅ OpenAI integration
- ✅ ML behavior model
- ✅ Personal agents
- ✅ Edge case handler
- ✅ LangGraph orchestrator

Expected output:
```
🚀 SCHEDULO AI SYSTEM TEST SUITE
================================
✅ OpenAI API key found
...
📊 TEST SUMMARY
================================
✅ PASS - OpenAI Integration
✅ PASS - ML Behavior Model
✅ PASS - Personal Agent
✅ PASS - Edge Case Handler
✅ PASS - LangGraph Orchestrator

5/5 tests passed
🎉 All tests passed! System is ready.
```

### 6. Start Backend Server

```bash
# Start FastAPI server
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 7. Start Frontend (New Terminal)

```bash
# In a new terminal window
cd ..
npm run dev:frontend
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5000/
```

### 8. Access the Application

Open your browser and navigate to:

- **Frontend**: http://localhost:5000
- **API Documentation**: http://localhost:8000/docs
- **API Base**: http://localhost:8000/api

## Quick Test

### Test via API

```bash
# Schedule a meeting
curl -X POST http://localhost:8000/api/schedule/request \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Sync",
    "attendee_ids": ["u1", "u2"],
    "duration": 30,
    "meeting_type": "team_sync",
    "priority": "medium"
  }'
```

### Test via Frontend

1. Go to http://localhost:5000
2. Click "Schedule Meeting"
3. Fill in:
   - Title: "Team Sync"
   - Select attendees: Alex, Sarah
   - Duration: 30 minutes
4. Click "Find Times"
5. See AI-powered recommendations!

## Understanding the Sample Data

The seed command creates:

### Users (5)
- u1: Alex Chen (alex@example.com)
- u2: Sarah Johnson (sarah@example.com)
- u3: Marcus Williams (marcus@example.com)
- u4: Emily Davis (emily@example.com)
- u5: James Wilson (james@example.com)

### Preferences
Each user has:
- Work hours: 9 AM - 5 PM
- Timezone: UTC
- Preferred meeting duration: 30 minutes
- Buffer time: 5 minutes
- Max meetings per day: 8

### Sample Meetings
10 historical meetings for ML training

## Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Ensure PostgreSQL is running
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Check status
psql -U postgres -c "SELECT version();"
```

### OpenAI API Error

```
⚠️ Warning: OPENAI_API_KEY not set, using mock responses
```

**Solution**: Set your API key
```bash
export OPENAI_API_KEY=sk-your-key-here
```

Or add to `.env` file.

### Port Already in Use

```
ERROR: [Errno 48] Address already in use
```

**Solution**: Use different port
```bash
# Backend
uvicorn main:app --reload --port 8001

# Frontend
npm run dev:frontend -- --port 5001
```

### Import Errors

```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution**: Reinstall dependencies
```bash
cd python_backend
pip install -r requirements.txt --force-reinstall
```

## Next Steps

### 1. Explore the API

Visit http://localhost:8000/docs to see:
- All available endpoints
- Request/response schemas
- Try out API calls interactively

### 2. View Agent Activity

```bash
# Get agent activity
curl http://localhost:8000/api/agents/activity
```

### 3. Check Upcoming Meetings

```bash
# Get upcoming meetings
curl http://localhost:8000/api/meetings/upcoming
```

### 4. Customize Preferences

```bash
# Update user preferences
curl -X PUT http://localhost:8000/api/preferences/u1 \
  -H "Content-Type: application/json" \
  -d '{
    "work_hours_start": "10:00",
    "work_hours_end": "18:00",
    "preferred_meeting_duration": 45
  }'
```

### 5. Add More Users

```bash
# Use the CLI
python cli.py seed --users 10
```

### 6. View Database

```bash
# Connect to database
psql schedulo

# View users
SELECT * FROM users;

# View meetings
SELECT * FROM meetings;

# View preferences
SELECT * FROM user_preferences;
```

## Understanding the Workflow

When you schedule a meeting, here's what happens:

1. **Parse Request** (OpenAI)
   - Natural language → structured data

2. **Personal Agents** (Parallel)
   - Each attendee's agent:
     - Loads private calendar
     - Loads preferences
     - Trains ML model on historical data
     - Predicts acceptance probability
     - Generates availability signal

3. **Coordinate** (Multi-Agent)
   - Finds consensus slots
   - Ranks by confidence

4. **Edge Cases** (Handler)
   - Checks timezone fairness
   - Validates working hours
   - Ensures no back-to-back overload

5. **Rank & Explain** (OpenAI)
   - Sorts recommendations
   - Generates human-readable explanations

6. **Decision** (Conditional)
   - High confidence → Complete
   - Low confidence → Escalate to human

## CLI Commands

```bash
# Database management
python cli.py init          # Create tables
python cli.py seed          # Add sample data
python cli.py drop          # Drop all tables
python cli.py reset         # Drop and recreate

# With options
python cli.py seed --users 10 --meetings 50
```

## Environment Variables Reference

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=sk-...

# Optional (with defaults)
OPENAI_MODEL=gpt-4                    # OpenAI model to use
OPENAI_MAX_TOKENS=1000                # Max tokens per request
CONFIDENCE_THRESHOLD=0.6              # Escalation threshold
LOOKBACK_DAYS=90                      # Days of history for ML
AGENT_TIMEOUT=30                      # Agent timeout (seconds)
MAX_NEGOTIATION_ROUNDS=3              # Max coordination rounds
DEBUG=False                           # Debug mode
```

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- Backend: Changes to `.py` files auto-reload
- Frontend: Changes to `.tsx` files auto-reload

### View Logs

```bash
# Backend logs (in terminal running uvicorn)
# Shows:
# - API requests
# - Agent execution
# - Database queries
# - OpenAI API calls

# Frontend logs (browser console)
# Shows:
# - API calls
# - React Query cache
# - WebSocket messages
```

### Debug Mode

```bash
# Enable debug mode
export DEBUG=True

# Or in .env
DEBUG=True
```

### Database Inspection

```bash
# View all tables
psql schedulo -c "\dt"

# View table schema
psql schedulo -c "\d users"

# Count records
psql schedulo -c "SELECT COUNT(*) FROM meetings;"
```

## Resources

- **Documentation**: See `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Database Schema**: See `DATABASE.md`
- **Architecture**: See `FINAL_ARCHITECTURE.md`
- **Implementation Status**: See `IMPLEMENTATION_STATUS.md`

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs (backend terminal)
3. Check API documentation at `/docs`
4. Review the test output from `test_system.py`

## What's Next?

Now that you have the system running:

1. **Explore the UI** - Schedule meetings, view recommendations
2. **Test the API** - Try different scenarios
3. **Review the Code** - Understand the architecture
4. **Customize** - Add your own features
5. **Deploy** - See `DEPLOYMENT.md` for production setup

---

**You're all set! 🚀**

The system is now running and ready to schedule meetings intelligently using AI.
