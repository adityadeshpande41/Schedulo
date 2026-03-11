/**
 * React Query hooks for agent operations
 */

import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { AgentActivity } from "@/types/schedulo";

export function useAgentActivity() {
  return useQuery({
    queryKey: ["agent-activity"],
    queryFn: () => apiClient.getAgentActivity(),
    refetchInterval: 3000, // Poll every 3 seconds
  });
}

export function useAgentInfo() {
  return useQuery({
    queryKey: ["agent-info"],
    queryFn: () => apiClient.getAgentInfo(),
    staleTime: Infinity, // Agent info doesn't change
  });
}

export function useAgentWebSocket() {
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = apiClient.connectAgentWebSocket(
      (activity) => {
        setActivities((prev) => [...prev, activity]);
      },
      (error) => {
        console.error("WebSocket error:", error);
        setIsConnected(false);
      }
    );

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  return { activities, isConnected };
}
