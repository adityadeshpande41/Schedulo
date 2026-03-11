# Schedulo System Flow

Complete end-to-end flow of the AI scheduling system.

## High-Level Flow

```
┌─────────────┐
│   User      │
│  (Frontend) │
└──────┬──────┘
       │ POST /api/schedule/request
       │ {title, attendees, duration}
       ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                      │
│                 (api/routes/schedule.py)                │
└──────┬──────────────────────────────────────────────────┘
       │
       │ Calls LangGraph Orchestrator
       ▼
┌─────────────────────────────────────────────────────────┐
│              LangGraph Orchestrator                     │
│         (agents/langgraph_orchestrator.py)              │
│                                                         │
│  State-based workflow with 7 nodes:                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Parse Request (OpenAI)                       │   │
│  │    "Schedule sync next week" → structured data  │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 2. Personal Agents (Parallel)                   │   │
│  │    Execute one agent per attendee               │   │
│  └─────────────────────────────────────────────────┘   │
│         │              │              │                 │
│         ▼              ▼              ▼                 │
│    ┌────────┐    ┌────────┐    ┌────────┐             │
│    │Agent u1│    │Agent u2│    │Agent u3│             │
│    └────────┘    └────────┘    └────────┘             │
│         │              │              │                 │
│         └──────────────┴──────────────┘                │
│                        │                                │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 3. Coordinate (Multi-Agent)                     │   │
│  │    Find consensus across agents                 │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 4. Edge Cases (Handler)                         │   │
│  │    Validate timezone, hours, conflicts          │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 5. Rank (Sort + OpenAI Explanations)            │   │
│  │    Sort by confidence, generate explanations    │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 6. Decision (Conditional Routing)               │   │
│  │    Confidence > 60%? → Complete : Escalate      │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│              ┌─────────┴─────────┐                      │
│              ▼                   ▼                      │
│         ┌─────────┐         ┌─────────┐                │
│         │Escalate │         │Complete │                │
│         └─────────┘         └─────────┘                │
│                                                         │
└──────┬──────────────────────────────────────────────────┘
       │
       │ Returns final state
       ▼
┌─────────────────────────────────────────────────────────┐
│                  Schedule Service                       │
│            (services/schedule_service.py)               │
│                                                         │
│  Formats response:                                      │
│  - Convert state to API response                        │
│  - Format time slots                                    │
│  - Add metadata                                         │
└──────┬──────────────────────────────────────────────────┘
       │
       │ JSON response
       ▼
┌─────────────────────────────────────────────────────────┐
│                      Frontend                           │
│                  (React + React Query)                  │
│                                                         │
│  Displays:                                              │
│  - Recommended time slots                               │
│  - Confidence scores                                    │
│  - AI explanations                                      │
│  - Escalation notices                                   │
└─────────────────────────────────────────────────────────┘
```

## Personal Agent Deep Dive

Each personal agent executes independently:

```
┌─────────────────────────────────────────────────────────┐
│              Personal Agent (e.g., Alex's)              │
│            (agents/personal_agent.py)                   │
│                                                         │
│  Step 1: Load Private Data                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ UserDataService.get_user_calendar(user_id)      │   │
│  │ UserDataService.get_user_preferences(user_id)   │   │
│  │ UserDataService.get_historical_meetings(...)    │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  Step 2: Train ML Model                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ BehaviorLearningModel.train(historical_data)    │   │
│  │                                                 │   │
│  │ Learns:                                         │   │
│  │ - Time of day preferences                       │   │
│  │ - Day of week patterns                          │   │
│  │ - Meeting type preferences                      │   │
│  │ - Reschedule patterns                           │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  Step 3: Check Availability                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │ For each time window:                           │   │
│  │   1. Check calendar (is_busy?)                  │   │
│  │   2. ML predict acceptance (0.0-1.0)            │   │
│  │   3. Evaluate preferences (score)               │   │
│  │   4. Calculate flexibility (0.0-1.0)            │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  Step 4: Generate Signals                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │ AvailabilitySignal {                            │   │
│  │   status: "available" | "busy" | "flexible"     │   │
│  │   confidence: 0.92                              │   │
│  │   flexibility: 0.7                              │   │
│  │   priority_override: "can_reschedule_internal"  │   │
│  │ }                                               │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  Step 5: Return Result                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │ AgentResult {                                   │   │
│  │   data: {                                       │   │
│  │     user_id: "u1",                              │   │
│  │     availability_signals: [...]                 │   │
│  │   },                                            │   │
│  │   confidence: 0.92                              │   │
│  │ }                                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  PRIVACY: Never shares calendar details!                │
└─────────────────────────────────────────────────────────┘
```

