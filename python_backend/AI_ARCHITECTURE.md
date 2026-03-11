# AI Architecture - Schedulo

## Overview

Schedulo is a **truly multi-agentic AI system** that solves privacy-preserving meeting scheduling through distributed intelligence and machine learning.

## Core Innovation

### The Problem
Traditional scheduling tools require access to all calendars (centralized). This violates privacy and doesn't scale for distributed teams.

### Our Solution
**Privacy-Preserving Multi-Agent System** where:
- Each user has their own AI agent
- Agents only access their owner's data
- Agents negotiate via minimal signals
- No raw calendar data is ever shared

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Multi-Agent Coordinator                         │
│         (No access to private calendar data)                 │
│                                                              │
│  • Facilitates negotiation protocol                          │
│  • Aggregates availability signals                           │
│  • Handles edge cases                                        │
│  • Generates explanations (OpenAI)                           │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Availability Signals Only
                            │ (never raw calendar data)
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼───────┐  ┌───────▼────────┐
│ Personal Agent │  │Personal Agent│  │ Personal Agent │
│   (Alex)       │  │   (Sarah)    │  │   (Marcus)     │
├────────────────┤  ├──────────────┤  ├────────────────┤
│ ML Model       │  │ ML Model     │  │ ML Model       │
│ OpenAI Context │  │ OpenAI Context│  │ OpenAI Context │
│ Private Cal    │  │ Private Cal  │  │ Private Cal    │
│ Preferences    │  │ Preferences  │  │ Preferences    │
└────────────────┘  └──────────────┘  └────────────────┘
```

## Orchestration Layer

### LangGraph Orchestrator

**Purpose**: State-based multi-agent workflow orchestration

**Features**:
- **Graph-based workflow**: Nodes (agents) + Edges (flow)
- **Conditional routing**: Dynamic decisions (escalate vs complete)
- **State management**: Shared state across all agents
- **Checkpointing**: Resume from failures
- **Human-in-the-loop**: Escalation support

**Workflow**:
```
START → Parse Request (OpenAI) → Personal Agents (Parallel) →
Coordinate → Edge Cases → Rank & Explain → 
Should Escalate? → [Escalate | Complete] → END
```

**File**: `agents/langgraph_orchestrator.py`

**Documentation**: `agents/LANGGRAPH_ARCHITECTURE.md`

## AI Components

### 1. Personal Agent (Per User)

**Purpose**: Privacy-preserving individual scheduling intelligence

**AI Features**:
- **ML Behavior Model**: Learns from historical data
  - Time of day preferences
  - Day of week patterns
  - Meeting type preferences
  - Reschedule probability
  - Acceptance prediction

- **OpenAI Integration**: Natural language understanding
  - Parse scheduling requests
  - Answer preference queries
  - Resolve conflicts with reasoning
  - Generate explanations

**Privacy Guarantee**: Only accesses owner's data, shares minimal signals

**File**: `agents/personal_agent.py`

### 2. ML Behavior Learning Model

**Purpose**: Learn user scheduling behavior from history

**Algorithm**:
```python
Features:
- hour_of_day (0-23)
- day_of_week (0-6)
- meeting_type (team_sync, client_call, etc.)
- duration (minutes)
- attendee_count
- priority (high/medium/low)
- previous_reschedules

Target:
- was_accepted (binary)
- was_rescheduled (binary)
- response_time (seconds)

Model: Random Forest / XGBoost
Training: Incremental learning from feedback
```

**Predictions**:
1. **Acceptance Probability**: Will user accept this slot?
2. **Reschedule Probability**: Will user reschedule existing meeting?
3. **Preference Score**: How well does slot match preferences?

**File**: `agents/ml_behavior_model.py`

### 3. OpenAI Assistant

**Purpose**: Natural language understanding and reasoning

**Use Cases**:

1. **Parse Requests**:
   ```
   Input: "Schedule 30-min sync with Sarah next week, afternoon"
   Output: {
     attendees: ["Sarah"],
     duration: 30,
     time_preference: "afternoon",
     date_range: "next_week"
   }
   ```

2. **Query Preferences**:
   ```
   Input: "When does Alex prefer meetings?"
   Output: "Alex prefers afternoon meetings (85% acceptance) 
            and avoids Friday after 3pm"
   ```

3. **Resolve Conflicts**:
   ```
   Input: High-priority client call conflicts with internal 1:1
   Output: {
     resolution: "reschedule_internal",
     reasoning: "User reschedules internal for clients 85% of time",
     confidence: 0.85
   }
   ```

4. **Generate Explanations**:
   ```
   Input: Recommended slot
   Output: "Tuesday 2pm is optimal because:
            - All attendees available
            - Matches your afternoon preference
            - No timezone conflicts
            - 15-min buffer before next meeting"
   ```

**Model**: GPT-4 (configurable)

**File**: `agents/openai_integration.py`

### 4. Multi-Agent Coordinator

**Purpose**: Facilitate negotiation without accessing private data

**Protocol**:
1. Generate candidate time windows
2. Request availability signals from each agent
3. Find consensus (all agents available)
4. Handle edge cases
5. Rank and explain recommendations
6. Escalate if needed

**Edge Cases Handled**:
- Timezone conflicts
- All attendees busy
- Conflicting priorities
- Last-minute requests
- Recurring meeting conflicts
- Vacation/holiday conflicts
- Working hours violations
- Back-to-back meeting limits
- Duration constraints
- Availability gaps

**File**: `agents/multi_agent_coordinator.py`

### 5. Edge Case Handler

**Purpose**: Comprehensive edge case handling

**Categories**:
1. **Timezone**: International teams, fairness
2. **Availability**: All busy, gaps, conflicts
3. **Priority**: Conflicting high-priority meetings
4. **Timing**: Last-minute, recurring, holidays
5. **Constraints**: Working hours, back-to-back, duration

**File**: `agents/edge_case_handler.py`

## Data Flow

### Scheduling Request Flow

```
1. User Request
   "Schedule Q2 planning with Sarah, Marcus, Priya"
   
