import type {
  User,
  Meeting,
  TimeSlot,
  AgentActivity,
  UserPreference,
  DecisionExplanation,
  AgentInfo,
  ScheduleRequest,
  MockApiService,
} from "@/types/schedulo";

export const currentUser: User = {
  id: "u1",
  name: "Alex Rivera",
  email: "alex@schedulo.ai",
  role: "Product Manager",
  timezone: "America/New_York",
};

export const mockUsers: User[] = [
  currentUser,
  { id: "u2", name: "Sarah Chen", email: "sarah@schedulo.ai", role: "Engineering Lead", timezone: "America/Los_Angeles" },
  { id: "u3", name: "Marcus Johnson", email: "marcus@schedulo.ai", role: "Designer", timezone: "America/Chicago" },
  { id: "u4", name: "Priya Patel", email: "priya@schedulo.ai", role: "Data Scientist", timezone: "Asia/Kolkata" },
  { id: "u5", name: "James Kim", email: "james@client.com", role: "VP of Sales (Client)", timezone: "America/New_York" },
];

export const mockMeetings: Meeting[] = [
  {
    id: "m1",
    title: "Sprint Planning",
    type: "team_sync",
    startTime: "2026-03-11T10:00:00",
    endTime: "2026-03-11T11:00:00",
    duration: 60,
    attendees: [
      { id: "u1", name: "Alex Rivera", email: "alex@schedulo.ai", role: "Product Manager", availability: "available", responseStatus: "accepted" },
      { id: "u2", name: "Sarah Chen", email: "sarah@schedulo.ai", role: "Engineering Lead", availability: "available", responseStatus: "accepted" },
      { id: "u3", name: "Marcus Johnson", email: "marcus@schedulo.ai", role: "Designer", availability: "available", responseStatus: "accepted" },
    ],
    status: "confirmed",
    priority: "high",
    location: "Virtual — Zoom",
    description: "Weekly sprint planning and backlog review",
  },
  {
    id: "m2",
    title: "Client Strategy Review",
    type: "client_call",
    startTime: "2026-03-11T14:00:00",
    endTime: "2026-03-11T15:00:00",
    duration: 60,
    attendees: [
      { id: "u1", name: "Alex Rivera", email: "alex@schedulo.ai", role: "Product Manager", availability: "available", responseStatus: "accepted" },
      { id: "u5", name: "James Kim", email: "james@client.com", role: "VP of Sales", availability: "soft_conflict", responseStatus: "tentative" },
    ],
    status: "pending",
    priority: "high",
    location: "Virtual — Google Meet",
    description: "Q2 strategy alignment with client team",
  },
  {
    id: "m3",
    title: "1:1 with Sarah",
    type: "one_on_one",
    startTime: "2026-03-12T09:30:00",
    endTime: "2026-03-12T10:00:00",
    duration: 30,
    attendees: [
      { id: "u1", name: "Alex Rivera", email: "alex@schedulo.ai", role: "Product Manager", availability: "available", responseStatus: "accepted" },
      { id: "u2", name: "Sarah Chen", email: "sarah@schedulo.ai", role: "Engineering Lead", availability: "available", responseStatus: "accepted" },
    ],
    status: "confirmed",
    priority: "medium",
    location: "Office — Room 4B",
  },
  {
    id: "m4",
    title: "Design Review",
    type: "workshop",
    startTime: "2026-03-12T15:00:00",
    endTime: "2026-03-12T16:30:00",
    duration: 90,
    attendees: [
      { id: "u1", name: "Alex Rivera", email: "alex@schedulo.ai", role: "Product Manager", availability: "available", responseStatus: "accepted" },
      { id: "u3", name: "Marcus Johnson", email: "marcus@schedulo.ai", role: "Designer", availability: "available", responseStatus: "accepted" },
      { id: "u4", name: "Priya Patel", email: "priya@schedulo.ai", role: "Data Scientist", availability: "soft_conflict", responseStatus: "tentative" },
    ],
    status: "confirmed",
    priority: "medium",
    location: "Virtual — Figma",
  },
  {
    id: "m5",
    title: "Morning Standup",
    type: "standup",
    startTime: "2026-03-13T09:00:00",
    endTime: "2026-03-13T09:15:00",
    duration: 15,
    attendees: [
      { id: "u1", name: "Alex Rivera", email: "alex@schedulo.ai", role: "Product Manager", availability: "available", responseStatus: "accepted" },
      { id: "u2", name: "Sarah Chen", email: "sarah@schedulo.ai", role: "Engineering Lead", availability: "available", responseStatus: "accepted" },
      { id: "u3", name: "Marcus Johnson", email: "marcus@schedulo.ai", role: "Designer", availability: "available", responseStatus: "accepted" },
      { id: "u4", name: "Priya Patel", email: "priya@schedulo.ai", role: "Data Scientist", availability: "available", responseStatus: "accepted" },
    ],
    status: "confirmed",
    priority: "low",
    location: "Virtual — Slack Huddle",
  },
];

