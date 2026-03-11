# Schedulo - Final Architecture

## 🎯 Complete Multi-Agent AI System

### What We Built

A **production-ready, privacy-preserving multi-agent AI scheduling system** with:

1. ✅ **LangGraph Orchestration** - State-based workflow management
2. ✅ **Personal Agents** - One per user, privacy-isolated
3. ✅ **ML Behavior Learning** - Real learning from historical data
4. ✅ **OpenAI Integration** - GPT-4 for NLP and reasoning
5. ✅ **Multi-Agent Coordination** - Privacy-preserving negotiation
6. ✅ **Edge Case Handling** - 10+ edge cases covered
7. ✅ **Database Layer** - PostgreSQL with SQLAlchemy
8. ✅ **REST API** - FastAPI backend
9. ✅ **React Frontend** - Modern UI with real-time updates

---

## 🏗️ System Architecture

### Layer 1: LangGraph Orchestration

```
┌─────────────────────────────────────────────────────────┐
│           LangGraph Orchestrator                        │
│                                                         │
│  Workflow Graph:                                        │
│  START → Parse → Personal Agents → Coordinate →        │
│  Edge Cases → Rank → [Escalate | Complete] → END       │
│                                                         │
│  Features:                                              │
│  • State management across agents                       │
│  • Conditional routing (if/else logic)                  │
│  • Checkpointing (fault tolerance)                      │
│  • Human-in-the-loop (escalation)                       │
└─────────────────────────────────────────────────────────┘
```

**File**: `agents/langgraph_orchestrator.py`

### Layer 2: Personal Agents (Privacy-Preserving)

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Alex's Agent │    │ Sarah's Agent│    │Marcus's Agent│
├──────────────┤    ├──────────────┤    ├──────────────┤
│ ML Model     │    │ ML Model     │    │ ML Model     │
│ OpenAI       │    │ OpenAI       │    │ OpenAI       │
│ Private Cal  │    │ Private Cal  │    │ Private Cal  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
              Shares only: "available/busy/flexible"
              Never shares: calendar details
```

**Files**:
- `agents/personal_agent.py` - Main agent logic
- `agents/ml_behavior_model.py` - ML learning
- `agents/openai_integration.py` - GPT-4 integration

### Layer 3: Coordination & Edge Cases

```
┌─────────────────────────────────────────────────────────┐
│         Multi-Agent Coordinator                         │
│                                                         │
│  • Receives availability signals                        │
│  • Finds consensus (all available)                      │
│  • Handles conflicts                                    │
│  • Ranks recommendations                                │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Edge Case Handler                               │
│                                                         │
│  Handles:                                               │
│  ✓ Timezone conflicts                                   │
│  ✓ All attendees busy                                   │
│  ✓ Conflicting priorities                               │
│  ✓ Last-minute requests                                 │
│  ✓ Recurring conflicts                                  │
│  ✓ Vacation/holidays                                    │
│  ✓ Working hours violations                             │
│  ✓ Back-to-back limits                                  │
│  ✓ Duration constraints                                 │
│  ✓ Availability gaps                                    │
└─────────────────────────────────────────────────────────┘
```

**Files**:
- `agents/multi_agent_coordinator.py`
- `agents/edge_case_handler.py`

### Layer 4: Data & API

```
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend                            │
│                                                         │
│  Endpoints:                                             │
│  • POST /api/schedule/request                           │
│  • GET  /api/meetings/upcoming                          │
│  • GET  /api/agents/activity                            │
│  • GET  /api/preferences/{user_id}                      │
│  • WS   /api/agents/ws/activity                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│           PostgreSQL Database                           │
│                                                         │
│  Tables:                                                │
│  • users, meetings, meeting_attendees                   │
│  • user_preferences, time_slots                         │
│  • meeting_decisions, agent_activities                  │
│  • schedule_requests, calendar_events                   │
│  • historical_meetings (for ML)                         │
└─────────────────────────────────────────────────────────┘
```

**Files**:
- `main.py` - FastAPI app
- `api/routes/` - API endpoints
- `database/models.py` - SQLAlchemy models

### Layer 5: Frontend

```
┌─────────────────────────────────────────────────────────┐
│              React Frontend                             │
│                                                         │
│  Pages:                                                 │
│  • Dashboard - Schedule meetings                        │
│  • Agent Flow - Visualize agents                        │
│  • Decision - AI explanations                           │
│                                                         │
│  Features:                                              │
│  • Real-time updates (React Query)                      │
│  • WebSocket for agent status                           │
│  • Dark mode, animations                                │
└─────────────────────────────────────────────────────────┘
```

**Files**:
- `client/src/pages/` - React pages
- `client/src/hooks/` - React Query hooks
- `client/src/lib/api.ts` - API client

---

## 🤖 AI Components Breakdown

### 1. LangGraph Orchestrator

**What it does**:
- Manages workflow state
- Routes between agents
- Handles escalation
- Provides checkpointing

**Key Features**:
```python
# State management
class SchedulingState(TypedDict):
    request: str
    attendee_ids: list[str]
    personal_agent_signals: dict
    consensus_slots: list[dict]
    ranked_recommendations: list[dict]
    escalation_needed: bool

