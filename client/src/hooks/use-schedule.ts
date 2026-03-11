/**
 * React Query hooks for scheduling operations
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import type { ScheduleRequest, TimeSlot } from "@/types/schedulo";

export function useCreateScheduleRequest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ScheduleRequest) =>
      apiClient.createScheduleRequest(request),
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      queryClient.invalidateQueries({ queryKey: ["agent-activity"] });
    },
  });
}

export function useRecommendedSlots(
  attendeeIds: string[],
  duration: number,
  meetingType: string,
  priority: string,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: ["recommended-slots", attendeeIds, duration, meetingType, priority],
    queryFn: () =>
      apiClient.getRecommendedSlots(attendeeIds, duration, meetingType, priority),
    enabled: enabled && attendeeIds.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useConfirmTimeSlot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (slotId: string) => apiClient.confirmTimeSlot(slotId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
    },
  });
}