2. OpenAI Parsing
   → Extract: attendees, duration, priority, type
   
3. Coordinator Generates Candidates
   → 50 potential time windows
   
4. Personal Agents Analyze (Parallel)
   Alex's Agent:
     ✓ Check private calendar
     ✓ ML predicts acceptance: 0.92
     ✓ Evaluate preferences
     ✓ Return signal: "available, confidence: 0.92"
   
   Sarah's Agent:
     ✓ Check private calendar
     ✓ ML predicts acceptance: 0.88
     ✓ Evaluate preferences
     ✓ Return signal: "available, confidence: 0.88"
   
   Marcus's Agent:
     ✓ Check private calendar
     ✓ ML predicts acceptance: 0.75
     ✓ Evaluate preferences
     ✓ Return signal: "flexible, confidence: 0.75"
   
5. Coordinator Finds Consensus
   → Slot: Tuesday 2pm
   → All agents: available
   → Avg confidence: 0.85
   
6. Edge Case Handling
   ✓ Timezone check: Fair for all
   ✓ Working hours: Within bounds
   ✓ Back-to-back: No issues
   
7. OpenAI Explanation
   → "Tuesday 2pm is optimal because..."
   
8. User Sees Recommendation
   → "Best time: Tuesday 2pm (85% confidence)"
   → [Schedule] [See Alternatives]
```

## Privacy Guarantees

### What Agents Share
✅ Availability status: "available" | "busy" | "flexible"
✅ Confidence score: 0.0 - 1.0
✅ Flexibility score: 0.0 - 1.0
✅ Priority override: "can_reschedule_internal"

### What Agents NEVER Share
❌ Calendar event titles
❌ Meeting descriptions
❌ Attendee lists
❌ Location details
❌ Full calendar view
❌ Personal patterns

## Learning & Improvement

### Continuous Learning

```python
# After each scheduling decision
feedback = {
    "proposed_slot": {...},
    "user_accepted": True/False,
    "user_choice": {...},
    "reason": "..."
}

# Update ML model
personal_agent.behavior_model.update_from_feedback(feedback)

# Update OpenAI context
personal_agent.ai_assistant.update_context(feedback)
```

### Metrics Tracked
- Acceptance rate by time/day/type
- Reschedule patterns
- Response time
- Preference drift over time
- Model accuracy

## Scalability

### Per-User Agents
- Each user has isolated agent
- Agents can run in parallel
- No shared state (except coordination)
- Scales to 1000s of users

### Optimization
- Cache ML predictions
- Batch OpenAI calls
- Async agent execution
- Connection pooling

## Configuration

```python
# .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
CONFIDENCE_THRESHOLD=0.6  # Escalate below this
MAX_NEGOTIATION_ROUNDS=3
LOOKBACK_DAYS=90  # Historical data for ML
```

## Future Enhancements

### Phase 2
- [ ] Real-time learning (online ML)
- [ ] Federated learning across users
- [ ] Advanced NLP (intent detection)
- [ ] Multi-modal input (voice, email)

### Phase 3
- [ ] Predictive scheduling
- [ ] Proactive suggestions
- [ ] Team-wide optimization
- [ ] Integration with productivity tools

## Why This Is Innovative

1. **Privacy-Preserving**: No centralized calendar access
2. **Truly Multi-Agent**: Each agent is independent
3. **ML-Powered**: Real learning, not rules
4. **Explainable**: AI explains every decision
5. **Scalable**: Distributed architecture
6. **Production-Ready**: Handles all edge cases

## Technical Stack

- **Orchestration**: LangGraph (state-based workflows)
- **ML**: Scikit-learn, NumPy, Pandas
- **NLP**: OpenAI GPT-4, LangChain
- **Backend**: FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Async**: Python asyncio

## Deployment

See `DEPLOYMENT.md` for production deployment guide.

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI key
export OPENAI_API_KEY=sk-...

# Initialize database
python cli.py init
python cli.py seed

# Run backend
uvicorn main:app --reload --port 8000
```

## Testing

```bash
# Test personal agent
python -m pytest tests/test_personal_agent.py

# Test ML model
python -m pytest tests/test_ml_model.py

# Test coordination
python -m pytest tests/test_coordinator.py
```

## License

MIT

## Contributors

Built as a portfolio project demonstrating:
- Multi-agent AI systems
- Privacy-preserving ML
- Production-ready architecture
- Comprehensive edge case handling