# Conditional routing
def should_escalate(state) -> "escalate" | "complete":
    if state["confidence"] < 0.6:
        return "escalate"
    return "complete"
```

### 2. Personal Agent

**What it does**:
- Learns user preferences via ML
- Predicts acceptance probability
- Generates availability signals
- Never shares private data

**Key Features**:
```python
# ML prediction
acceptance_prob = model.predict_acceptance(
    time_window, meeting_context, historical_data
)

# Privacy-preserving signal
signal = AvailabilitySignal(
    status="available",  # Not calendar details!
    confidence=0.92,
    flexibility=0.7
)
```

### 3. ML Behavior Model

**What it learns**:
- Time of day preferences (85% acceptance at 2pm)
- Day of week patterns (prefers Tue/Thu)
- Meeting type preferences (reschedules internal for clients)
- Reschedule probability (40% for 1:1s)

**Algorithm**:
```python
# Features
X = [hour, day_of_week, meeting_type, duration, priority]

# Target
y = was_accepted  # Binary classification

# Model
model = RandomForestClassifier()
model.fit(X, y)

# Prediction
prob = model.predict_proba(new_slot)[0][1]
```

### 4. OpenAI Integration

**Use cases**:
1. **Parse requests**: "Schedule 30-min sync next week" → structured data
2. **Query preferences**: "When does Alex prefer meetings?" → answer
3. **Resolve conflicts**: High-priority conflict → reasoning
4. **Generate explanations**: Why this slot? → human-readable text

**Implementation**:
```python
# Parse natural language
parsed = await openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{
        "role": "system",
        "content": "Parse scheduling request"
    }, {
        "role": "user",
        "content": request
    }]
)
```

### 5. Edge Case Handler

**Handles**:
- Timezone conflicts (international teams)
- All attendees busy (find flexible slots)
- Conflicting priorities (escalate)
- Last-minute requests (< 24 hours)
- Recurring conflicts (one-time vs permanent)
- Vacation/holidays (exclude periods)
- Working hours violations (respect boundaries)
- Back-to-back limits (max 3 consecutive)
- Duration constraints (doesn't fit)
- Availability gaps (systematic conflicts)

---

## 🔒 Privacy Guarantees

### What Agents Share
✅ Status: "available" | "busy" | "flexible"
✅ Confidence: 0.85
✅ Flexibility: 0.7
✅ Priority override: "can_reschedule_internal"

### What Agents NEVER Share
❌ Calendar event titles
❌ Meeting descriptions
❌ Attendee lists
❌ Location details
❌ Full calendar view
❌ Personal patterns

---

## 📊 Data Flow Example

### Request: "Schedule Q2 planning with Sarah, Marcus, Priya"

```
1. LangGraph: START
   └─> Parse Request Node

2. OpenAI: Parse natural language
   Input: "Schedule Q2 planning with Sarah, Marcus, Priya"
   Output: {
     attendees: ["Sarah", "Marcus", "Priya"],
     duration: 60,
     type: "team_sync",
     priority: "high"
   }

3. LangGraph: Personal Agents Node (Parallel)
   
   Alex's Agent:
   ├─> Check private calendar
   ├─> ML predicts: 92% acceptance
   ├─> Evaluate preferences
   └─> Signal: "available, confidence: 0.92"
   
   Sarah's Agent:
   ├─> Check private calendar
   ├─> ML predicts: 88% acceptance
   ├─> Evaluate preferences
   └─> Signal: "available, confidence: 0.88"
   
   Marcus's Agent:
   ├─> Check private calendar
   ├─> ML predicts: 75% acceptance
   ├─> Evaluate preferences
   └─> Signal: "flexible, confidence: 0.75"

4. LangGraph: Coordinate Node
   ├─> Find consensus: Tuesday 2pm
   ├─> All agents: available
   └─> Avg confidence: 0.85

5. LangGraph: Edge Cases Node
   ├─> Check timezone: Fair for all ✓
   ├─> Check working hours: Within bounds ✓
   ├─> Check back-to-back: No issues ✓
   └─> Edge cases: None

6. LangGraph: Rank Node
   ├─> Sort by confidence
   ├─> OpenAI generates explanation
   └─> Top slot: Tuesday 2pm (85% confidence)

7. LangGraph: Conditional Routing
   ├─> Confidence: 85% (> 60% threshold)
   ├─> No approval needed
   └─> Route: COMPLETE

8. LangGraph: Complete Node
   └─> Return recommendations

9. User sees:
   "Best time: Tuesday 2pm (85% confidence)"
   "All attendees available"
   "Explanation: This time works well because..."
   [Schedule] [See Alternatives]