export const mockSlots: TimeSlot[] = [
  {
    id: "s1",
    startTime: "2026-03-13T10:00:00",
    endTime: "2026-03-13T11:00:00",
    score: 97,
    confidence: 95,
    rank: 1,
    reasoning: "All attendees free. Optimal time based on preferences.",
    conflicts: [],
    attendeeAvailability: [
      { attendeeId: "u1", status: "available" },
      { attendeeId: "u2", status: "available" },
      { attendeeId: "u3", status: "available" },
    ],
    requiresApproval: false,
    recommended: true,
  },
  {
    id: "s2",
    startTime: "2026-03-13T14:00:00",
    endTime: "2026-03-13T15:00:00",
    score: 82,
    confidence: 80,
    rank: 2,
    reasoning: "One soft conflict. Sarah has a tentative hold that can be moved.",
    conflicts: [
      { type: "soft", description: "Sarah has a tentative team lunch", attendeeId: "u2", resolution: "Can be rescheduled" },
    ],
    attendeeAvailability: [
      { attendeeId: "u1", status: "available" },
      { attendeeId: "u2", status: "soft_conflict" },
      { attendeeId: "u3", status: "available" },
    ],
    requiresApproval: false,
    recommended: false,
  },
  {
    id: "s3",
    startTime: "2026-03-14T11:00:00",
    endTime: "2026-03-14T12:00:00",
    score: 74,
    confidence: 70,
    rank: 3,
    reasoning: "Next day availability. Optimized for external priority.",
    conflicts: [
      { type: "soft", description: "Marcus prefers mornings for deep work", attendeeId: "u3" },
    ],
    attendeeAvailability: [
      { attendeeId: "u1", status: "available" },
      { attendeeId: "u2", status: "available" },
      { attendeeId: "u3", status: "soft_conflict" },
    ],
    requiresApproval: false,
    recommended: false,
  },
  {
    id: "s4",
    startTime: "2026-03-14T16:00:00",
    endTime: "2026-03-14T17:00:00",
    score: 58,
    confidence: 55,
    rank: 4,
    reasoning: "Late afternoon slot. Requires approval from Priya due to timezone overlap.",
    conflicts: [
      { type: "hard", description: "Priya's working hours end at this time (IST)", attendeeId: "u4" },
    ],
    attendeeAvailability: [
      { attendeeId: "u1", status: "available" },
      { attendeeId: "u2", status: "available" },
      { attendeeId: "u4", status: "hard_conflict" },
    ],
    requiresApproval: true,
    recommended: false,
  },
];

export const mockAgentActivity: AgentActivity[] = [
  { id: "a1", agentType: "calendar", status: "complete", message: "Scanned 4 calendars across 3 timezones", timestamp: "2026-03-11T09:30:01", progress: 100 },
  { id: "a2", agentType: "behavior", status: "complete", message: "Analyzed 90 days of scheduling patterns", timestamp: "2026-03-11T09:30:03", progress: 100 },
  { id: "a3", agentType: "coordination", status: "analyzing", message: "Negotiating across 3 attendee preferences", timestamp: "2026-03-11T09:30:05", progress: 72 },
  { id: "a4", agentType: "orchestrator", status: "waiting", message: "Awaiting coordination results to rank slots", timestamp: "2026-03-11T09:30:06", progress: 0 },
];