## ML Behavior Model Flow

```
┌─────────────────────────────────────────────────────────┐
│              ML Behavior Model                          │
│         (agents/ml_behavior_model.py)                   │
│                                                         │
│  Training Phase:                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Input: Historical meetings (90 days)            │   │
│  │                                                 │   │
│  │ For each meeting:                               │   │
│  │   - start_time (datetime)                       │   │
│  │   - duration (int)                              │   │
│  │   - type (string)                               │   │
│  │   - was_accepted (bool)                         │   │
│  │   - was_rescheduled (bool)                      │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Learn Patterns:                                 │   │
│  │                                                 │   │
│  │ time_preferences = {                            │   │
│  │   9: 0.65,   # 65% acceptance at 9am            │   │
│  │   10: 0.78,  # 78% acceptance at 10am           │   │
│  │   14: 0.92,  # 92% acceptance at 2pm ⭐         │   │
│  │   16: 0.71   # 71% acceptance at 4pm            │   │
│  │ }                                               │   │
│  │                                                 │   │
│  │ day_preferences = {                             │   │
│  │   0: 0.75,   # Monday: 75%                      │   │
│  │   1: 0.88,   # Tuesday: 88% ⭐                  │   │
│  │   2: 0.82,   # Wednesday: 82%                   │   │
│  │   3: 0.85,   # Thursday: 85% ⭐                 │   │
│  │   4: 0.45    # Friday: 45%                      │   │
│  │ }                                               │   │
│  │                                                 │   │
│  │ reschedule_patterns = {                         │   │
│  │   "one_on_one": 0.40,      # 40% reschedule    │   │
│  │   "team_sync": 0.25,       # 25% reschedule    │   │
│  │   "client_call": 0.05      # 5% reschedule     │   │
│  │ }                                               │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  Prediction Phase:                                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Input: New time slot                            │   │
│  │   - Tuesday, 2pm, 30 min, team_sync             │   │
│  │                                                 │   │
│  │ Calculate:                                      │   │
│  │   base_prob = 0.5                               │   │
│  │   + time_factor (0.92 for 2pm)                  │   │
│  │   + day_factor (0.88 for Tuesday)               │   │
│  │   + type_factor (0.75 for team_sync)            │   │
│  │   = 0.92 acceptance probability ⭐              │   │
│  └─────────────────────────────────────────────────┘   │
│                        │                                │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Output: Prediction                              │   │
│  │   acceptance_prob: 0.92                         │   │
│  │   reschedule_prob: 0.25                         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## OpenAI Integration Flow

```
┌─────────────────────────────────────────────────────────┐
│              OpenAI Integration                         │
│         (agents/openai_integration.py)                  │
│                                                         │
│  Use Case 1: Parse Natural Language                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Input: "Schedule 30-min sync with Sarah next    │   │
│  │         week, preferably afternoon"             │   │
│  │                                                 │   │
│  │ OpenAI GPT-4:                                   │   │
│  │   System: "Parse scheduling request"            │   │
│  │   User: <request>                               │   │
│  │   Response format: JSON                         │   │
│  │                                                 │   │
│  │ Output: {                                       │   │
│  │   attendees: ["Sarah"],                         │   │
│  │   duration: 30,                                 │   │
│  │   time_preference: "afternoon",                 │   │
│  │   date_range: "next_week",                      │   │
│  │   priority: "medium",                           │   │
│  │   type: "team_sync"                             │   │
│  │ }                                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Use Case 2: Generate Explanation                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Input: Recommendation + Context                 │   │
│  │                                                 │   │
│  │ OpenAI GPT-4:                                   │   │
│  │   System: "Explain scheduling recommendation"   │   │
│  │   User: <recommendation details>                │   │
│  │                                                 │   │
│  │ Output: "I recommend Tuesday 2pm because:       │   │
│  │   - All attendees are available                 │   │
│  │   - You typically prefer afternoon meetings     │   │
│  │     (85% acceptance rate)                       │   │
│  │   - No conflicts with high-priority meetings    │   │
│  │   - Respects everyone's working hours"          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Use Case 3: Resolve Conflict                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Input: Conflict details + User patterns         │   │
│  │                                                 │   │
│  │ OpenAI GPT-4:                                   │   │
│  │   System: "Resolve scheduling conflict"         │   │
│  │   User: <conflict + patterns>                   │   │
│  │   Response format: JSON                         │   │
│  │                                                 │   │
│  │ Output: {                                       │   │
│  │   resolution: "reschedule_existing",            │   │
│  │   reasoning: "User typically reschedules        │   │
│  │               internal meetings for clients",   │   │
│  │   confidence: 0.85,                             │   │
│  │   escalate_to_human: false                      │   │
│  │ }                                               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Database Access Flow

