# Schedulo — AI-Powered Multi-Agent Scheduling Frontend

## Overview
Schedulo is a premium frontend demo for an AI-powered multi-agent meeting scheduler. The frontend uses mock data and is designed to later connect to a Python FastAPI backend.

## Tech Stack
- React + TypeScript
- Tailwind CSS
- Framer Motion (animations)
- shadcn/ui (component library)
- wouter (routing)
- lucide-react (icons)

## Architecture
Frontend-only with mock data layer (`client/src/data/mock.ts`) designed for future API replacement.

### Directory Structure
```
client/src/
├── components/
│   ├── schedulo/       # Custom Schedulo components (assistant, navbar, theme toggle, shiny text)
│   └── ui/             # shadcn/ui components
├── data/               # Mock data and mock API service
├── hooks/              # Custom hooks (theme)
├── lib/                # Utilities (cn, queryClient)
├── pages/              # Page components
│   ├── landing.tsx     # Marketing landing page
│   ├── dashboard.tsx   # Main app dashboard
│   ├── agent-flow.tsx  # Agent architecture explainer
│   ├── decision.tsx    # AI Decision Cockpit
│   └── not-found.tsx   # 404 page
└── types/              # TypeScript interfaces (schedulo.ts)
```

### Pages
1. **Landing** (`/`) — Marketing page with hero, capabilities, agent workflow, CTA
2. **Dashboard** (`/dashboard`) — Upcoming meetings, schedule form, AI agent panel, preferences
3. **Agent Flow** (`/agents`) — Multi-agent architecture visualization with info flow
4. **AI Decision Cockpit** (`/decision`) — Meeting recommendation with confidence, tradeoffs, insights

### Key Components
- `ScheduloAssistant` — Animated SVG mascot with floating, blinking, glowing effects
- `ShinyText` — Gradient animated text for headings
- `ThemeToggle` — Animated dark/light mode toggle
- `Navbar` — Responsive navigation with active state indicators

### Theme
- Dark mode supported via `useTheme` hook and `.dark` class on `<html>`
- Primary color: Blue (217, 91%, 60%)
- Font: Inter (sans), Lora (serif), JetBrains Mono (mono)

### Future Backend Integration
Types in `client/src/types/schedulo.ts` map to planned FastAPI endpoints:
- `/schedule/request` → `ScheduleRequest`
- `/slots/recommendations` → `TimeSlot[]`
- `/agents/activity` → `AgentActivity[]`
- `/preferences/:id` → `UserPreference[]`
- `/meetings/:id/decision` → `DecisionExplanation`

Mock API service in `client/src/data/mock.ts` can be swapped for real API calls.
