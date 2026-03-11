/**
 * API Client for Schedulo Backend
 * Handles all HTTP requests to FastAPI backend
 */

import type {
  Meeting,
  TimeSlot,
  AgentActivity,
  UserPreference,
  DecisionExplanation,
  ScheduleRequest,
} from "@/types/schedulo";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      credentials: "include",
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: response.statusText,
        }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Schedule endpoints
  async createScheduleRequest(request: ScheduleRequest): Promise<{
    request_id: string;
    status: string;
    recommended_slots: TimeSlot[];
    approval_needed: boolean;
    confidence: number;
    message: string;
  }> {
    return this.request("/schedule/request", {
      method: "POST",
      body: JSON.stringify({
        title: request.title,
        attendee_ids: request.attendees,
        duration: request.duration,
        priority: request.priority,
        meeting_type: request.type,
        notes: request.notes,
        preferred_time_range: request.preferredTimeRange,
      }),
    });
  }

  async getRecommendedSlots(
    attendeeIds: string[],
    duration: number,
    meetingType: string,
    priority: string
  ): Promise<TimeSlot[]> {
    const params = new URLSearchParams({
      attendee_ids: attendeeIds.join(","),
      duration: duration.toString(),
      meeting_type: meetingType,
      priority: priority,
    });

    return this.request(`/schedule/slots/recommendations?${params}`);
  }

  async confirmTimeSlot(slotId: string): Promise<{
    status: string;
    slot_id: string;
    message: string;
  }> {
    return this.request(`/schedule/slots/${slotId}/confirm`, {
      method: "POST",
    });
  }

  // Meeting endpoints
  async getUpcomingMeetings(
    userId: string,
    days: number = 7
  ): Promise<Meeting[]> {
    const params = new URLSearchParams({
      user_id: userId,
      days: days.toString(),
    });

    return this.request(`/meetings/upcoming?${params}`);
  }

  async getMeetingById(meetingId: string): Promise<Meeting> {
    return this.request(`/meetings/${meetingId}`);
  }

  async getMeetingDecision(
    meetingId: string
  ): Promise<DecisionExplanation> {
    return this.request(`/meetings/${meetingId}/decision`);
  }

  async updateMeetingStatus(
    meetingId: string,
    status: string
  ): Promise<{ meeting_id: string; status: string; updated: boolean }> {
    return this.request(`/meetings/${meetingId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  }

  async cancelMeeting(meetingId: string): Promise<{
    meeting_id: string;
    status: string;
    message: string;
  }> {
    return this.request(`/meetings/${meetingId}`, {
      method: "DELETE",
    });
  }

  // Preference endpoints
  async getUserPreferences(userId: string): Promise<UserPreference[]> {
    return this.request(`/preferences/${userId}`);
  }

  async updatePreference(
    preferenceId: string,
    data: { active?: boolean; value?: string }
  ): Promise<{ preference_id: string; updated: boolean }> {
    return this.request(`/preferences/${preferenceId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async createPreference(
    userId: string,
    category: string,
    label: string,
    value: string,
    description: string
  ): Promise<UserPreference> {
    return this.request(`/preferences/${userId}`, {
      method: "POST",
      body: JSON.stringify({ category, label, value, description }),
    });
  }

  // Agent endpoints
  async getAgentActivity(): Promise<AgentActivity[]> {
    return this.request("/agents/activity");
  }

  async getAgentInfo(): Promise<Array<{
    type: string;
    name: string;
    description: string;
    capabilities: string[];
    icon: string;
    color: string;
  }>> {
    return this.request("/agents/info");
  }

  // WebSocket for real-time agent updates
  connectAgentWebSocket(
    onMessage: (activity: AgentActivity) => void,
    onError?: (error: Event) => void
  ): WebSocket {
    const wsUrl = this.baseUrl.replace("http", "ws") + "/agents/ws/activity";
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const activity = JSON.parse(event.data);
        onMessage(activity);
      } catch (error) {
        console.error("WebSocket message parse error:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (onError) onError(error);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    // Send ping every 30 seconds to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      } else {
        clearInterval(pingInterval);
      }
    }, 30000);

    return ws;
  }

  // Health check
  async healthCheck(): Promise<{
    status: string;
    agents: Record<string, string>;
  }> {
    return this.request("/health");
  }
}

export const apiClient = new ApiClient();
export default apiClient;
