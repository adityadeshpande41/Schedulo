/**
 * React Query hooks for user preferences
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";

export function useUserPreferences(userId: string) {
  return useQuery({
    queryKey: ["preferences", userId],
    queryFn: () => apiClient.getUserPreferences(userId),
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useUpdatePreference() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      preferenceId,
      data,
    }: {
      preferenceId: string;
      data: { active?: boolean; value?: string };
    }) => apiClient.updatePreference(preferenceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["preferences"] });
    },
  });
}

export function useCreatePreference() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      category,
      label,
      value,
      description,
    }: {
      userId: string;
      category: string;
      label: string;
      value: string;
      description: string;
    }) => apiClient.createPreference(userId, category, label, value, description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["preferences"] });
    },
  });
}
