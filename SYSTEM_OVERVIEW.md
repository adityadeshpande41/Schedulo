# Schedulo - Multi-Agent AI Scheduling System

## 🎯 Problem Statement

Meeting scheduling is solved when one person has access to all calendars. But what if access is gated? Can you build an agentic system where each agent only has access to one person's calendar, yet meetings are scheduled based on multiple people's availability?

**Additional Challenge**: Learn preferences over time instead of just finding open slots, and escalate to humans when needed.

## ✨ Our Solution

A **privacy-preserving multi-agent AI system** where:
- Each user has their own AI agent
- Agents learn individual preferences via ML
- Agents negotiate without sharing private data
- OpenAI powers natural language understanding
- Comprehensive edge case handling

## 🏗️ Architecture

### LangGraph Orchestrator (Workflow Management)
```python
class LangGraphOrchestrator:
    - State-based workflow graph
    - Conditional routing (escalate vs complete)
    - Checkpointing (fault tolerance)
    - Human-in-the-loop (escalation)
    
Workflow:
START → Parse → Personal Agents → Coordinate → 
Edge Cases → Rank → [Escalate | Complete] → END
```

### Personal Agent (One Per User)
```python
class PersonalAgent:
    - ML Behavior Model (learns preferences)
    - OpenAI Assistant (NLP & reasoning)
    - Private Calendar Access (owner only)
    - Availability Signal Generator (privacy-preserving)
```

**What It Does**:
- ✅ Learns from 90 days of history
- ✅ Predicts acceptance probability
- ✅ Identifies reschedule patterns
- ✅ Shares only: "available/busy/flexible"
- ✅ Never shares: calendar details

### ML Behavior Model
```python
Learns:
- Time of day preferences (85% acceptance at 2pm)
- Day of week patterns (prefers Tue/Thu)
- Meeting type preferences (reschedules internal for clients)
- Reschedule probability (40% for 1:1s)

Algorithm: Random Forest / XGBoost
Training: Incremental learning from feedback
```

### OpenAI Integration
```python
Use Cases:
1. Parse: "Schedule 30-min sync next week, afternoon"
2. Query: "When does Alex prefer meetings?"
3. Resolve: High-priority conflict reasoning
4. Explain: "Tuesday 2pm is optimal because..."

Model: GPT-4
```

### Multi-Agent Coordinator
```python
Protocol:
1. Generate candidate windows
2. Request availability signals (parallel)
3. Find consensus (all available)
4. Handle edge cases
5. Rank & explain (OpenAI)
6. Escalate if needed
```

### Edge Case Handler
```python
Handles:
- Timezone conflicts (international teams)
- All attendees busy
- Conflicting priorities
- Last-minute requests
- Recurring conflicts
- Vacation/holidays
- Working hours violations
- Back-to-back limits
- Duration constraints
- Availability gaps
```

## 🔒 Privacy Guarantees

### What Agents Share
✅ Status: "available" | "busy" | "flexible"
✅ Confidence: 0.85
✅ Flexibility: 0.7

### What Agents NEVER Share
❌ Calendar event titles
❌ Meeting descriptions
❌ Attendee lists
❌ Full calendar view

## 🎨 User Experience

### Simple Request
```
User: "Schedule 30-min sync with Sarah"

Behind the scenes:
1. Alex's Agent: Checks calendar, ML predicts 92% acceptance
2. Sarah's Agent: Checks calendar, ML predicts 88% acceptance
3. Coordinator: Finds Tuesday 2pm (both available)
4. OpenAI: Generates explanation
5. User sees: "Tuesday 2pm (90% confidence)"

Time: 5 seconds vs 5 emails
```

### Complex Multi-Person
```
User: "Schedule Q2 planning with Sarah, Marcus, Priya"

Behind the scenes:
1. 4 agents analyze independently
2. Coordinator negotiates
3. Handles timezone conflicts (Priya in India)
4. Finds optimal slot
5. Explains reasoning

Time: 10 seconds vs 20+ emails
```

### Learned Behavior
```
After 2 months:
- Agent knows Alex reschedules internal for clients
- Agent knows Sarah prefers Tue/Thu for 1:1s
- Agent knows Marcus avoids Friday afternoons

Recommendation: "Thursday 3pm"
Why? Learned patterns + high confidence
```

