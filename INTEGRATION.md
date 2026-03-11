# Frontend-Backend Integration Guide

## Overview

The Schedulo frontend is now connected to the FastAPI backend. All mock data has been replaced with real API calls using React Query for efficient data fetching and caching.

## Architecture

```
Frontend (React + Vite)  ←→  Backend (FastAPI + Python)
     Port 5000                    Port 8000
```

## Setup Instructions

### 1. Backend Setup

```bash
cd python_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if needed

# Start backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Install dependencies (if not already done)
npm install

# Configure environment
# .env file already created with:
# VITE_API_URL=http://localhost:8000/api
# VITE_DEFAULT_USER_ID=u1

# Start frontend
npm run dev:frontend
```

Frontend will be available at: `http://localhost:5000`

### 3. Run Both Together

```bash
# Terminal 1: Backend
cd python_backend && ./run.sh

# Terminal 2: Frontend
npm run dev:frontend
```

## API Integration

### API Client (`client/src/lib/api.ts`)

Centralized API client handling all HTTP requests:

```typescript
import { apiClient } from "@/lib/api";

// Schedule a meeting
const result = await apiClient.createScheduleRequest(request);

// Get upcoming meetings
const meetings = await apiClient.getUpcomingMeetings(userId, 7);

// Get agent activity
const activities = await apiClient.getAgentActivity();
```

### React Query Hooks

Custom hooks for each API domain:

**Meetings** (`client/src/hooks/use-meetings.ts`)
- `useUpcomingMeetings(userId, days)` - Get upcoming meetings
- `useMeeting(meetingId)` - Get single meeting
- `useMeetingDecision(meetingId)` - Get AI decision explanation
- `useUpdateMeetingStatus()` - Update meeting status
- `useCancelMeeting()` - Cancel meeting

**Schedule** (`client/src/hooks/use-schedule.ts`)
- `useCreateScheduleRequest()` - Create scheduling request
- `useRecommendedSlots()` - Get recommended time slots
- `useConfirmTimeSlot()` - Confirm selected slot

**Agents** (`client/src/hooks/use-agents.ts`)
- `useAgentActivity()` - Get agent activity (polls every 3s)
- `useAgentInfo()` - Get agent capabilities
- `useAgentWebSocket()` - Real-time agent updates via WebSocket

**Preferences** (`client/src/hooks/use-preferences.ts`)
- `useUserPreferences(userId)` - Get user preferences
- `useUpdatePreference()` - Update preference
- `useCreatePreference()` - Create new preference

## Updated Pages

### Dashboard (`client/src/pages/dashboard.tsx`)
- ✅ Fetches real meetings from backend
- ✅ Fetches real agent activity
- ✅ Fetches real user preferences
- ✅ Creates schedule requests via API
- ✅ Loading states with React Query

### Agent Flow (`client/src/pages/agent-flow.tsx`)
- ✅ Fetches agent info from backend
- ✅ Loading state while fetching

### Decision Page (`client/src/pages/decision.tsx`)
- ✅ Fetches meeting decision from backend
- ✅ Shows AI explanation and insights

## Features

### Automatic Caching
React Query automatically caches API responses:
- Meetings: 2 minutes
- Preferences: 5 minutes
- Agent info: Infinite (doesn't change)

### Automatic Refetching
Queries automatically refetch on:
- Window focus
- Network reconnection
- Manual invalidation after mutations

### Optimistic Updates
Mutations invalidate related queries:
```typescript
// After creating a schedule request
queryClient.invalidateQueries({ queryKey: ["meetings"] });
queryClient.invalidateQueries({ queryKey: ["agent-activity"] });
```

### Real-time Updates
WebSocket connection for live agent activity:
```typescript
const { activities, isConnected } = useAgentWebSocket();
```

### Error Handling
All API calls include error handling:
```typescript
try {
  const result = await createSchedule.mutateAsync(request);
  setSlots(result.recommended_slots);
} catch (error) {
  console.error("Error getting recommendations:", error);
}
```

## Environment Variables

### Frontend (`.env`)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_DEFAULT_USER_ID=u1
```

### Backend (`python_backend/.env`)
```bash
API_V1_STR=/api
PROJECT_NAME=Schedulo
DATABASE_URL=postgresql://user:password@localhost/schedulo
AGENT_TIMEOUT=30
LOOKBACK_DAYS=90
CORS_ORIGINS=http://localhost:5000,http://localhost:5173
```

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Create Schedule Request
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

### 3. Get Upcoming Meetings
```bash
curl "http://localhost:8000/api/meetings/upcoming?user_id=u1&days=7"
```

### 4. Get Agent Activity
```bash
curl http://localhost:8000/api/agents/activity
```

## Next Steps

1. **Database Integration**
   - Replace mock data in services with real database queries
   - Implement SQLAlchemy models
   - Add migrations

2. **Authentication**
   - Add JWT token authentication
   - Protect API endpoints
   - Add user registration/login

3. **Calendar Integration**
   - Google Calendar OAuth
   - Outlook Calendar OAuth
   - Sync calendar events

4. **Real Agent Execution**
   - Connect agents to real calendar data
   - Implement historical data analysis
   - Add ML models for behavior prediction

5. **WebSocket Enhancements**
   - Broadcast agent status updates
   - Real-time collaboration features
   - Live meeting updates

## Troubleshooting

### CORS Errors
- Ensure backend CORS_ORIGINS includes frontend URL
- Check that backend is running on port 8000
- Verify frontend is using correct API_URL

### Connection Refused
- Ensure backend is running: `cd python_backend && uvicorn main:app --reload --port 8000`
- Check firewall settings
- Verify ports 5000 and 8000 are available

### 404 Errors
- Check API endpoint paths match between frontend and backend
- Verify API_V1_STR is set to `/api` in backend config
- Check FastAPI router prefixes

### Data Not Loading
- Open browser DevTools → Network tab
- Check for failed API requests
- Verify backend logs for errors
- Check React Query DevTools for query status

## Development Workflow

1. Start backend: `cd python_backend && ./run.sh`
2. Start frontend: `npm run dev:frontend`
3. Open browser: `http://localhost:5000`
4. Check API docs: `http://localhost:8000/docs`
5. Monitor logs in both terminals

## Production Deployment

### Backend
```bash
cd python_backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm run build
# Serve dist/public with your web server
```

Update environment variables for production URLs.