```

---

## 🚀 Key Innovations

### 1. Privacy-Preserving
- No centralized calendar access
- Distributed agent architecture
- Minimal information sharing

### 2. Truly Multi-Agent
- Each agent is independent
- Parallel execution
- Negotiation protocol

### 3. ML-Powered
- Real learning, not rules
- Incremental updates
- Personalized per user

### 4. LangGraph Orchestration
- State-based workflows
- Conditional routing
- Fault tolerance
- Human-in-the-loop

### 5. OpenAI-Enhanced
- Natural language understanding
- Intelligent reasoning
- Human-readable explanations

### 6. Production-Ready
- Comprehensive edge cases
- Database-backed
- REST API
- WebSocket support
- Scalable architecture

---

## 📁 Complete File Structure

```
python_backend/
├── agents/
│   ├── langgraph_orchestrator.py     # LangGraph workflow ⭐
│   ├── personal_agent.py             # Per-user agent ⭐
│   ├── ml_behavior_model.py          # ML learning ⭐
│   ├── openai_integration.py         # GPT-4 integration ⭐
│   ├── multi_agent_coordinator.py    # Negotiation ⭐
│   ├── edge_case_handler.py          # Edge cases ⭐
│   ├── base_agent.py                 # Base class
│   └── __init__.py                   # Exports
│
├── database/
│   ├── models.py                     # SQLAlchemy models
│   ├── connection.py                 # DB connection
│   ├── seed.py                       # Sample data
│   └── __init__.py
│
├── api/
│   ├── routes/
│   │   ├── schedule.py               # Scheduling endpoints
│   │   ├── meetings.py               # Meeting CRUD
│   │   ├── preferences.py            # User preferences
│   │   └── agents.py                 # Agent status
│   └── models/
│       ├── requests.py               # Request models
│       └── responses.py              # Response models
│
├── services/
│   ├── schedule_service.py           # Business logic
│   ├── meeting_service.py
│   ├── preference_service.py
│   └── agent_service.py
│
├── core/
│   └── config.py                     # Configuration
│
├── alembic/                          # Database migrations
├── main.py                           # FastAPI app
├── cli.py                            # CLI tool
└── requirements.txt                  # Dependencies

client/
├── src/
│   ├── pages/
│   │   ├── dashboard.tsx             # Main UI
│   │   ├── agent-flow.tsx            # Agent visualization
│   │   └── decision.tsx              # AI explanations
│   ├── hooks/
│   │   ├── use-schedule.ts           # Scheduling hooks
│   │   ├── use-meetings.ts           # Meeting hooks
│   │   ├── use-agents.ts             # Agent hooks
│   │   └── use-preferences.ts        # Preference hooks
│   ├── lib/
│   │   └── api.ts                    # API client
│   └── components/                   # UI components
└── .env                              # Frontend config

Documentation/
├── SYSTEM_OVERVIEW.md                # High-level overview
├── AI_ARCHITECTURE.md                # AI system design
├── LANGGRAPH_ARCHITECTURE.md         # LangGraph details
├── DATABASE.md                       # Database schema
├── DEPLOYMENT.md                     # Deployment guide
├── INTEGRATION.md                    # Frontend-backend
└── QUICKSTART.md                     # Get started
```

---

## 🎯 What Makes This Portfolio-Worthy

### Technical Depth
✅ Multi-agent AI system
✅ LangGraph orchestration
✅ ML behavior learning
✅ OpenAI integration
✅ Privacy-preserving design

### Production Quality
✅ Comprehensive edge cases
✅ Database layer
✅ REST API
✅ Frontend integration
✅ Documentation

### Innovation
✅ Solves real problem
✅ Novel approach (privacy-preserving)
✅ Scalable architecture
✅ Explainable AI

### Completeness
✅ Backend + Frontend
✅ AI + ML + NLP
✅ Database + API
✅ Tests + Docs
✅ Deployment ready

---

## 🚦 Getting Started

```bash
# 1. Install dependencies
cd python_backend
pip install -r requirements.txt

# 2. Set OpenAI key
export OPENAI_API_KEY=sk-...

# 3. Initialize database
python cli.py init
python cli.py seed

# 4. Start backend
uvicorn main:app --reload --port 8000

# 5. Start frontend (new terminal)
cd ../
npm install
npm run dev:frontend

# 6. Open browser
# Frontend: http://localhost:5000
# API Docs: http://localhost:8000/docs
```

---

## 📚 Documentation

- **SYSTEM_OVERVIEW.md** - Start here
- **AI_ARCHITECTURE.md** - AI system design
- **LANGGRAPH_ARCHITECTURE.md** - Orchestration details
- **DATABASE.md** - Database schema
- **DEPLOYMENT.md** - Production deployment
- **INTEGRATION.md** - Frontend-backend
- **QUICKSTART.md** - 5-minute setup

---

## 🎓 Skills Demonstrated

- Multi-agent AI systems
- LangGraph orchestration
- Machine learning (scikit-learn)
- Natural language processing (OpenAI)
- Privacy-preserving design
- Distributed systems
- FastAPI backend
- React frontend
- PostgreSQL database
- REST API design
- WebSocket real-time
- Production architecture

---

**Built to solve a real problem with innovative AI** 🚀
