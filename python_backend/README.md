# Schedulo AI Agent System

Multi-agent architecture for intelligent meeting scheduling.

## Architecture

### Agents

1. **Calendar Agent** (`calendar_agent.py`)
   - Scans calendars across all attendees
   - Identifies available time windows
   - Handles timezone normalization
   - Detects hard and soft conflicts

2. **Behavior Agent** (`behavior_agent.py`)
   - Learns from historical scheduling patterns
   - Analyzes user preferences (time of day, days of week)
   - Scores windows based on learned behavior
   - Predicts acceptance rates

3. **Coordination Agent** (`coordination_agent.py`)
   - Negotiates across attendee preferences
   - Resolves scheduling conflicts
   - Balances priorities
   - Optimizes for timezone fairness

4. **Orchestrator Agent** (`orchestrator_agent.py`)
   - Coordinates all agents
   - Synthesizes outputs into ranked recommendations
   - Generates explanations
   - Determines when human approval is needed

## Usage

```python
from agents import OrchestratorAgent

orchestrator = OrchestratorAgent()

context = {
    "attendee_ids": ["user1", "user2", "user3"],
    "duration": 60,
    "meeting_type": "team_sync",
    "priority": "high",
    "date_range": (start_date, end_date)
}

result = await orchestrator.execute(context)

# Access recommendations
slots = result.data["recommended_slots"]
explanations = result.data["explanations"]
```

## Installation

```bash
pip install -r requirements.txt
```

## Next Steps

- Integrate with calendar APIs (Google Calendar, Outlook)
- Connect to database for historical data
- Implement ML models for behavior prediction
- Add real-time agent status updates via WebSockets


## FastAPI Backend

### API Endpoints

#### Schedule
- `POST /api/schedule/request` - Create scheduling request
- `GET /api/schedule/slots/recommendations` - Get recommended slots
- `POST /api/schedule/slots/{slot_id}/confirm` - Confirm time slot

#### Meetings
- `GET /api/meetings/upcoming` - Get upcoming meetings
- `GET /api/meetings/{meeting_id}` - Get meeting details
- `GET /api/meetings/{meeting_id}/decision` - Get AI decision explanation
- `PATCH /api/meetings/{meeting_id}/status` - Update meeting status
- `DELETE /api/meetings/{meeting_id}` - Cancel meeting

#### Preferences
- `GET /api/preferences/{user_id}` - Get user preferences
- `PATCH /api/preferences/{preference_id}` - Update preference
- `POST /api/preferences/{user_id}` - Create preference

#### Agents
- `GET /api/agents/activity` - Get agent activity status
- `GET /api/agents/info` - Get agent information
- `WS /api/agents/ws/activity` - WebSocket for real-time updates

### Running the Backend

```bash
cd python_backend

# Option 1: Using the run script
./run.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Testing the API

```bash
# Health check
curl http://localhost:8000/api/health

# Create schedule request
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

### Architecture

```
python_backend/
├── agents/              # AI agent system
│   ├── base_agent.py
│   ├── calendar_agent.py
│   ├── behavior_agent.py
│   ├── coordination_agent.py
│   └── orchestrator_agent.py
├── api/
│   ├── models/          # Pydantic models
│   │   ├── requests.py
│   │   └── responses.py
│   └── routes/          # API endpoints
│       ├── schedule.py
│       ├── meetings.py
│       ├── preferences.py
│       └── agents.py
├── services/            # Business logic
│   ├── schedule_service.py
│   ├── meeting_service.py
│   ├── preference_service.py
│   └── agent_service.py
├── core/
│   └── config.py        # Configuration
└── main.py              # FastAPI app
```


## Database Setup

### Quick Start

```bash
# Install PostgreSQL
brew install postgresql@15  # macOS
# or: sudo apt install postgresql  # Linux

# Create database
createdb schedulo

# Set environment variable
export DATABASE_URL="postgresql://localhost/schedulo"

# Initialize database
python cli.py init

# Seed sample data
python cli.py seed
```

### CLI Commands

```bash
python cli.py init    # Create tables
python cli.py seed    # Add sample data
python cli.py drop    # Drop all tables
python cli.py reset   # Drop + init + seed
```

### Database Models

- **users** - User accounts
- **meetings** - Scheduled meetings
- **meeting_attendees** - Meeting participants
- **user_preferences** - Scheduling preferences
- **time_slots** - AI recommendations
- **meeting_decisions** - AI explanations
- **agent_activities** - Agent execution logs
- **schedule_requests** - Request history
- **calendar_events** - External calendar cache
- **historical_meetings** - Behavior analysis data

See `DATABASE.md` for detailed schema documentation.

### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

See `DEPLOYMENT.md` for deploying to Render.com (free tier).

Quick deploy:
1. Push to GitHub
2. Connect to Render
3. Use `render.yaml` blueprint
4. Database auto-configured
