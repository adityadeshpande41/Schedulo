# LangGraph Orchestration Architecture

## Overview

We use **LangGraph** for state-based multi-agent orchestration. LangGraph provides:
- **State management** across agents
- **Graph-based workflows** with conditional routing
- **Checkpointing** for fault tolerance
- **Human-in-the-loop** for escalation
- **Visualization** of agent workflows

## Workflow Graph

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Parse Request   │ ← OpenAI parses natural language
│   (OpenAI)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Personal Agents │ ← Each agent analyzes independently
│   (Parallel)    │   (Privacy-preserving)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Coordinate     │ ← Find consensus across agents
│                 │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Edge Cases     │ ← Handle timezone, conflicts, etc.
│                 │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Rank & Explain │ ← OpenAI generates explanations
│   (OpenAI)      │
└──────┬──────────┘
       │
       ▼
    ┌──┴──┐
    │ ??? │ Should escalate?
    └──┬──┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌────┐  ┌────────┐
│ESC │  │COMPLETE│
└────┘  └────────┘
   │       │
   └───┬───┘
       │
       ▼
    ┌─────┐
    │ END │
    └─────┘
```

## State Flow

### SchedulingState (Shared State)

```python
class SchedulingState(TypedDict):
    # Input
    request: str                    # "Schedule with Sarah next week"
    attendee_ids: list[str]         # ["u1", "u2"]
    duration: int                   # 30
    meeting_context: dict           # {type, priority}
    
    # Agent Outputs
    parsed_request: dict            # Parsed by OpenAI
    personal_agent_signals: dict    # user_id -> signals
    consensus_slots: list[dict]     # Agreed-upon slots
    edge_cases_handled: list[str]   # ["timezone_conflicts"]
    ranked_recommendations: list    # Final ranked list
    
    # Decision
    confidence: float               # 0.85
    escalation_needed: bool         # False
    escalation_reason: str          # ""
    
    # Workflow
    messages: list[BaseMessage]     # Conversation history
    next_step: str                  # Current node
    iteration: int                  # Workflow iteration
```

## Node Descriptions

### 1. Parse Request Node
**Purpose**: Parse natural language using OpenAI

**Input**:
```python
state["request"] = "Schedule 30-min sync with Sarah next week, afternoon"
```

**Output**:
```python
state["parsed_request"] = {
    "attendees": ["Sarah"],
    "duration": 30,
    "time_preference": "afternoon",
    "date_range": "next_week"
}
```

**Agent**: OpenAI GPT-4

---

### 2. Personal Agents Node
**Purpose**: Execute personal agents in parallel

**Input**:
```python
state["attendee_ids"] = ["u1", "u2", "u3"]
state["parsed_request"] = {...}
```

**Process**:
```python
for user_id in attendee_ids:
    agent = PersonalAgent(user_id)
    signals = agent.get_availability_signals()
    # Privacy: Only shares "available/busy/flexible"
```

**Output**:
```python
state["personal_agent_signals"] = {
    "u1": [{"status": "available", "confidence": 0.92}],
    "u2": [{"status": "available", "confidence": 0.88}],
    "u3": [{"status": "flexible", "confidence": 0.75}]
}
```

---

### 3. Coordinate Node
**Purpose**: Find consensus across agents

**Input**:
```python
state["personal_agent_signals"] = {...}
```

**Process**:
```python
coordinator = MultiAgentCoordinator()
consensus = coordinator.find_consensus(signals)
```

**Output**:
```python
state["consensus_slots"] = [
    {
        "window": {"start": "2024-03-12 14:00", "end": "2024-03-12 14:30"},
        "confidence": 0.85,
        "all_available": True
    }
]
```

---

### 4. Edge Cases Node
**Purpose**: Handle edge cases

**Input**:
```python
state["consensus_slots"] = [...]
```

**Process**:
```python
handler = EdgeCaseHandler()
# Check timezone conflicts
# Check working hours
# Check back-to-back limits
# etc.
```

**Output**:
```python
state["edge_cases_handled"] = ["timezone_conflicts", "working_hours"]
state["consensus_slots"] = [...]  # Filtered/adjusted
```

---

### 5. Rank Node
**Purpose**: Rank slots and generate explanations

**Input**:
```python
state["consensus_slots"] = [...]
```

**Process**:
```python
# Sort by confidence
ranked = sorted(slots, key=lambda s: s["confidence"], reverse=True)

# Generate explanations with OpenAI
for slot in ranked[:3]:
    explanation = openai.generate_explanation(slot)