export const mockPreferences: UserPreference[] = [
  { id: "p1", userId: "u1", category: "time", label: "Prefers Afternoons", description: "Scheduling meetings after 1 PM when possible", value: "afternoon", icon: "sun", active: true },
  { id: "p2", userId: "u1", category: "time", label: "No Fridays After 3 PM", description: "Avoid scheduling on Friday afternoons", value: "no_friday_pm", icon: "calendar-x", active: true },
  { id: "p3", userId: "u1", category: "priority", label: "Client Calls First", description: "Will move internal 1:1s for customer calls", value: "client_priority", icon: "arrow-up", active: true },
  { id: "p4", userId: "u1", category: "behavior", label: "No Back-to-Back", description: "Prefers 15-minute buffer between meetings", value: "buffer_15", icon: "clock", active: true },
  { id: "p5", userId: "u1", category: "escalation", label: "Low Confidence Escalation", description: "Escalate to human when AI confidence is below 60%", value: "escalate_low", icon: "alert-triangle", active: true },
  { id: "p6", userId: "u1", category: "behavior", label: "Deep Work Mornings", description: "Reserve mornings for focused work when possible", value: "deep_work_am", icon: "brain", active: false },
];

export const mockDecision: DecisionExplanation = {
  meetingId: "m2",
  requestSummary: "Schedule a 60-minute Client Strategy Review with James Kim (VP Sales). High priority, cross-timezone.",
  recommendedSlot: mockSlots[0],
  alternativeSlots: mockSlots.slice(1),
  tradeoffs: [
    "Morning slot may conflict with Alex's deep work preference",
    "Afternoon alternatives have lower attendee alignment",
    "Cross-timezone constraints limit available windows",
  ],
  overallConfidence: 92,
  approvalNeeded: false,
  agentInsights: [
    { agent: "calendar", insight: "Found 12 open windows across both calendars this week" },
    { agent: "behavior", insight: "James Kim historically accepts morning EST meetings 85% of the time" },
    { agent: "coordination", insight: "No hard conflicts detected. One soft conflict resolvable." },
    { agent: "orchestrator", insight: "Top recommendation scores 97/100 with 95% confidence" },
  ],
};

export const agentInfoList: AgentInfo[] = [
  {
    type: "calendar",
    name: "Calendar Agent",
    description: "Scans and analyzes calendar data across all attendees to identify available windows.",
    capabilities: ["Multi-calendar scanning", "Timezone normalization", "Recurring event detection", "Buffer time analysis"],
    icon: "calendar-search",
    color: "from-blue-500 to-cyan-500",
  },
  {
    type: "behavior",
    name: "Behavior Agent",
    description: "Learns scheduling patterns and preferences from historical data to optimize recommendations.",
    capabilities: ["Pattern recognition", "Preference learning", "Time-of-day optimization", "Meeting type analysis"],
    icon: "brain",
    color: "from-purple-500 to-pink-500",
  },
  {
    type: "coordination",
    name: "Coordination Agent",
    description: "Negotiates across attendees to resolve conflicts and find mutually optimal times.",
    capabilities: ["Conflict resolution", "Priority balancing", "Cross-timezone negotiation", "Soft conflict handling"],
    icon: "users",
    color: "from-amber-500 to-orange-500",
  },
  {
    type: "orchestrator",
    name: "Orchestrator",
    description: "Synthesizes all agent outputs into a ranked list of slot recommendations with explanations.",
    capabilities: ["Multi-signal ranking", "Confidence scoring", "Explainable decisions", "Human escalation"],
    icon: "cpu",
    color: "from-emerald-500 to-teal-500",
  },
];

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockApi: MockApiService = {
  getUpcomingMeetings: async (): Promise<Meeting[]> => {
    await delay(600);
    return mockMeetings;
  },
  getRecommendedSlots: async (_request: ScheduleRequest): Promise<TimeSlot[]> => {
    await delay(1200);
    return mockSlots;
  },
  getAgentActivity: async (): Promise<AgentActivity[]> => {
    await delay(800);
    return mockAgentActivity;
  },
  getUserPreferences: async (_userId: string): Promise<UserPreference[]> => {
    await delay(500);
    return mockPreferences;
  },
  getMeetingDecision: async (_meetingId: string): Promise<DecisionExplanation> => {
    await delay(1000);
    return mockDecision;
  },
};