```
┌─────────────────────────────────────────────────────────┐
│              User Data Service                          │
│         (services/user_data_service.py)                 │
│                                                         │
│  PRIVACY: Each method only returns data for ONE user    │
│                                                         │
│  Method 1: get_user_calendar(user_id, start, end)      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SELECT * FROM calendar_events                   │   │
│  │ WHERE user_id = 'u1'                            │   │
│  │   AND start_time >= '2026-03-10'                │   │
│  │   AND end_time <= '2026-04-10'                  │   │
│  │                                                 │   │
│  │ Returns: [                                      │   │
│  │   {id, start_time, end_time, is_busy, ...}      │   │
│  │ ]                                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Method 2: get_user_preferences(user_id)               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SELECT * FROM user_preferences                  │   │
│  │ WHERE user_id = 'u1'                            │   │
│  │                                                 │   │
│  │ Returns: {                                      │   │
│  │   work_hours_start: "09:00",                    │   │
│  │   work_hours_end: "17:00",                      │   │
│  │   timezone: "UTC",                              │   │
│  │   preferred_meeting_duration: 30,               │   │
│  │   ...                                           │   │
│  │ }                                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Method 3: get_historical_meetings(user_id, days)      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SELECT * FROM historical_meetings               │   │
│  │ WHERE user_id = 'u1'                            │   │
│  │   AND meeting_date >= NOW() - INTERVAL '90 days'│   │
│  │                                                 │   │
│  │ Returns: [                                      │   │
│  │   {meeting_id, start_time, was_accepted, ...}   │   │
│  │ ]                                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Method 4: check_availability(user_id, start, end)     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SELECT COUNT(*) FROM calendar_events            │   │
│  │ WHERE user_id = 'u1'                            │   │
│  │   AND is_busy = true                            │   │
│  │   AND (overlaps with time window)               │   │
│  │                                                 │   │
│  │ Returns: true (available) | false (busy)        │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Complete Example: Schedule Q2 Planning

```
User Request:
  "Schedule Q2 Planning with Sarah and Marcus, 60 minutes, high priority"