### Smart Escalation
```
Scenario: Urgent client call conflicts with 1:1

Agent:
- Detects conflict
- ML: "Alex reschedules internal 85% of time"
- Confidence: 76% (below 80% threshold)
- ESCALATES TO HUMAN

User sees:
"⚠️ Conflicts with your 1:1 with Sarah"
"You usually reschedule internal for clients"
"Should I reschedule the 1:1?"
[Yes] [No] [Find another time]
```

## 🚀 Innovation Points

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

### 4. Explainable AI
- OpenAI generates explanations
- Transparent reasoning
- User trust

### 5. Production-Ready
- Comprehensive edge cases
- Scalable architecture
- Database-backed

## 📊 Technical Stack

**AI/ML**:
- LangGraph (multi-agent orchestration)
- LangChain (agent framework)
- OpenAI GPT-4 (NLP & reasoning)
- Scikit-learn (behavior learning)
- NumPy, Pandas (data processing)

**Backend**:
- FastAPI (async API)
- SQLAlchemy (ORM)
- PostgreSQL (database)
- Python asyncio (concurrency)

**Frontend**:
- React + TypeScript
- TanStack Query (data fetching)
- Tailwind CSS (styling)
- Framer Motion (animations)

## 📁 Project Structure

```
python_backend/
├── agents/
│   ├── langgraph_orchestrator.py  # LangGraph workflow
│   ├── personal_agent.py          # Per-user AI agent
│   ├── ml_behavior_model.py       # ML learning
│   ├── openai_integration.py      # GPT-4 integration
│   ├── multi_agent_coordinator.py # Negotiation
│   └── edge_case_handler.py       # Edge cases
├── database/
│   ├── models.py                  # SQLAlchemy models
│   ├── connection.py              # DB connection
│   └── seed.py                    # Sample data
├── api/
│   ├── routes/                    # API endpoints
│   └── models/                    # Pydantic models
└── main.py                        # FastAPI app

client/
├── src/
│   ├── pages/                     # React pages
│   ├── hooks/                     # React Query hooks
│   ├── lib/api.ts                 # API client
│   └── components/                # UI components
```

## 🎯 Key Features

### For Users
- ⏱️ **Time Saved**: 2-3 hours/month
- 🔒 **Privacy**: Calendar stays private
- 🤖 **Smart**: Learns preferences
- 📈 **Improves**: Gets better over time

### For Teams
- 🌍 **Timezone-Aware**: Fair for distributed teams
- ⚡ **Fast**: 4-person meeting in 10 seconds
- 🎯 **Intelligent**: Priority-based resolution
- 📊 **Insights**: Understand patterns

### For Organizations
- 💰 **ROI**: Less time in "scheduling hell"
- ✅ **Compliance**: Privacy by design
- 📈 **Scalable**: Works for 2 or 200 people
- 🔧 **Customizable**: Per-team preferences

## 🚦 Getting Started

### 1. Backend Setup
```bash
cd python_backend
pip install -r requirements.txt

# Set OpenAI key
export OPENAI_API_KEY=sk-...

# Initialize database
python cli.py init
python cli.py seed

# Start server
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
npm install
npm run dev:frontend
```

### 3. Open Browser
```
Frontend: http://localhost:5000
API Docs: http://localhost:8000/docs
```

## 📚 Documentation

- **AI_ARCHITECTURE.md** - Detailed AI system design
- **DATABASE.md** - Database schema & setup
- **DEPLOYMENT.md** - Production deployment
- **INTEGRATION.md** - Frontend-backend integration
- **QUICKSTART.md** - Get started in 5 minutes

## 🎓 Portfolio Value

This project demonstrates:
- ✅ Multi-agent AI systems
- ✅ Privacy-preserving ML
- ✅ OpenAI integration
- ✅ Production architecture
- ✅ Edge case handling
- ✅ Full-stack development
- ✅ Real-world problem solving

## 🔮 Future Enhancements

### Phase 2
- Real-time learning (online ML)
- Federated learning
- Voice/email input
- Calendar integrations (Google, Outlook)

### Phase 3
- Predictive scheduling
- Proactive suggestions
- Team-wide optimization
- Productivity analytics

## 📝 License

MIT

## 🙏 Acknowledgments

Inspired by the challenge from Distyl's hackathon on privacy-preserving multi-agent scheduling.

---

**Built to solve a real problem with innovative AI** 🚀
