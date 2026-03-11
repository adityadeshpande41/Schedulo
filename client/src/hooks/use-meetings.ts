/**
 * React Query hooks for meeting operations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

export function useUpcomingMeetings(userId: string, days: number = 7) {
  return useQuery({
    queryKey: ["meetings", "upcoming", userId, days],
    queryFn: () => apiClient.getUpcomingMeetings(userId, days),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useMeeting(meetingId: string) {
  return useQuery({
    queryKey: ["meetings", meetingId],
    queryFn: () => apiClient.getMeetingById(meetingId),
    enabled: !!meetingId,
  });
}

export function useMeetingDecision(meetingId: string) {
  return useQuery({
    queryKey: ["meetings", meetingId, "decision"],
    queryFn: () => apiClient.getMeetingDecision(meetingId),
    enabled: !!meetingId,
  });
}

export function useUpdateMeetingStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ meetingId, status }: { meetingId: string; status: string }) =>
      apiClient.updateMeetingStatus(meetingId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
    },
  });
}

export function useCancelMeeting() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (meetingId: string) => apiClient.cancelMeeting(meetingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
    },
  });
}
