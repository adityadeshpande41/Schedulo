export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: string;
  timezone: string;
}

export interface Attendee {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: string;
  availability: "available" | "soft_conflict" | "hard_conflict" | "unknown";
  responseStatus: "accepted" | "declined" | "tentative" | "pending";
}

export interface Meeting {
  id: string;
  title: string;
  type: "team_sync" | "one_on_one" | "client_call" | "standup" | "workshop" | "interview";
  startTime: string;
  endTime: string;
  duration: number;
  attendees: Attendee[];
  status: "confirmed" | "pending" | "rescheduled" | "cancelled";
  priority: "high" | "medium" | "low";
  location?: string;
  description?: string;
}

export interface ScheduleRequest {
  title: string;
  attendees: string[];
  duration: number;
  priority: "high" | "medium" | "low";
  type: Meeting["type"];
  preferredTimeRange?: { start: string; end: string };
  notes?: string;
}

export interface TimeSlot {
  id: string;
  startTime: string;
  endTime: string;
  score: number;
  confidence: number;
  rank: number;
  reasoning: string;
  conflicts: SlotConflict[];
  attendeeAvailability: { attendeeId: string; status: Attendee["availability"] }[];
  requiresApproval: boolean;
  recommended: boolean;
}

export interface SlotConflict {
  type: "soft" | "hard";
  description: string;
  attendeeId?: string;
  resolution?: string;
}

export type AgentType = "calendar" | "behavior" | "coordination" | "orchestrator";

export type AgentStatus = "idle" | "scanning" | "analyzing" | "negotiating" | "ranking" | "complete" | "waiting";

export interface AgentActivity {
  id: string;
  agentType: AgentType;
  status: AgentStatus;
  message: string;
  timestamp: string;
  details?: string;
  progress?: number;
}

export interface UserPreference {
  id: string;
  userId: string;
  category: "time" | "behavior" | "priority" | "escalation";
  label: string;
  description: string;
  value: string;
  icon: string;
  active: boolean;
}

export interface DecisionExplanation {
  meetingId: string;
  requestSummary: string;
  recommendedSlot: TimeSlot;
  alternativeSlots: TimeSlot[];
  tradeoffs: string[];
  overallConfidence: number;
  approvalNeeded: boolean;
  approvalReason?: string;
  agentInsights: { agent: AgentType; insight: string }[];
}

export interface AgentInfo {
  type: AgentType;
  name: string;
  description: string;
  capabilities: string[];
  icon: string;
  color: string;
}

export interface MockApiService {
  getUpcomingMeetings: () => Promise<Meeting[]>;
  getRecommendedSlots: (request: ScheduleRequest) => Promise<TimeSlot[]>;
  getAgentActivity: () => Promise<AgentActivity[]>;
  getUserPreferences: (userId: string) => Promise<UserPreference[]>;
  getMeetingDecision: (meetingId: string) => Promise<DecisionExplanation>;
}