```

**Output**:
```python
state["ranked_recommendations"] = [
    {
        "rank": 1,
        "confidence": 0.92,
        "explanation": "Tuesday 2pm is optimal because...",
        "recommended": True
    }
]
```

---

### 6a. Escalate Node
**Purpose**: Escalate to human

**Triggered When**:
- No recommendations found
- Confidence < 60%
- Requires approval
- Critical edge cases

**Output**:
```python
state["escalation_needed"] = True
state["escalation_reason"] = "Low confidence (55%)"
```

---

### 6b. Complete Node
**Purpose**: Complete successfully

**Output**:
```python
state["escalation_needed"] = False
# Recommendations ready for user
```

## Conditional Routing

### should_escalate()

```python
def should_escalate(state: SchedulingState) -> Literal["escalate", "complete"]:
    # No recommendations
    if not state["ranked_recommendations"]:
        return "escalate"
    
    top_slot = state["ranked_recommendations"][0]
    
    # Low confidence
    if top_slot["confidence"] < 0.6:
        return "escalate"
    
    # Requires approval
    if top_slot.get("requires_approval"):
        return "escalate"
    
    return "complete"
```

## Checkpointing

LangGraph supports checkpointing for fault tolerance:

```python
# Save state at each node
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Resume from checkpoint
config = {"configurable": {"thread_id": "session_123"}}
result = await graph.ainvoke(state, config)
```

## Human-in-the-Loop

When escalation is needed:

```python
# Workflow pauses at escalate node
state["escalation_needed"] = True

# Human reviews and provides input
human_decision = await get_human_input(state)

# Resume workflow with human input
state["human_override"] = human_decision
result = await graph.ainvoke(state, config)
```

## Advantages of LangGraph

### 1. State Management
- Shared state across all agents
- Type-safe with TypedDict
- Automatic state updates

### 2. Conditional Routing
- Dynamic workflow based on conditions
- If/else logic in graph
- Multiple exit paths

### 3. Fault Tolerance
- Checkpointing at each node
- Resume from failures
- Retry logic

### 4. Observability
- Track state changes
- View message history
- Debug workflow

### 5. Scalability
- Parallel agent execution
- Async/await support
- Efficient state passing

## Comparison: Before vs After

### Before (Manual Orchestration)
```python
# Manual coordination
result1 = await agent1.execute()
result2 = await agent2.execute()
result3 = await agent3.execute()

# Manual state management
state = {}
state["result1"] = result1
state["result2"] = result2

# Manual conditional logic
if result1.confidence < 0.6:
    escalate()
else:
    complete()
```

### After (LangGraph)
```python
# Automatic orchestration
orchestrator = LangGraphOrchestrator()
result = await orchestrator.execute(request)

# Automatic state management
# Automatic conditional routing
# Automatic checkpointing
```

## Usage Example

```python
from agents.langgraph_orchestrator import LangGraphOrchestrator

# Initialize
orchestrator = LangGraphOrchestrator()

# Execute workflow
result = await orchestrator.execute(
    request="Schedule Q2 planning with Sarah, Marcus, Priya",
    attendee_ids=["u1", "u2", "u3", "u4"],
    duration=60,
    meeting_context={"type": "team_sync", "priority": "high"}
)

# Check result
if result["escalation_needed"]:
    print(f"Escalation: {result['escalation_reason']}")
    # Show to human for decision
else:
    print(f"Recommendations: {result['ranked_recommendations']}")
    # Show to user
```

## Visualization

```python
# Visualize the graph
orchestrator.visualize_graph("workflow.png")

# Get graph structure
structure = orchestrator.get_graph_structure()
print(structure)
```

## Configuration

```python
# .env
LANGGRAPH_CHECKPOINT_ENABLED=true
LANGGRAPH_MAX_ITERATIONS=10
LANGGRAPH_TIMEOUT=30
```

## Future Enhancements

### Phase 2
- [ ] Streaming responses (real-time updates)
- [ ] Multi-turn conversations
- [ ] Dynamic graph modification
- [ ] A/B testing different workflows

### Phase 3
- [ ] Distributed execution
- [ ] Graph versioning
- [ ] Performance monitoring
- [ ] Workflow analytics

## Resources

- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- Examples: https://github.com/langchain-ai/langgraph/tree/main/examples
- Tutorials: https://langchain-ai.github.io/langgraph/tutorials/

## Summary

LangGraph provides:
✅ **State management** - Shared state across agents
✅ **Conditional routing** - Dynamic workflow
✅ **Checkpointing** - Fault tolerance
✅ **Human-in-the-loop** - Escalation support
✅ **Observability** - Track workflow execution
✅ **Scalability** - Parallel execution

This makes our multi-agent system **production-ready** and **maintainable**! 🚀