┌─────────────────────────────────────────────────────────┐
│ Step 1: API receives request                            │
│   POST /api/schedule/request                            │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: LangGraph - Parse Request                       │
│   OpenAI: "Schedule Q2 Planning..." → {                 │
│     attendees: ["Sarah", "Marcus"],                     │
│     duration: 60,                                       │
│     priority: "high",                                   │
│     type: "team_sync"                                   │
│   }                                                     │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: LangGraph - Personal Agents (Parallel)          │
│                                                         │
│   Sarah's Agent:                                        │
│   ├─ Load calendar: 5 events next week                  │
│   ├─ Load preferences: prefers afternoon                │
│   ├─ Train ML: 50 historical meetings                   │
│   ├─ Check Tuesday 2pm: Available                       │
│   ├─ ML predict: 88% acceptance                         │
│   └─ Signal: "available", confidence: 0.88              │
│                                                         │
│   Marcus's Agent:                                       │
│   ├─ Load calendar: 8 events next week                  │
│   ├─ Load preferences: prefers morning                  │
│   ├─ Train ML: 45 historical meetings                   │
│   ├─ Check Tuesday 2pm: Busy (internal 1:1)             │
│   ├─ ML predict reschedule: 75% (high priority)         │
│   └─ Signal: "flexible", confidence: 0.75               │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: LangGraph - Coordinate                          │
│   Consensus slots:                                      │
│   - Tuesday 2pm: Sarah available, Marcus flexible       │
│   - Wednesday 10am: Both available                      │
│   - Thursday 3pm: Both available                        │
│                                                         │
│   Ranked by confidence:                                 │
│   1. Wednesday 10am (0.90)                              │
│   2. Thursday 3pm (0.87)                                │
│   3. Tuesday 2pm (0.82)                                 │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: LangGraph - Edge Cases                          │
│   ✓ Timezone: All UTC, fair                             │
│   ✓ Working hours: All within 9-5                       │
│   ✓ Back-to-back: No issues                             │
│   ✓ Duration: Fits in all slots                         │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 6: LangGraph - Rank & Explain                      │
│   OpenAI generates explanations:                        │
│                                                         │
│   Slot 1 (Wednesday 10am):                              │
│   "I recommend Wednesday 10am because both attendees    │
│    are available, it's within everyone's preferred      │
│    hours, and there are no conflicts."                  │
│                                                         │
│   Slot 2 (Thursday 3pm):                                │
│   "Thursday 3pm works well as an alternative..."        │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 7: LangGraph - Decision                            │
│   Confidence: 0.90 (> 0.60 threshold)                   │
│   Decision: COMPLETE ✓                                  │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 8: API returns response                            │
│   {                                                     │
│     status: "completed",                                │
│     recommended_slots: [                                │
│       {                                                 │
│         start_time: "2026-03-12T10:00:00Z",             │
│         end_time: "2026-03-12T11:00:00Z",               │
│         confidence: 0.90,                               │
│         explanation: "I recommend Wednesday 10am...",   │
│         recommended: true                               │
│       },                                                │
│       ...                                               │
│     ],                                                  │
│     confidence: 0.90                                    │
│   }                                                     │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 9: Frontend displays results                       │
│   ✅ Best time: Wednesday 10am (90% confidence)         │
│   📝 Explanation: "I recommend Wednesday 10am..."       │
│   🔄 Alternatives: Thursday 3pm, Tuesday 2pm            │
│   [Schedule Meeting] [See More Options]                 │
└─────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **Privacy-Preserving**: Each agent only accesses one user's data
2. **ML-Powered**: Real learning from historical patterns
3. **AI-Enhanced**: OpenAI for NLP and reasoning
4. **Orchestrated**: LangGraph manages complex workflow
5. **Scalable**: Parallel agent execution
6. **Intelligent**: Handles 10+ edge cases
7. **Explainable**: Human-readable explanations
8. **Adaptive**: Escalates when uncertain

---

**The system is designed to be both powerful and transparent** 🚀
